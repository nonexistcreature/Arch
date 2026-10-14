package dev.arkhaven.core;

import dev.arkhaven.core.meteor.MeteorEntity;
import dev.arkhaven.core.rift.RiftEntity;
import dev.arkhaven.core.ward.WardGeneratorBlock;
import dev.arkhaven.core.ward.WardGeneratorBlockEntity;
import dev.arkhaven.core.zones.HearthStoneBlock;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

public final class ModRegistry {
    public static final DeferredRegister.Blocks BLOCKS = DeferredRegister.createBlocks(ArkhavenCore.MODID);
    public static final DeferredRegister.Items ITEMS = DeferredRegister.createItems(ArkhavenCore.MODID);
    public static final DeferredRegister<BlockEntityType<?>> BLOCK_ENTITIES = DeferredRegister.create(Registries.BLOCK_ENTITY_TYPE, ArkhavenCore.MODID);
    public static final DeferredRegister<EntityType<?>> ENTITIES = DeferredRegister.create(Registries.ENTITY_TYPE, ArkhavenCore.MODID);
    public static final DeferredRegister<CreativeModeTab> TABS = DeferredRegister.create(Registries.CREATIVE_MODE_TAB, ArkhavenCore.MODID);

    private static BlockBehaviour.Properties machine() {
        return BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_LIGHT_BLUE).strength(4.0f, 1200.0f)
                .sound(SoundType.AMETHYST).requiresCorrectToolForDrops().lightLevel(s -> s.getValue(WardGeneratorBlock.ACTIVE) ? 12 : 3);
    }

    public static final DeferredBlock<WardGeneratorBlock> WARD_T1 = BLOCKS.register("ward_generator_t1", () -> new WardGeneratorBlock(1, machine()));
    public static final DeferredBlock<WardGeneratorBlock> WARD_T2 = BLOCKS.register("ward_generator_t2", () -> new WardGeneratorBlock(2, machine()));
    public static final DeferredBlock<WardGeneratorBlock> WARD_T3 = BLOCKS.register("ward_generator_t3", () -> new WardGeneratorBlock(3, machine()));
    public static final DeferredBlock<HearthStoneBlock> HEARTH_STONE = BLOCKS.register("hearth_stone",
            () -> new HearthStoneBlock(BlockBehaviour.Properties.of().mapColor(MapColor.STONE).strength(3.0f, 1200.0f)
                    .sound(SoundType.STONE).lightLevel(s -> 10)));
    public static final DeferredBlock<Block> METEORITE_ORE = BLOCKS.register("meteorite_ore",
            () -> new Block(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_BLACK).strength(4.5f, 6.0f)
                    .sound(SoundType.ANCIENT_DEBRIS).requiresCorrectToolForDrops().lightLevel(s -> 4)));

    public static final DeferredItem<BlockItem> WARD_T1_ITEM = ITEMS.registerSimpleBlockItem(WARD_T1);
    public static final DeferredItem<BlockItem> WARD_T2_ITEM = ITEMS.registerSimpleBlockItem(WARD_T2);
    public static final DeferredItem<BlockItem> WARD_T3_ITEM = ITEMS.registerSimpleBlockItem(WARD_T3);
    public static final DeferredItem<BlockItem> HEARTH_STONE_ITEM = ITEMS.registerSimpleBlockItem(HEARTH_STONE);
    public static final DeferredItem<BlockItem> METEORITE_ORE_ITEM = ITEMS.registerSimpleBlockItem(METEORITE_ORE);
    public static final DeferredItem<Item> STAR_ATLAS = ITEMS.register("star_atlas", () -> new dev.arkhaven.core.director.StarAtlasItem(new Item.Properties().stacksTo(1)));

    @SuppressWarnings("DataFlowIssue")
    public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<WardGeneratorBlockEntity>> WARD_BE = BLOCK_ENTITIES.register("ward_generator",
            () -> BlockEntityType.Builder.of(WardGeneratorBlockEntity::new, WARD_T1.get(), WARD_T2.get(), WARD_T3.get()).build(null));

    public static final DeferredHolder<EntityType<?>, EntityType<MeteorEntity>> METEOR = ENTITIES.register("meteor",
            () -> EntityType.Builder.<MeteorEntity>of(MeteorEntity::new, MobCategory.MISC).sized(1.6f, 1.6f)
                    .clientTrackingRange(24).updateInterval(1).fireImmune().build("arkhaven_core:meteor"));
    public static final DeferredHolder<EntityType<?>, EntityType<RiftEntity>> RIFT = ENTITIES.register("rift",
            () -> EntityType.Builder.<RiftEntity>of(RiftEntity::new, MobCategory.MISC).sized(1.0f, 3.0f)
                    .clientTrackingRange(16).fireImmune().build("arkhaven_core:rift"));

    public static final DeferredHolder<CreativeModeTab, CreativeModeTab> TAB = TABS.register("main", () -> CreativeModeTab.builder()
            .title(Component.translatable("itemGroup.arkhaven_core"))
            .icon(() -> new ItemStack(WARD_T1_ITEM.get()))
            .displayItems((params, out) -> {
                out.accept(WARD_T1_ITEM.get());
                out.accept(WARD_T2_ITEM.get());
                out.accept(WARD_T3_ITEM.get());
                out.accept(HEARTH_STONE_ITEM.get());
                out.accept(METEORITE_ORE_ITEM.get());
                out.accept(STAR_ATLAS.get());
            }).build());

    public static void register(IEventBus bus) {
        BLOCKS.register(bus);
        ITEMS.register(bus);
        BLOCK_ENTITIES.register(bus);
        ENTITIES.register(bus);
        TABS.register(bus);
    }

    private ModRegistry() {}
}
