package dev.arkhaven.core.zones;

import dev.arkhaven.core.ArkhavenCore;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.BiomeTags;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Heightmap;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.neoforge.event.server.ServerStartedEvent;

/**
 * Everyone starts on dry land, whatever their origin or class (owner's rule):
 * - on server start the world spawn is moved out of water onto the nearest dry, non-ocean surface;
 * - first login and respawn without a bed/anchor: a player already standing on dry land is left alone
 *   (vanilla's spot, or wherever NeoOrigins put them); only a player in water / over nothing solid is moved,
 *   to the nearest dry land around THEM. Earlier versions always snapped to the world spawn and searched rings
 *   from it, moving players up to 256 blocks away from a perfectly fine spot (snow, slabs, leaves failed the check).
 */
public final class LandSpawn {
    private static final String FIRST_JOIN_TAG = "arkhaven_landed";

    @SubscribeEvent
    public static void onServerStarted(ServerStartedEvent event) {
        ServerLevel ow = event.getServer().overworld();
        BlockPos spawn = ow.getSharedSpawnPos();
        if (isDryLand(ow, spawn)) {
            // Spawn can be recorded at bedrock level when chunks weren't generated yet: put it on the surface.
            BlockPos top = ow.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, spawn);
            if (top.getY() != spawn.getY()) {
                ow.setDefaultSpawnPos(top, 0f);
                ArkhavenCore.LOG.info("World spawn moved to the surface: {} -> {}", spawn, top);
            }
            return;
        }
        BlockPos land = findLand(ow, spawn, 2048);
        if (land != null) {
            ow.setDefaultSpawnPos(land, 0f);
            ArkhavenCore.LOG.info("World spawn {} was in water; moved to dry land at {}", spawn, land);
        } else {
            ArkhavenCore.LOG.warn("No dry land found within 2048 blocks of spawn {}", spawn);
        }
    }

    @SubscribeEvent
    public static void onLogin(PlayerEvent.PlayerLoggedInEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer p)) return;
        if (p.getTags().contains(FIRST_JOIN_TAG)) return;
        p.addTag(FIRST_JOIN_TAG);
        rescueIfWet(p);
    }

    @SubscribeEvent
    public static void onRespawn(PlayerEvent.PlayerRespawnEvent event) {
        if (event.isEndConquered() || !(event.getEntity() instanceof ServerPlayer p)) return;
        if (p.getRespawnPosition() != null) return; // has a bed / anchor: vanilla handles it
        rescueIfWet(p);
    }

    /** Leave the player where they are unless they stand in water / over nothing solid; then the nearest land around them. */
    static void rescueIfWet(ServerPlayer p) {
        ServerLevel level = p.serverLevel();
        BlockPos at = p.blockPosition();
        if (isSafeStanding(level, at)) return;
        BlockPos land = findLand(level, at, 256);
        if (land == null) {
            if (level == p.server.overworld()) toSpawn(p);
            return;
        }
        ArkhavenCore.LOG.info("{} appeared in water/unsafe at {}; moved to dry land at {}", p.getGameProfile().getName(), at, land);
        p.teleportTo(level, land.getX() + 0.5, land.getY(), land.getZ() + 0.5, p.getYRot(), p.getXRot());
        p.setAirSupply(p.getMaxAirSupply());
    }

    /** Lenient check of the exact spot: no fluid at feet/head, and something with collision within 3 blocks below. */
    public static boolean isSafeStanding(ServerLevel level, BlockPos feet) {
        if (!level.getFluidState(feet).isEmpty() || !level.getFluidState(feet.above()).isEmpty()) return false;
        for (int dy = 1; dy <= 3; dy++) { // right after placement the player may hover a block or two above ground
            BlockPos below = feet.below(dy);
            if (!level.getFluidState(below).isEmpty()) return false;
            if (!level.getBlockState(below).getCollisionShape(level, below).isEmpty()) return true;
        }
        return false;
    }

    public static void toSpawn(ServerPlayer p) {
        ServerLevel ow = p.server.overworld();
        BlockPos s = ow.getSharedSpawnPos();
        BlockPos top = ow.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, s);
        if (!isDryLand(ow, top)) {
            BlockPos land = findLand(ow, s, 256);
            if (land != null) top = land;
        }
        p.teleportTo(ow, top.getX() + 0.5, top.getY(), top.getZ() + 0.5, p.getYRot(), p.getXRot());
        p.setAirSupply(p.getMaxAirSupply());
    }

    static boolean isDryLand(ServerLevel level, BlockPos pos) {
        BlockPos top = level.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, pos);
        BlockState ground = level.getBlockState(top.below());
        if (!level.getFluidState(top).isEmpty() || !level.getFluidState(top.below()).isEmpty()) return false;
        if (ground.is(BlockTags.LEAVES) || !ground.isSolid()) return false;
        return top.getY() >= level.getSeaLevel(); // solid, dry, not an underwater pocket
    }

    /**
     * Ring search for the nearest land. Candidates are pre-filtered with the biome source (no chunk generation),
     * and only promising spots load a chunk for the real surface check — at most 12 chunk loads in total.
     */
    static BlockPos findLand(ServerLevel level, BlockPos center, int radius) {
        int loads = 0;
        for (int r = 32; r <= radius; r += 32) {
            for (int dx = -r; dx <= r; dx += 32) {
                for (int dz = -r; dz <= r; dz += 32) {
                    if (Math.abs(dx) != r && Math.abs(dz) != r) continue; // ring only
                    BlockPos p = center.offset(dx, 0, dz);
                    var biome = level.getUncachedNoiseBiome(p.getX() >> 2, 63 >> 2, p.getZ() >> 2);
                    if (biome.is(BiomeTags.IS_OCEAN) || biome.is(BiomeTags.IS_DEEP_OCEAN)) continue;
                    if (++loads > 48) return null;
                    BlockPos top = level.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, p);
                    if (isDryLand(level, p)) return top;
                }
            }
        }
        return null;
    }

    private LandSpawn() {}
}
