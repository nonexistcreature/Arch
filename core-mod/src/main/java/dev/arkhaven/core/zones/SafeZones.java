package dev.arkhaven.core.zones;

import dev.arkhaven.core.ArkhavenCore;
import dev.arkhaven.core.Config;
import net.minecraft.core.BlockPos;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.level.Level;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.neoforge.event.entity.living.FinalizeSpawnEvent;

import java.lang.reflect.Method;

/**
 * Zone 0 (docs/10_RPG_DANGER.md §6): no natural hostile spawns in the Haven, in Open Parties and Claims claims (+margin)
 * and around hearth stones. Event mobs (rifts, MobSpawnType.EVENT) are not filtered, but rifts never open in zone 0.
 * OPAC is a soft dependency accessed by reflection, so the mod works without it.
 */
public final class SafeZones {
    private static boolean opacTried;
    private static Method opacGet, opacClaimsManager, opacClaimAt;

    @SubscribeEvent
    public static void onFinalizeSpawn(FinalizeSpawnEvent event) {
        MobSpawnType type = event.getSpawnType();
        if (type != MobSpawnType.NATURAL && type != MobSpawnType.CHUNK_GENERATION && type != MobSpawnType.PATROL) return;
        if (event.getEntity().getType().getCategory() != MobCategory.MONSTER) return;
        if (!(event.getLevel().getLevel() instanceof ServerLevel level)) return;
        if (isSafe(level, BlockPos.containing(event.getX(), event.getY(), event.getZ()))) event.setSpawnCancelled(true);
    }

    /** Zone 0 test. */
    public static boolean isSafe(ServerLevel level, BlockPos pos) {
        if (level.dimension() == Level.OVERWORLD) {
            BlockPos spawn = level.getSharedSpawnPos();
            int r = Config.HAVEN_RADIUS.get();
            if (horizontalDistSqr(pos, spawn) <= (long) r * r) return true;
        }
        if (HearthStones.get(level.getServer()).isNearHearth(level, pos, Config.HEARTH_RADIUS.get())) return true;
        return isClaimedNear(level, pos, Config.CLAIM_MARGIN.get());
    }

    public static boolean isClaimed(ServerLevel level, BlockPos pos) {
        return claimAt(level, pos.getX() >> 4, pos.getZ() >> 4);
    }

    /** True if any chunk within `margin` blocks of pos is claimed. */
    public static boolean isClaimedNear(ServerLevel level, BlockPos pos, int margin) {
        int cr = (margin + 15) >> 4;
        int cx = pos.getX() >> 4, cz = pos.getZ() >> 4;
        for (int dx = -cr; dx <= cr; dx++) for (int dz = -cr; dz <= cr; dz++) {
            if (claimAt(level, cx + dx, cz + dz)) return true;
        }
        return false;
    }

    private static boolean claimAt(ServerLevel level, int chunkX, int chunkZ) {
        if (!opacTried) initOpac();
        if (opacClaimAt == null) return false;
        try {
            Object api = opacGet.invoke(null, level.getServer());
            Object mgr = opacClaimsManager.invoke(api);
            return opacClaimAt.invoke(mgr, level.dimension().location(), chunkX, chunkZ) != null;
        } catch (ReflectiveOperationException | RuntimeException e) {
            return false;
        }
    }

    private static synchronized void initOpac() {
        if (opacTried) return;
        opacTried = true;
        try {
            Class<?> api = Class.forName("xaero.pac.common.server.api.OpenPACServerAPI");
            opacGet = api.getMethod("get", MinecraftServer.class);
            opacClaimsManager = api.getMethod("getServerClaimsManager");
            Class<?> mgr = opacClaimsManager.getReturnType();
            opacClaimAt = mgr.getMethod("get", net.minecraft.resources.ResourceLocation.class, int.class, int.class);
            ArkhavenCore.LOG.info("Open Parties and Claims found: claims are safe zones");
        } catch (ReflectiveOperationException | RuntimeException | LinkageError e) {
            opacClaimAt = null;
            ArkhavenCore.LOG.info("Open Parties and Claims API not available ({}); using hearth stones and the Haven only", e.toString());
        }
    }

    public static boolean opacAvailable() {
        if (!opacTried) initOpac();
        return opacClaimAt != null;
    }

    public static long horizontalDistSqr(BlockPos a, BlockPos b) {
        long dx = a.getX() - b.getX(), dz = a.getZ() - b.getZ();
        return dx * dx + dz * dz;
    }

    private SafeZones() {}
}
