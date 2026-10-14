package dev.arkhaven.core;

import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.mojang.brigadier.context.CommandContext;
import dev.arkhaven.core.director.EventDirector;
import dev.arkhaven.core.ward.WardGeneratorBlockEntity;
import dev.arkhaven.core.zones.ZoneHints;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.SharedSuggestionProvider;
import net.minecraft.commands.arguments.EntityArgument;
import net.minecraft.commands.arguments.coordinates.BlockPosArgument;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.neoforge.event.RegisterCommandsEvent;

import java.util.List;

/**
 * /arkhaven status | forecast | zone | event <shower|strike|rift> [player] | vacation on|off | intensity <0-3>
 *          | train <type> | kit demo [player] | ward fill <pos> <crystals>
 * Everything except forecast/zone needs permission level 2.
 */
public final class Commands {
    private static final List<String> TYPES = List.of(EventDirector.SHOWER, EventDirector.STRIKE, EventDirector.RIFT);

    @SubscribeEvent
    public static void register(RegisterCommandsEvent event) {
        CommandDispatcher<CommandSourceStack> d = event.getDispatcher();
        d.register(net.minecraft.commands.Commands.literal("arkhaven")
                .then(net.minecraft.commands.Commands.literal("forecast").executes(ctx -> {
                    EventDirector.forecast(ctx.getSource().getServer()).forEach(c -> ctx.getSource().sendSuccess(() -> c, false));
                    return 1;
                }))
                .then(net.minecraft.commands.Commands.literal("zone").executes(ctx -> {
                    ServerPlayer p = ctx.getSource().getPlayerOrException();
                    int z = ZoneHints.zoneOf(p.serverLevel(), p.blockPosition());
                    ctx.getSource().sendSuccess(() -> Component.translatable("message.arkhaven_core.zone." + z), false);
                    return z;
                }))
                .then(net.minecraft.commands.Commands.literal("status").requires(s -> s.hasPermission(2)).executes(ctx -> {
                    ctx.getSource().sendSuccess(() -> EventDirector.status(ctx.getSource().getServer()), false);
                    return 1;
                }))
                .then(net.minecraft.commands.Commands.literal("event").requires(s -> s.hasPermission(2))
                        .then(net.minecraft.commands.Commands.argument("type", StringArgumentType.word())
                                .suggests((c, b) -> SharedSuggestionProvider.suggest(TYPES, b))
                                .executes(ctx -> runEvent(ctx, ctx.getSource().getPlayer()))
                                .then(net.minecraft.commands.Commands.argument("player", EntityArgument.player())
                                        .executes(ctx -> runEvent(ctx, EntityArgument.getPlayer(ctx, "player"))))))
                .then(net.minecraft.commands.Commands.literal("vacation").requires(s -> s.hasPermission(2))
                        .then(net.minecraft.commands.Commands.literal("on").executes(ctx -> vacation(ctx, true)))
                        .then(net.minecraft.commands.Commands.literal("off").executes(ctx -> vacation(ctx, false))))
                .then(net.minecraft.commands.Commands.literal("intensity").requires(s -> s.hasPermission(2))
                        .then(net.minecraft.commands.Commands.argument("level", IntegerArgumentType.integer(0, 3)).executes(ctx -> {
                            int lvl = IntegerArgumentType.getInteger(ctx, "level");
                            Config.INTENSITY.set(lvl);
                            Config.INTENSITY.save();
                            ctx.getSource().sendSuccess(() -> Component.translatable("message.arkhaven_core.cmd.intensity", lvl), true);
                            return lvl;
                        })))
                .then(net.minecraft.commands.Commands.literal("train").requires(s -> s.hasPermission(2))
                        .then(net.minecraft.commands.Commands.argument("type", StringArgumentType.word())
                                .suggests((c, b) -> SharedSuggestionProvider.suggest(TYPES, b))
                                .executes(ctx -> {
                                    String t = StringArgumentType.getString(ctx, "type");
                                    EventDirector.train(ctx.getSource().getServer(), t);
                                    ctx.getSource().sendSuccess(() -> Component.literal("trained: " + t), true);
                                    return 1;
                                })))
                .then(net.minecraft.commands.Commands.literal("kit").requires(s -> s.hasPermission(2))
                        .then(net.minecraft.commands.Commands.literal("demo")
                                .executes(ctx -> kit(ctx, ctx.getSource().getPlayerOrException()))
                                .then(net.minecraft.commands.Commands.argument("player", EntityArgument.player())
                                        .executes(ctx -> kit(ctx, EntityArgument.getPlayer(ctx, "player"))))))
                .then(net.minecraft.commands.Commands.literal("ward").requires(s -> s.hasPermission(2))
                        .then(net.minecraft.commands.Commands.literal("fill")
                                .then(net.minecraft.commands.Commands.argument("pos", BlockPosArgument.blockPos())
                                        .then(net.minecraft.commands.Commands.argument("crystals", IntegerArgumentType.integer(0, 16)).executes(ctx -> {
                                            BlockPos pos = BlockPosArgument.getLoadedBlockPos(ctx, "pos");
                                            if (!(ctx.getSource().getLevel().getBlockEntity(pos) instanceof WardGeneratorBlockEntity be)) {
                                                ctx.getSource().sendFailure(Component.literal("no ward generator at " + pos.toShortString()));
                                                return 0;
                                            }
                                            be.setFuelCrystals(IntegerArgumentType.getInteger(ctx, "crystals"));
                                            ctx.getSource().sendSuccess(be::statusLine, true);
                                            return 1;
                                        }))))));
    }

