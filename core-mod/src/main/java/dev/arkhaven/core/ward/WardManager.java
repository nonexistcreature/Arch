package dev.arkhaven.core.ward;

import dev.arkhaven.core.Config;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.entity.monster.Creeper;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.neoforge.event.level.ExplosionEvent;
import net.neoforged.neoforge.event.level.LevelEvent;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Index of active wards per dimension, refreshed by each generator's tick.
 * Also the explosion filter: blocks inside an active ward never break; creeper explosions never break blocks.
 */
public final class WardManager {
    public record Ward(BlockPos pos, int radius, int tier) {
        public boolean covers(Vec3 p) {
            return p.distanceToSqr(Vec3.atCenterOf(pos)) <= (double) radius * radius;
        }
    }

    private static final Map<ResourceKey<Level>, Map<BlockPos, Ward>> WARDS = new ConcurrentHashMap<>();

    public static void put(Level level, BlockPos pos, int radius, int tier) {
        WARDS.computeIfAbsent(level.dimension(), k -> new ConcurrentHashMap<>()).put(pos.immutable(), new Ward(pos.immutable(), radius, tier));
    }

    public static void remove(Level level, BlockPos pos) {
        Map<BlockPos, Ward> m = WARDS.get(level.dimension());
        if (m != null) m.remove(pos);
    }

    /** The strongest active ward covering a point, or null. */
    public static Ward covering(Level level, Vec3 p) {
        Map<BlockPos, Ward> m = WARDS.get(level.dimension());
        if (m == null) return null;
        Ward best = null;
        for (Ward w : m.values()) if (w.covers(p) && (best == null || w.tier > best.tier)) best = w;
        return best;
    }

    public static boolean isProtected(Level level, Vec3 p) {
        return covering(level, p) != null;
    }

    public static boolean isProtected(Level level, Vec3 p, int minTier) {
        Ward w = covering(level, p);
        return w != null && w.tier >= minTier;
    }

    @SubscribeEvent
    public static void onDetonate(ExplosionEvent.Detonate event) {
        Level level = event.getLevel();
        if (Config.CREEPERS_KEEP_BLOCKS.get() && event.getExplosion().getDirectSourceEntity() instanceof Creeper) {
            event.getAffectedBlocks().clear();
            return;
        }
        Map<BlockPos, Ward> m = WARDS.get(level.dimension());
        if (m == null || m.isEmpty()) return;
        event.getAffectedBlocks().removeIf(bp -> isProtected(level, Vec3.atCenterOf(bp)));
    }

    @SubscribeEvent
    public static void onUnload(LevelEvent.Unload event) {
        if (event.getLevel() instanceof Level l) WARDS.remove(l.dimension());
    }

    private WardManager() {}
}
