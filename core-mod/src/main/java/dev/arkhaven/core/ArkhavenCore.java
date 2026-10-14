package dev.arkhaven.core;

import com.mojang.logging.LogUtils;
import dev.arkhaven.core.director.EventDirector;
import dev.arkhaven.core.zones.SafeZones;
import dev.arkhaven.core.zones.ZoneHints;
import net.minecraft.resources.ResourceLocation;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.ModContainer;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.config.ModConfig;
import net.neoforged.neoforge.common.NeoForge;
import org.slf4j.Logger;

/**
 * Arkhaven Core: the small amount of server logic KubeJS does badly.
 * Wards, meteors, rifts, the event director, safe zones, creeper-proof builds, zone hints.
 */
@Mod(ArkhavenCore.MODID)
public final class ArkhavenCore {
    public static final String MODID = "arkhaven_core";
    public static final Logger LOG = LogUtils.getLogger();

    public ArkhavenCore(IEventBus modBus, ModContainer container) {
        ModRegistry.register(modBus);
        container.registerConfig(ModConfig.Type.COMMON, Config.SPEC);
        NeoForge.EVENT_BUS.register(SafeZones.class);
        NeoForge.EVENT_BUS.register(ZoneHints.class);
        NeoForge.EVENT_BUS.register(EventDirector.class);
        NeoForge.EVENT_BUS.register(Commands.class);
        NeoForge.EVENT_BUS.register(dev.arkhaven.core.ward.WardManager.class);
    }

    public static ResourceLocation id(String path) {
        return ResourceLocation.fromNamespaceAndPath(MODID, path);
    }

    /** Items registered by KubeJS live in the plain "arkhaven" namespace. */
    public static ResourceLocation pack(String path) {
        return ResourceLocation.fromNamespaceAndPath("arkhaven", path);
    }
}
