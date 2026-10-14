package dev.arkhaven.core.rift;

import dev.arkhaven.core.ArkhavenCore;
import dev.arkhaven.core.ModRegistry;
import dev.arkhaven.core.ward.WardManager;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Holder;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.TagKey;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/**
 * A rift: a shimmering tear that releases waves of mobs from #arkhaven:rift_spawns for a few minutes, then closes
 * and drops rift shards. Its mobs are leashed to it (pulled back past 32 blocks) and vanish when it closes.
 */
public class RiftEntity extends Entity {
    public static final TagKey<EntityType<?>> SPAWNS = TagKey.create(Registries.ENTITY_TYPE, ArkhavenCore.pack("rift_spawns"));
    private static final String MOB_TAG = "arkhaven_rift_mob";
    private int lifetime = 20 * 60 * 4;
    private int waves = 4;
    private final List<UUID> spawned = new ArrayList<>();

    public RiftEntity(EntityType<? extends RiftEntity> type, Level level) {
        super(type, level);
        noPhysics = true;
    }

    public static RiftEntity open(ServerLevel level, BlockPos near, int waves, int minutes) {
        BlockPos ground = level.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, near);
        RiftEntity r = new RiftEntity(ModRegistry.RIFT.get(), level);
        r.setPos(Vec3.atBottomCenterOf(ground).add(0, 1.0, 0));
        r.waves = waves;
        r.lifetime = minutes * 60 * 20;
        level.addFreshEntity(r);
        level.playSound(null, ground, SoundEvents.END_PORTAL_SPAWN, SoundSource.HOSTILE, 3.0f, 0.7f);
        return r;
    }

    @Override
    protected void defineSynchedData(net.minecraft.network.syncher.SynchedEntityData.Builder builder) {}

    @Override
    public void tick() {
        super.tick();
        Level level = level();
        if (level.isClientSide) {
            for (int i = 0; i < 8; i++) {
                double a = random.nextDouble() * Math.PI * 2;
                level.addParticle(i % 2 == 0 ? ParticleTypes.PORTAL : ParticleTypes.REVERSE_PORTAL,
                        getX() + Math.cos(a) * 0.6, getY() + random.nextDouble() * 3, getZ() + Math.sin(a) * 0.6, 0, 0.02, 0);
            }
            return;
        }
        ServerLevel sl = (ServerLevel) level;
        if (WardManager.isProtected(sl, position(), 2)) { close(sl, false); return; }
        int waveEvery = Math.max(20 * 20, lifetime / Math.max(1, waves));
        if (tickCount % waveEvery == 1 && spawned.size() < waves * 4) spawnWave(sl);
        if (tickCount % 20 == 0) leash(sl);
        if (tickCount >= lifetime || (sl.isDay() && tickCount > 20 * 30)) close(sl, true);
    }

    private void spawnWave(ServerLevel level) {
        List<Holder<EntityType<?>>> pool = new ArrayList<>();
        BuiltInRegistries.ENTITY_TYPE.getTagOrEmpty(SPAWNS).forEach(pool::add);
        if (pool.isEmpty()) return;
        int count = 2 + random.nextInt(3);
        for (int i = 0; i < count; i++) {
            EntityType<?> type = pool.get(random.nextInt(pool.size())).value();
            BlockPos p = level.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,
                    blockPosition().offset(random.nextInt(9) - 4, 0, random.nextInt(9) - 4));
            Entity e = type.spawn(level, p, MobSpawnType.EVENT);
            if (e instanceof Mob mob) {
                mob.addTag(MOB_TAG);
                spawned.add(mob.getUUID());
            }
        }
        level.sendParticles(ParticleTypes.REVERSE_PORTAL, getX(), getY() + 1.5, getZ(), 80, 1.5, 1.5, 1.5, 0.2);
    }

    private void leash(ServerLevel level) {
        for (UUID id : spawned) {
            Entity e = level.getEntity(id);
            if (e != null && e.isAlive() && e.distanceToSqr(this) > 32 * 32) {
                e.teleportTo(getX() + random.nextInt(5) - 2, getY(), getZ() + random.nextInt(5) - 2);
            }
        }
    }

    private void close(ServerLevel level, boolean reward) {
        for (UUID id : spawned) {
            Entity e = level.getEntity(id);
            if (e != null && e.isAlive()) e.discard();
        }
        // Also clean up any strays from a rift that was unloaded mid-event.
        for (Mob m : level.getEntitiesOfClass(Mob.class, new AABB(blockPosition()).inflate(48), m -> m.getTags().contains(MOB_TAG))) m.discard();
        if (reward) {
            Item shard = BuiltInRegistries.ITEM.get(ArkhavenCore.pack("rift_shard"));
            if (shard != Items.AIR) level.addFreshEntity(new ItemEntity(level, getX(), getY() + 0.5, getZ(), new ItemStack(shard, 1 + random.nextInt(waves))));
        }
        level.sendParticles(ParticleTypes.FLASH, getX(), getY() + 1.5, getZ(), 1, 0, 0, 0, 0);
        level.playSound(null, blockPosition(), SoundEvents.BEACON_DEACTIVATE, SoundSource.HOSTILE, 3.0f, 0.6f);
        discard();
    }

    @Override
    protected void readAdditionalSaveData(CompoundTag tag) {
        lifetime = tag.getInt("Lifetime");
        waves = tag.getInt("Waves");
    }

    @Override
    protected void addAdditionalSaveData(CompoundTag tag) {
        tag.putInt("Lifetime", lifetime);
        tag.putInt("Waves", waves);
    }

    @Override
    public boolean isPickable() {
        return false;
    }
}
