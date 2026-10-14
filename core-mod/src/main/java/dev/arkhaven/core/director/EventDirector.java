package dev.arkhaven.core.director;

import dev.arkhaven.core.ArkhavenCore;
import dev.arkhaven.core.Config;
import dev.arkhaven.core.meteor.MeteorEntity;
import dev.arkhaven.core.rift.RiftEntity;
import dev.arkhaven.core.ward.WardManager;
import dev.arkhaven.core.zones.SafeZones;
import dev.arkhaven.core.zones.ZoneHints;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.game.ClientboundSetSubtitleTextPacket;
import net.minecraft.network.protocol.game.ClientboundSetTitleTextPacket;
import net.minecraft.network.protocol.game.ClientboundSetTitlesAnimationPacket;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerBossEvent;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.BossEvent;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.Vec3;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.neoforge.event.server.ServerStoppedEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;

import java.util.List;

/**
 * The Event Director (docs/03_INTEGRATION.md §7, docs/05_WORLD_EVENTS.md).
 * Never runs anything with nobody online, during the grace period, on vacation or at intensity 0.
 * The first event of each type is a gentle tutorial. Disasters only run after the group "trained" for them
 * (KubeJS calls /arkhaven train <type> when the matching "Elements & Defence" quest is completed).
 */
public final class EventDirector {
    public static final String SHOWER = "shower", STRIKE = "strike", RIFT = "rift";
    private static final int PERIOD = 400; // 20 s
    private static ServerBossEvent strikeBar;

    // ---------------------------------------------------------------- public API (commands, wards)

    private static volatile boolean eventRunning;

    /** Cheap: refreshed once a second by the director tick (wards call this every tick). */
    public static boolean isEventRunning(MinecraftServer server) {
        return eventRunning;
    }

    public static String blockReason(MinecraftServer server) {
        DirectorState s = DirectorState.get(server);
        if (Config.INTENSITY.get() == 0) return "intensity0";
        if (s.vacation) return "vacation";
        if (server.getPlayerList().getPlayerCount() == 0) return "noplayers";
        if (inGrace(server, s)) return "grace";
        return null;
    }

    public static void train(MinecraftServer server, String type) {
        DirectorState s = DirectorState.get(server);
        if (s.trained.add(type)) s.setDirty();
    }

    public static void setVacation(MinecraftServer server, boolean on) {
        DirectorState s = DirectorState.get(server);
        s.vacation = on;
        if (on) cancelStrike(server, s);
        s.setDirty();
    }

    /** Forced start from /arkhaven event (ops). Ignores schedule and training but still never runs with 0 players. */
    public static boolean force(MinecraftServer server, String type, ServerPlayer target) {
        DirectorState s = DirectorState.get(server);
        ServerLevel ow = server.overworld();
        switch (type) {
            case SHOWER -> startShower(server, s, 20 * 60 * 3);
            case STRIKE -> {
                if (target == null) return false;
                return scheduleStrike(server, s, target, 30 * 20);
            }
            case RIFT -> {
                if (target == null) return false;
                BlockPos p = pickSpot(ow, target.blockPosition(), 24, 40, false);
                if (p == null) return false;
                boolean tutorial = s.seen.add(RIFT);
                RiftEntity.open(ow, p, tutorial ? 1 : 2 + Config.INTENSITY.get(), tutorial ? 2 : 4);
                s.setDirty();
            }
            default -> { return false; }
        }
        return true;
    }

    public static List<Component> forecast(MinecraftServer server) {
        DirectorState s = DirectorState.get(server);
        String reason = blockReason(server);
        long threshold = strikeThresholdTicks();
        int pct = (int) Math.min(100, s.onlineTicksSinceStrike * 100 / Math.max(1, threshold));
        return List.of(
                Component.translatable("message.arkhaven_core.forecast.title", Config.INTENSITY.get()).withStyle(ChatFormatting.GOLD),
                Component.translatable(s.tonightShower ? "message.arkhaven_core.forecast.shower_yes" : "message.arkhaven_core.forecast.shower_no"),
                Component.translatable(s.tonightRift && s.trained.contains(RIFT) ? "message.arkhaven_core.forecast.rift_yes" : "message.arkhaven_core.forecast.rift_no"),
                Component.translatable(s.trained.contains(STRIKE) ? "message.arkhaven_core.forecast.strike" : "message.arkhaven_core.forecast.strike_untrained", pct),
                Component.translatable("message.arkhaven_core.forecast.cooldown", hoursUntilNextDisaster(server)),
                reason == null ? Component.translatable("message.arkhaven_core.forecast.active")
                        : Component.translatable("message.arkhaven_core.forecast.paused." + reason).withStyle(ChatFormatting.GRAY));
    }

