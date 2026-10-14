package dev.arkhaven.core.ward;

import dev.arkhaven.core.ArkhavenCore;
import net.minecraft.core.registries.Registries;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;

/** Ward fuel is defined by item tags #arkhaven:ward_fuel/t1..t3 (filled with the KubeJS ward crystals). */
public final class WardFuel {
    public static final TagKey<Item> T1 = TagKey.create(Registries.ITEM, ArkhavenCore.pack("ward_fuel/t1"));
    public static final TagKey<Item> T2 = TagKey.create(Registries.ITEM, ArkhavenCore.pack("ward_fuel/t2"));
    public static final TagKey<Item> T3 = TagKey.create(Registries.ITEM, ArkhavenCore.pack("ward_fuel/t3"));

    /** @return 3, 2, 1 for fuel of that tier, 0 if the stack is not ward fuel. */
    public static int tierOf(ItemStack stack) {
        if (stack.is(T3)) return 3;
        if (stack.is(T2)) return 2;
        if (stack.is(T1)) return 1;
        return 0;
    }

    private WardFuel() {}
}
