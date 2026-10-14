package dev.arkhaven.core.zones;

import dev.arkhaven.core.Config;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;

import java.util.Map;
import java.util.UUID;
import java.util.WeakHashMap;
import java.util.concurrent.ConcurrentHashMap;

/** Actionbar hint when a player crosses between danger zones 0–3. */
public final class ZoneHints {
    private static final Map<UUID, Integer> LAST = new ConcurrentHashMap<>();

    /** 0 safe, 1 calm, 2 wild, 3 dangerous. */
    public static int zoneOf(ServerLevel level, BlockPos pos) {
        if (level.dimension() != Level.OVERWORLD) {
            String ns = level.dimension().location().getNamespace();
            // Pocket/utility dimensions are not "dangerous".
            if (ns.equals("ae2") || ns.equals("irons_spellbooks") || ns.equals("occultism")) return 1;
            return 3;
        }
        if (SafeZones.isSafe(level, pos)) return 0;
        if (pos.getY() < 0) return 2;
        int calm = Config.CALM_RADIUS.get();
        if (SafeZones.horizontalDistSqr(pos, level.getSharedSpawnPos()) > (long) calm * calm) return 2;
        return 1;
    }

    @SubscribeEvent
    public static void onTick(PlayerTickEvent.Post event) {
        Player p = event.getEntity();
        if (!(p instanceof ServerPlayer sp) || sp.tickCount % 40 != 0 || !Config.ZONE_HINTS.get()) return;
        int zone = zoneOf(sp.serverLevel(), sp.blockPosition());
        Integer last = LAST.put(sp.getUUID(), zone);
        if (last == null || last == zone) return;
        ChatFormatting color = switch (zone) {
            case 0 -> ChatFormatting.GREEN;
            case 1 -> ChatFormatting.AQUA;
            case 2 -> ChatFormatting.GOLD;
            default -> ChatFormatting.RED;
        };
        sp.displayClientMessage(Component.translatable("message.arkhaven_core.zone." + zone).withStyle(color), true);
    }

    private ZoneHints() {}
}