    public static Component status(MinecraftServer server) {
        DirectorState s = DirectorState.get(server);
        return Component.literal(String.format("intensity=%d vacation=%s trained=%s seen=%s onlineMin=%d strikePending=%s(%ds) tonight[shower=%s rift=%s] block=%s opac=%s",
                Config.INTENSITY.get(), s.vacation, s.trained, s.seen, s.onlineTicksSinceStrike / 1200, s.strikePending,
                s.strikeTicksLeft / 20, s.tonightShower, s.tonightRift, blockReason(server), SafeZones.opacAvailable()));
    }

    // ---------------------------------------------------------------- tick

    @SubscribeEvent
    public static void onServerTick(ServerTickEvent.Post event) {
        MinecraftServer server = event.getServer();
        ServerLevel ow = server.overworld();
        DirectorState s = DirectorState.get(server);
        if (s.firstGameTime < 0) { s.firstGameTime = ow.getGameTime(); s.setDirty(); }
        if (s.strikePending) tickStrike(server, s);
        if (server.getTickCount() % 20 == 0) {
            eventRunning = s.strikePending || ow.getGameTime() < s.showerEndTick
                    || !ow.getEntities(dev.arkhaven.core.ModRegistry.RIFT.get(), e -> true).isEmpty();
        }
        if (ow.getGameTime() < s.showerEndTick && ow.getGameTime() % 100 == 0) tickShower(server, s);
        if (server.getTickCount() % PERIOD != 0) return;

        String reason = blockReason(server);
        if (reason != null) {
            if (s.strikePending && !"grace".equals(reason)) cancelStrike(server, s);
            return;
        }
        s.onlineTicksSinceStrike += PERIOD;
        s.setDirty();

        long day = ow.getDayTime() / 24000L;
        long time = ow.getDayTime() % 24000L;
        RandomSource rnd = ow.random;
        int intensity = Config.INTENSITY.get();
        if (day != s.lastPlannedDay) {
            s.lastPlannedDay = day;
            s.tonightShower = rnd.nextDouble() < Config.SHOWER_NIGHT_CHANCE.get();
            double riftChance = Config.RIFT_NIGHT_CHANCE.get() * (intensity == 3 ? 2.5 : intensity == 2 ? 1.6 : 1.0);
            s.tonightRift = rnd.nextDouble() < riftChance;
            s.showerDone = false;
            s.riftDone = false;
        }
        boolean night = time >= 13000 && time <= 23000;
        if (night && s.tonightShower && !s.showerDone && !ow.isRaining()) {
            s.showerDone = true;
            startShower(server, s, 20 * 60 * 5);
        }
        if (night && time >= 14000 && s.tonightRift && !s.riftDone && s.trained.contains(RIFT) && !disasterCooldown(s)) {
            s.riftDone = true;
            startRiftNight(server, s);
        }
        if (!s.strikePending && s.trained.contains(STRIKE) && !disasterCooldown(s) && s.onlineTicksSinceStrike >= strikeThresholdTicks() && rnd.nextInt(30) == 0) {
            List<ServerPlayer> players = ow.players();
            if (!players.isEmpty()) scheduleStrike(server, s, players.get(rnd.nextInt(players.size())), Config.STRIKE_WARNING_SECONDS.get() * 20);
        }
    }

    @SubscribeEvent
    public static void onStopped(ServerStoppedEvent event) {
        strikeBar = null;
    }

    /** Owner's rule: at most one disaster per N real hours (default 72). */
    static boolean disasterCooldown(DirectorState s) {
        return System.currentTimeMillis() - s.lastDisasterMillis < Config.MIN_REAL_HOURS_BETWEEN_DISASTERS.get() * 3_600_000L;
    }

    static void markDisaster(DirectorState s) {
        s.lastDisasterMillis = System.currentTimeMillis();
        s.setDirty();
    }

    public static long hoursUntilNextDisaster(MinecraftServer server) {
        DirectorState s = DirectorState.get(server);
        long left = Config.MIN_REAL_HOURS_BETWEEN_DISASTERS.get() * 3_600_000L - (System.currentTimeMillis() - s.lastDisasterMillis);
        return Math.max(0, (left + 3_599_999L) / 3_600_000L);
    }

