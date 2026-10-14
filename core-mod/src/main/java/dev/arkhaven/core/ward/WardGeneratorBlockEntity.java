package dev.arkhaven.core.ward;

import dev.arkhaven.core.Config;
import dev.arkhaven.core.ModRegistry;
import dev.arkhaven.core.director.EventDirector;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;

public class WardGeneratorBlockEntity extends BlockEntity {
    public static final int MAX_CRYSTALS = 16;
    /** Remaining protection, in ticks. */
    private long fuelTicks;

    public WardGeneratorBlockEntity(BlockPos pos, BlockState state) {
        super(ModRegistry.WARD_BE.get(), pos, state);
    }

    public int tier() {
        return getBlockState().getBlock() instanceof WardGeneratorBlock b ? b.tier() : 1;
    }

    public int radius() {
        return Config.wardRadius(tier());
    }

    private static long ticksPerCrystal() {
        return Config.WARD_MINUTES_PER_CRYSTAL.get() * 60L * 20L;
    }

    public int fuelCrystals() {
        return (int) Math.ceil(fuelTicks / (double) ticksPerCrystal());
    }

    public boolean addFuel() {
        if (fuelTicks + ticksPerCrystal() > MAX_CRYSTALS * ticksPerCrystal()) return false;
        fuelTicks += ticksPerCrystal();
        setChanged();
        return true;
    }

    /** Debug/test helper: fill with fuel without items. */
    public void setFuelCrystals(int crystals) {
        fuelTicks = crystals * ticksPerCrystal();
        setChanged();
    }

    public boolean isActive() {
        return fuelTicks > 0 && level != null && !level.hasNeighborSignal(worldPosition);
    }

    public Component statusLine() {
        long minutes = fuelTicks / 20 / 60;
        return Component.translatable("message.arkhaven_core.ward.status", tier(), radius(), minutes,
                        Component.translatable(isActive() ? "message.arkhaven_core.ward.on" : "message.arkhaven_core.ward.off"))
                .withStyle(isActive() ? ChatFormatting.AQUA : ChatFormatting.GRAY);
    }

    public static void serverTick(Level level, BlockPos pos, BlockState state, WardGeneratorBlockEntity be) {
        ServerLevel sl = (ServerLevel) level;
        boolean active = be.isActive();
        if (active) WardManager.put(sl, pos, be.radius(), be.tier());
        else WardManager.remove(sl, pos);
        if (state.getValue(WardGeneratorBlock.ACTIVE) != active) {
            level.setBlock(pos, state.setValue(WardGeneratorBlock.ACTIVE, active), 3);
        }
        if (!active) return;
        // Fuel only burns while someone is around to be protected, or an event is running.
        boolean someoneNear = sl.getNearestPlayer(pos.getX() + 0.5, pos.getY() + 0.5, pos.getZ() + 0.5, be.radius() + 64, false) != null;
        if (someoneNear || EventDirector.isEventRunning(sl.getServer())) {
            be.fuelTicks--;
            if (be.fuelTicks % 200 == 0) be.setChanged();
        }
        // Dome hint: a few particles on the boundary every second.
        if (level.getGameTime() % 20 == 0) {
            int r = be.radius();
            for (int i = 0; i < 6; i++) {
                double a = level.random.nextDouble() * Math.PI * 2, b = level.random.nextDouble() * Math.PI / 2;
                double x = pos.getX() + 0.5 + Math.cos(a) * Math.cos(b) * r;
                double y = pos.getY() + 0.5 + Math.sin(b) * r;
                double z = pos.getZ() + 0.5 + Math.sin(a) * Math.cos(b) * r;
                sl.sendParticles(ParticleTypes.END_ROD, x, y, z, 1, 0, 0, 0, 0);
            }
        }
    }

    @Override
    protected void saveAdditional(CompoundTag tag, HolderLookup.Provider registries) {
        super.saveAdditional(tag, registries);
        tag.putLong("FuelTicks", fuelTicks);
    }

    @Override
    protected void loadAdditional(CompoundTag tag, HolderLookup.Provider registries) {
        super.loadAdditional(tag, registries);
        fuelTicks = tag.getLong("FuelTicks");
    }
}
