package dev.arkhaven.core.zones;

import dev.arkhaven.core.Config;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import org.jetbrains.annotations.Nullable;

/** Hearth stone: marks a home. Hostile mobs don't spawn naturally around it (zone 0). One per player; placing a new one moves it. */
public class HearthStoneBlock extends Block {
    public HearthStoneBlock(Properties props) {
        super(props);
    }

    @Override
    public void setPlacedBy(Level level, BlockPos pos, BlockState state, @Nullable LivingEntity placer, ItemStack stack) {
        super.setPlacedBy(level, pos, state, placer, stack);
        if (level instanceof ServerLevel sl && placer instanceof Player player) {
            BlockPos old = HearthStones.get(sl.getServer()).place(sl, pos, player.getUUID());
            if (old != null && !old.equals(pos) && sl.getBlockState(old).is(this)) sl.destroyBlock(old, true);
            player.displayClientMessage(Component.translatable("message.arkhaven_core.hearth.placed", Config.HEARTH_RADIUS.get()), false);
        }
    }

    @Override
    protected void onRemove(BlockState state, Level level, BlockPos pos, BlockState newState, boolean moved) {
        if (!state.is(newState.getBlock()) && level instanceof ServerLevel sl) HearthStones.get(sl.getServer()).remove(sl, pos);
        super.onRemove(state, level, pos, newState, moved);
    }
}