    private static boolean inGrace(MinecraftServer server, DirectorState s) {
        return s.firstGameTime >= 0 && server.overworld().getGameTime() - s.firstGameTime < Config.GRACE_DAYS.get() * 24000L;
    }

    private static long strikeThresholdTicks() {
        long t = Config.STRIKE_MIN_ONLINE_MINUTES.get() * 1200L;
        return switch (Config.INTENSITY.get()) { case 3 -> t / 4; case 2 -> t / 2; default -> t; };
    }

    // ---------------------------------------------------------------- meteor shower

    private static void startShower(MinecraftServer server, DirectorState s, int durationTicks) {
        ServerLevel ow = server.overworld();
        boolean tutorial = s.seen.add(SHOWER);
        s.showerEndTick = ow.getGameTime() + durationTicks;
        s.setDirty();
        announce(server, "shower", tutorial, ChatFormatting.YELLOW);
    }

    private static void tickShower(MinecraftServer server, DirectorState s) {
        ServerLevel ow = server.overworld();
        RandomSource rnd = ow.random;
        for (ServerPlayer p : ow.players()) {
            // Mostly beautiful streaks that burn up high in the sky.
            for (int i = 0; i < 2; i++) {
                Vec3 t = p.position().add(rnd.nextInt(400) - 200, 0, rnd.nextInt(400) - 200);
                MeteorEntity.spawn(ow, new Vec3(t.x, 140, t.z), 1, true, 150 + rnd.nextInt(40));
            }
            // Occasionally a small one lands in the wild: a gift of meteoric dust.
            if (rnd.nextInt(6) == 0) {
                BlockPos spot = pickSpot(ow, p.blockPosition(), 150, 400, true);
                if (spot != null && !disasterCooldown(s)) MeteorEntity.spawn(ow, Vec3.atCenterOf(spot), 1, true, -1);
            }
        }
    }

    // ---------------------------------------------------------------- rift night

    private static void startRiftNight(MinecraftServer server, DirectorState s) {
        ServerLevel ow = server.overworld();
        markDisaster(s);
        boolean tutorial = s.seen.add(RIFT);
        s.setDirty();
        announce(server, "rift", tutorial, ChatFormatting.DARK_PURPLE);
        int intensity = Config.INTENSITY.get();
        for (ServerPlayer p : ow.players()) {
            int min = intensity >= 2 ? 48 : 64, max = intensity >= 2 ? 96 : 128;
            BlockPos spot = pickSpot(ow, p.blockPosition(), min, max, true);
            if (spot == null) continue;
            RiftEntity.open(ow, spot, tutorial ? 1 : 2 + intensity, tutorial ? 2 : 3 + intensity);
        }
    }

    // ---------------------------------------------------------------- meteor strike

    private static boolean scheduleStrike(MinecraftServer server, DirectorState s, ServerPlayer target, int warningTicks) {
        ServerLevel ow = server.overworld();
        boolean tutorial = !s.seen.contains(STRIKE);
        int intensity = Config.INTENSITY.get();
        BlockPos base = target.getRespawnPosition() != null && target.getRespawnDimension() == ow.dimension() ? target.getRespawnPosition() : target.blockPosition();
        BlockPos spot = null;
        if (!tutorial && intensity >= 2 && ow.random.nextFloat() < 0.3f && !WardManager.isProtected(ow, Vec3.atCenterOf(base))) spot = base;
        if (spot == null) spot = pickSpot(ow, base, tutorial ? 150 : 60, tutorial ? 220 : 120, intensity <= 1 || tutorial);
        // Bases inside the Haven: look further out until we leave the safe zone.
        for (int r = 300; spot == null && r <= 900; r += 200) spot = pickSpot(ow, base, r, r + 150, true);
        if (spot == null) return false;
        s.strikePending = true;
        s.strikeTarget = spot;
        s.strikeTicksLeft = warningTicks;
        s.strikeTutorial = tutorial;
        s.setDirty();
        announce(server, "strike", tutorial, ChatFormatting.RED);
        server.getPlayerList().broadcastSystemMessage(Component.translatable("message.arkhaven_core.event.strike.where",
                spot.getX(), spot.getZ(), warningTicks / 20 / 60, warningTicks / 20 % 60).withStyle(ChatFormatting.RED), false);
        return true;
    }

