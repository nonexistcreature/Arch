package dev.arkhaven.core.meteor;

import dev.arkhaven.core.ArkhavenCore;
import dev.arkhaven.core.ModRegistry;
import dev.arkhaven.core.ward.WardManager;
import dev.arkhaven.core.zones.SafeZones;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.FluidTags;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MoverType;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

/**
 * A falling meteor. Flies on a straight steep line with a fire trail. On impact: explosion + small crater lined with
 * meteorite ore. Burns up harmlessly above an active ward (loot drops just outside the ward).
 * size: 1 = shower pebble, 2 = normal, 3 = big strike. harmless = tutorial / showers / calm-intensity safety.
 */
public class MeteorEntity extends Entity {
    private static final EntityDataAccessor<Integer> SIZE = SynchedEntityData.defineId(MeteorEntity.class, EntityDataSerializers.INT);
    private boolean harmless;
    /** If > 0 the meteor burns up at this altitude (visual-only shower meteors). */
    private int burnUpAt = -1;

    public MeteorEntity(EntityType<? extends MeteorEntity> type, Level level) {
        super(type, level);
        noPhysics = false;
    }

    public static MeteorEntity spawn(ServerLevel level, Vec3 target, int size, boolean harmless, int burnUpAt) {
        MeteorEntity m = new MeteorEntity(ModRegistry.METEOR.get(), level);
        double angle = level.random.nextDouble() * Math.PI * 2;
        double height = 180 + level.random.nextInt(60);
        double startY = Math.max(target.y + 120, Math.min(level.getMaxBuildHeight() - 4, target.y + height));
        double horiz = (startY - target.y) * 0.6;
        Vec3 start = new Vec3(target.x + Math.cos(angle) * horiz, startY, target.z + Math.sin(angle) * horiz);
        m.setPos(start);
        m.setDeltaMovement(target.subtract(start).normalize().scale(1.6));
        m.entityData.set(SIZE, size);
        m.harmless = harmless;
        m.burnUpAt = burnUpAt;
        level.addFreshEntity(m);
        return m;
    }

    public int size() {
        return entityData.get(SIZE);
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder builder) {
        builder.define(SIZE, 2);
    }

    @Override
    public void tick() {
        super.tick();
        Level level = level();
        if (level.isClientSide) {
            for (int i = 0; i < 3 + size() * 2; i++) {
                level.addParticle(i % 3 == 0 ? ParticleTypes.LARGE_SMOKE : ParticleTypes.FLAME,
                        getX() + (random.nextDouble() - 0.5) * size(), getY() + (random.nextDouble() - 0.5) * size(),
                        getZ() + (random.nextDouble() - 0.5) * size(), 0, 0.05, 0);
            }
            return;
        }
        ServerLevel sl = (ServerLevel) level;
        if (tickCount > 20 * 30) { discard(); return; }
        if (burnUpAt > 0 && getY() <= burnUpAt) { burnUp(sl, false); return; }
        // Wards burn meteors in the sky above them.
        if (getY() < level.getMaxBuildHeight() && WardManager.isProtected(sl, position())) { burnUp(sl, true); return; }
        Vec3 before = position();
        move(MoverType.SELF, getDeltaMovement());
        if (horizontalCollision || verticalCollision || onGround() || isInWater() || isInLava() || position().distanceToSqr(before) < 0.01) {
            impact(sl);
        }
    }

    private void burnUp(ServerLevel level, boolean overWard) {
        level.sendParticles(ParticleTypes.FLASH, getX(), getY(), getZ(), 1, 0, 0, 0, 0);
        level.sendParticles(ParticleTypes.LAVA, getX(), getY(), getZ(), 20, 1, 1, 1, 0.1);
        level.playSound(null, blockPosition(), SoundEvents.FIREWORK_ROCKET_BLAST_FAR, SoundSource.AMBIENT, 4.0f, 0.6f);
        if (overWard) {
            // Drop a little loot just outside the ward that stopped it.
            WardManager.Ward w = WardManager.covering(level, position());
            if (w != null) {
                Vec3 c = Vec3.atCenterOf(w.pos());
                Vec3 dir = new Vec3(getX() - c.x, 0, getZ() - c.z);
                if (dir.lengthSqr() < 1) dir = new Vec3(1, 0, 0);
                Vec3 out = c.add(dir.normalize().scale(w.radius() + 4));
                BlockPos ground = level.getHeightmapPos(net.minecraft.world.level.levelgen.Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, BlockPos.containing(out));
                dropLoot(level, Vec3.atCenterOf(ground.above()), size());
            }
        }
        discard();
    }