    private static int runEvent(CommandContext<CommandSourceStack> ctx, ServerPlayer target) {
        String type = StringArgumentType.getString(ctx, "type");
        if (ctx.getSource().getServer().getPlayerList().getPlayerCount() == 0) {
            ctx.getSource().sendFailure(Component.translatable("message.arkhaven_core.cmd.noplayers"));
            return 0;
        }
        boolean ok = EventDirector.force(ctx.getSource().getServer(), type, target);
        if (ok) ctx.getSource().sendSuccess(() -> Component.translatable("message.arkhaven_core.cmd.event", type), true);
        else ctx.getSource().sendFailure(Component.translatable("message.arkhaven_core.cmd.event_failed", type));
        return ok ? 1 : 0;
    }

    private static int vacation(CommandContext<CommandSourceStack> ctx, boolean on) {
        EventDirector.setVacation(ctx.getSource().getServer(), on);
        ctx.getSource().sendSuccess(() -> Component.translatable(on ? "message.arkhaven_core.cmd.vacation_on" : "message.arkhaven_core.cmd.vacation_off"), true);
        return 1;
    }

    /** Demo kit for the owner's first look (docs/09_ROADMAP.md HANDOFF): a small plane's worth of parts and some treats. */
    private static int kit(CommandContext<CommandSourceStack> ctx, ServerPlayer p) {
        String[][] kit = {
                {"simulated:physics_assembler", "1"}, {"aeronautics:propeller_bearing", "2"}, {"aeronautics:wooden_propeller", "2"},
                {"simulated:steering_wheel", "1"}, {"simulated:throttle_lever", "1"}, {"create:creative_motor", "2"},
                {"aeronautics:levitite", "16"}, {"aeronautics:aviators_goggles", "1"}, {"create:shaft", "16"}, {"create:cogwheel", "8"},
                {"minecraft:oak_planks", "64"}, {"minecraft:white_wool", "32"}, {"create:super_glue", "1"}, {"create:wrench", "1"},
                {"arkhaven_core:ward_generator_t1", "1"}, {"arkhaven:ward_crystal_t1", "4"}, {"arkhaven_core:star_atlas", "1"},
                {"farmersdelight:beef_stew", "4"}, {"vinery:red_wine", "1"}
        };
        int given = 0;
        for (String[] e : kit) {
            Item item = BuiltInRegistries.ITEM.get(ResourceLocation.parse(e[0]));
            if (item == Items.AIR) continue;
            ItemStack st = new ItemStack(item, Integer.parseInt(e[1]));
            if (!p.getInventory().add(st)) p.drop(st, false);
            given++;
        }
        int n = given;
        ctx.getSource().sendSuccess(() -> Component.translatable("message.arkhaven_core.cmd.kit", n), true);
        return n;
    }

    private Commands() {}
}
