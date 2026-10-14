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
 * - first login and every respawn without a bed/anchor put the player on that spot in the overworld.
 */
public final class LandSpawn {
    private static final String FIRST_JOIN_TAG = "arkhaven_landed";

    @SubscribeEvent
    public static void onServerStarted(ServerStartedEvent event) {
        ServerLevel ow = event.getServer().overworld();
        BlockPos spawn = ow.getSharedSpawnPos();
        if (isDryLand(ow, spawn)) return;
        BlockPos land = findLand(ow, spawn, 1024);
        if (land != null) {
            ow.setDefaultSpawnPos(land, 0f);
            ArkhavenCore.LOG.info("World spawn {} was in water; moved to dry land at {}", spawn, land);
        } else {
            ArkhavenCore.LOG.warn("No dry land found within 1024 blocks of spawn {}", spawn);
        }
    }

    @SubscribeEvent
    public static void onLogin(PlayerEvent.PlayerLoggedInEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer p)) return;
        if (p.getTags().contains(FIRST_JOIN_TAG)) return;
        p.addTag(FIRST_JOIN_TAG);
        toSpawn(p);
    }

    @SubscribeEvent
    public static void onRespawn(PlayerEvent.PlayerRespawnEvent event) {
        if (event.isEndConquered() || !(event.getEntity() instanceof ServerPlayer p)) return;
        if (p.getRespawnPosition() != null) return; // has a bed / anchor: vanilla handles it
        toSpawn(p);
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
        var biome = level.getBiome(top);
        return !biome.is(BiomeTags.IS_OCEAN) && !biome.is(BiomeTags.IS_RIVER);
    }

    /** Spiral search on a 16-block grid for the nearest dry surface. */
    static BlockPos findLand(ServerLevel level, BlockPos center, int radius) {
        for (int r = 16; r <= radius; r += 16) {
            for (int dx = -r; dx <= r; dx += 16) {
                for (int dz = -r; dz <= r; dz += 16) {
                    if (Math.abs(dx) != r && Math.abs(dz) != r) continue; // ring only
                    BlockPos p = center.offset(dx, 0, dz);
                    if (isDryLand(level, p)) return level.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, p);
                }
            }
        }
        return null;
    }

    private LandSpawn() {}
}