    private static void tickStrike(MinecraftServer server, DirectorState s) {
        ServerLevel ow = server.overworld();
        if (strikeBar == null) {
            strikeBar = new ServerBossEvent(Component.translatable("message.arkhaven_core.event.strike.bar"), BossEvent.BossBarColor.RED, BossEvent.BossBarOverlay.NOTCHED_10);
        }
        int total = Math.max(1, Config.STRIKE_WARNING_SECONDS.get() * 20);
        strikeBar.setProgress(Math.max(0f, Math.min(1f, s.strikeTicksLeft / (float) total)));
        for (ServerPlayer p : ow.players()) if (!strikeBar.getPlayers().contains(p)) strikeBar.addPlayer(p);
        if (s.strikeTicksLeft % 100 == 0) {
            // A glowing streak in the sky shows where it will fall.
            Vec3 t = Vec3.atCenterOf(s.strikeTarget);
            ow.sendParticles(ParticleTypes.END_ROD, t.x, Math.min(ow.getMaxBuildHeight() - 2, t.y + 90), t.z, 40, 2, 6, 2, 0.02);
        }
        if (s.strikeTicksLeft == 20 * 60 || s.strikeTicksLeft == 20 * 10) {
            for (ServerPlayer p : ow.players()) p.playNotifySound(SoundEvents.BELL_BLOCK, SoundSource.MASTER, 1.0f, 0.6f);
        }
        if (--s.strikeTicksLeft <= 0) {
            BlockPos ground = ow.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, s.strikeTarget);
            MeteorEntity.spawn(ow, Vec3.atCenterOf(ground), s.strikeTutorial ? 2 : 3, s.strikeTutorial, -1);
            s.seen.add(STRIKE);
            markDisaster(s);
            s.onlineTicksSinceStrike = 0;
            s.strikePending = false;
            strikeBar.removeAllPlayers();
            strikeBar = null;
        }
        s.setDirty();
    }

    private static void cancelStrike(MinecraftServer server, DirectorState s) {
        if (!s.strikePending) return;
        s.strikePending = false;
        s.setDirty();
        if (strikeBar != null) { strikeBar.removeAllPlayers(); strikeBar = null; }
        ArkhavenCore.LOG.info("Pending meteor strike cancelled (no players / vacation / intensity 0)");
    }

    // ---------------------------------------------------------------- helpers

    /** Random surface spot min..max blocks away; with avoidSafe it is never in zone 0. */
    private static BlockPos pickSpot(ServerLevel level, BlockPos around, int min, int max, boolean avoidSafe) {
        RandomSource rnd = level.random;
        for (int i = 0; i < 16; i++) {
            double a = rnd.nextDouble() * Math.PI * 2;
            int d = min + rnd.nextInt(Math.max(1, max - min));
            BlockPos p = level.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,
                    around.offset((int) (Math.cos(a) * d), 0, (int) (Math.sin(a) * d)));
            if (!level.isLoaded(p)) continue;
            if (avoidSafe && (ZoneHints.zoneOf(level, p) == 0 || SafeZones.isClaimedNear(level, p, 16) || WardManager.isProtected(level, Vec3.atCenterOf(p)))) continue;
            return p;
        }
        return null;
    }

    private static void announce(MinecraftServer server, String type, boolean tutorial, ChatFormatting color) {
        Component title = Component.translatable("message.arkhaven_core.event." + type + ".title").withStyle(color);
        Component sub = Component.translatable("message.arkhaven_core.event." + type + (tutorial ? ".tutorial" : ".subtitle"));
        for (ServerPlayer p : server.getPlayerList().getPlayers()) {
            p.connection.send(new ClientboundSetTitlesAnimationPacket(10, 80, 20));
            p.connection.send(new ClientboundSetTitleTextPacket(title));
            p.connection.send(new ClientboundSetSubtitleTextPacket(sub));
            p.playNotifySound(SoundEvents.RAID_HORN.value(), SoundSource.MASTER, 0.6f, 1.2f);
            p.sendSystemMessage(Component.translatable("message.arkhaven_core.event." + type + ".chat").withStyle(color));
            if (tutorial) p.sendSystemMessage(Component.translatable("message.arkhaven_core.event.tutorial_note").withStyle(ChatFormatting.GRAY));
        }
        ArkhavenCore.LOG.info("Event {} started (tutorial={})", type, tutorial);
    }

    private EventDirector() {}
}
