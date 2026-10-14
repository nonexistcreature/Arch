package dev.arkhaven.core;

import net.neoforged.neoforge.common.ModConfigSpec;

/** config/arkhaven_core-common.toml — every number from docs/03_INTEGRATION.md §7 and docs/05_WORLD_EVENTS.md. */
public final class Config {
    private static final ModConfigSpec.Builder B = new ModConfigSpec.Builder();

    public static final ModConfigSpec.IntValue INTENSITY = B
            .comment("Disaster intensity: 0 = off, 1 = gentle (default), 2 = serious, 3 = harsh")
            .defineInRange("events.intensity", 1, 0, 3);
    public static final ModConfigSpec.IntValue MIN_REAL_HOURS_BETWEEN_DISASTERS = B
            .comment("Real-world hours that must pass between two disasters (meteor strike, rift night, meteor-shower impacts).",
                     "Owner's rule: at most once every 3 real days, so players always have time to prepare.")
            .defineInRange("events.minRealHoursBetweenDisasters", 72, 1, 24 * 60);
    public static final ModConfigSpec.IntValue GRACE_DAYS = B
            .comment("In-game days after the world starts during which no events run")
            .defineInRange("events.graceDays", 7, 0, 365);
    public static final ModConfigSpec.IntValue STRIKE_MIN_ONLINE_MINUTES = B
            .comment("Minimum accumulated player-online minutes between two meteor strikes (intensity 1). Halved at 2, quartered at 3.")
            .defineInRange("events.strikeMinOnlineMinutes", 360, 10, 100000);
    public static final ModConfigSpec.IntValue STRIKE_WARNING_SECONDS = B
            .comment("Real seconds of warning before a meteor strike")
            .defineInRange("events.strikeWarningSeconds", 600, 30, 3600);
    public static final ModConfigSpec.DoubleValue RIFT_NIGHT_CHANCE = B
            .comment("Chance that a night becomes a rift night (intensity 1). x1.6 at 2, x2.5 at 3.")
            .defineInRange("events.riftNightChance", 0.10, 0.0, 1.0);
    public static final ModConfigSpec.DoubleValue SHOWER_NIGHT_CHANCE = B
            .comment("Chance that a clear night gets a meteor shower (mostly a reward)")
            .defineInRange("events.showerNightChance", 0.33, 0.0, 1.0);

    public static final ModConfigSpec.IntValue HAVEN_RADIUS = B
            .comment("Radius (blocks) around world spawn where hostile mobs never spawn naturally (zone 0)")
            .defineInRange("zones.havenRadius", 256, 0, 10000);
    public static final ModConfigSpec.IntValue CALM_RADIUS = B
            .comment("Radius around world spawn of the calm lands (zone 1); beyond is the wild (zone 2)")
            .defineInRange("zones.calmRadius", 1500, 0, 100000);
    public static final ModConfigSpec.IntValue CLAIM_MARGIN = B
            .comment("Extra safe margin (blocks) around Open Parties and Claims claims and hearth stones")
            .defineInRange("zones.claimMargin", 48, 0, 256);
    public static final ModConfigSpec.IntValue HEARTH_RADIUS = B
            .comment("Safe radius of a hearth stone")
            .defineInRange("zones.hearthRadius", 48, 8, 256);
    public static final ModConfigSpec.BooleanValue ZONE_HINTS = B
            .comment("Show an actionbar hint when crossing between danger zones")
            .define("zones.actionbarHints", true);
    public static final ModConfigSpec.BooleanValue CREEPERS_KEEP_BLOCKS = B
            .comment("Creeper explosions damage entities but never break blocks")
            .define("zones.creepersKeepBlocks", true);

    public static final ModConfigSpec.IntValue WARD_RADIUS_T1 = B.defineInRange("wards.radiusT1", 32, 4, 512);
    public static final ModConfigSpec.IntValue WARD_RADIUS_T2 = B.defineInRange("wards.radiusT2", 64, 4, 512);
    public static final ModConfigSpec.IntValue WARD_RADIUS_T3 = B.defineInRange("wards.radiusT3", 128, 4, 512);
    public static final ModConfigSpec.IntValue WARD_MINUTES_PER_CRYSTAL = B
            .comment("Real minutes of protection one crystal gives (only consumed while a player is near or an event runs)")
            .defineInRange("wards.minutesPerCrystal", 60, 1, 10000);

    public static final ModConfigSpec SPEC = B.build();

    private Config() {}

    public static int wardRadius(int tier) {
        return switch (tier) {
            case 3 -> WARD_RADIUS_T3.get();
            case 2 -> WARD_RADIUS_T2.get();
            default -> WARD_RADIUS_T1.get();
        };
    }
}