    private void impact(ServerLevel level) {
        BlockPos center = blockPosition();
        boolean inWater = level.getFluidState(center).is(FluidTags.WATER) || level.getFluidState(center.below()).is(FluidTags.WATER);
        boolean safe = harmless || SafeZones.isClaimed(level, center) && dev.arkhaven.core.Config.INTENSITY.get() <= 1;
        float power = switch (size()) { case 1 -> 1.5f; case 3 -> 5.5f; default -> 3.5f; };
        level.explode(this, getX(), getY(), getZ(), power, !safe && size() >= 2, safe ? Level.ExplosionInteraction.NONE : Level.ExplosionInteraction.TNT);
        if (!safe || harmless) buildCrater(level, center, size(), safe);
        dropLoot(level, position().add(0, 1, 0), size());
        if (inWater) {
            Item carp = BuiltInRegistries.ITEM.get(ArkhavenCore.pack("star_carp"));
            if (carp != net.minecraft.world.item.Items.AIR) level.addFreshEntity(new ItemEntity(level, getX(), getY() + 1, getZ(), new ItemStack(carp, 1 + random.nextInt(2))));
        }
        level.playSound(null, center, SoundEvents.GENERIC_EXPLODE.value(), SoundSource.AMBIENT, 6.0f, 0.5f);
        ArkhavenCore.LOG.info("Meteor (size {}, harmless={}) impact at {}", size(), safe, center);
        discard();
    }

    /** Lines the crater (or, when harmless, just the impact spot) with meteorite ore and a little magma. */
    private void buildCrater(ServerLevel level, BlockPos c, int size, boolean gentle) {
        int r = gentle ? 1 : size + 1;
        BlockState ore = ModRegistry.METEORITE_ORE.get().defaultBlockState();
        for (int dx = -r; dx <= r; dx++) for (int dz = -r; dz <= r; dz++) for (int dy = -r; dy <= 1; dy++) {
            BlockPos p = c.offset(dx, dy, dz);
            if (dx * dx + dy * dy + dz * dz > r * r + 1) continue;
            if (WardManager.isProtected(level, Vec3.atCenterOf(p))) continue;
            BlockState s = level.getBlockState(p);
            if (s.isAir() || s.canBeReplaced() || s.getDestroySpeed(level, p) < 0) continue;
            float roll = random.nextFloat();
            if (roll < 0.35f) level.setBlockAndUpdate(p, ore);
            else if (!gentle && roll < 0.45f) level.setBlockAndUpdate(p, Blocks.MAGMA_BLOCK.defaultBlockState());
        }
        if (gentle) level.setBlockAndUpdate(c, ore);
    }

    private static void dropLoot(ServerLevel level, Vec3 at, int size) {
        Item dust = BuiltInRegistries.ITEM.get(ArkhavenCore.pack("meteoric_dust"));
        if (dust == net.minecraft.world.item.Items.AIR) return;
        level.addFreshEntity(new ItemEntity(level, at.x, at.y, at.z, new ItemStack(dust, size * 2 + level.random.nextInt(3))));
    }

    @Override
    protected void readAdditionalSaveData(CompoundTag tag) {
        entityData.set(SIZE, tag.getInt("Size"));
        harmless = tag.getBoolean("Harmless");
        burnUpAt = tag.getInt("BurnUpAt");
    }

    @Override
    protected void addAdditionalSaveData(CompoundTag tag) {
        tag.putInt("Size", size());
        tag.putBoolean("Harmless", harmless);
        tag.putInt("BurnUpAt", burnUpAt);
    }

    @Override
    public boolean isOnFire() {
        return true;
    }

    @Override
    public boolean shouldRenderAtSqrDistance(double d) {
        return d < 512 * 512;
    }
}
