package dev.arkhaven.core.zones;

import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.saveddata.SavedData;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/** Persistent list of hearth stones (dimension, position, owner). One per player. Stored in the overworld data folder. */
public final class HearthStones extends SavedData {
    public record Hearth(String dim, BlockPos pos, UUID owner) {}

    private final List<Hearth> hearths = new ArrayList<>();

    public static HearthStones get(MinecraftServer server) {
        return server.overworld().getDataStorage().computeIfAbsent(
                new SavedData.Factory<>(HearthStones::new, HearthStones::load, null), "arkhaven_hearths");
    }

    private static HearthStones load(CompoundTag tag, HolderLookup.Provider registries) {
        HearthStones h = new HearthStones();
        ListTag list = tag.getList("Hearths", Tag.TAG_COMPOUND);
        for (int i = 0; i < list.size(); i++) {
            CompoundTag t = list.getCompound(i);
            h.hearths.add(new Hearth(t.getString("Dim"), BlockPos.of(t.getLong("Pos")), t.getUUID("Owner")));
        }
        return h;
    }

    @Override
    public CompoundTag save(CompoundTag tag, HolderLookup.Provider registries) {
        ListTag list = new ListTag();
        for (Hearth h : hearths) {
            CompoundTag t = new CompoundTag();
            t.putString("Dim", h.dim());
            t.putLong("Pos", h.pos().asLong());
            t.putUUID("Owner", h.owner());
            list.add(t);
        }
        tag.put("Hearths", list);
        return tag;
    }

    /** Places (or moves) the owner's hearth. Returns the previous position if it moved. */
    public BlockPos place(ServerLevel level, BlockPos pos, UUID owner) {
        BlockPos old = null;
        for (int i = hearths.size() - 1; i >= 0; i--) {
            if (hearths.get(i).owner().equals(owner)) {
                old = hearths.get(i).pos();
                hearths.remove(i);
            }
        }
        hearths.add(new Hearth(level.dimension().location().toString(), pos.immutable(), owner));
        setDirty();
        return old;
    }

    public void remove(ServerLevel level, BlockPos pos) {
        String dim = level.dimension().location().toString();
        if (hearths.removeIf(h -> h.dim().equals(dim) && h.pos().equals(pos))) setDirty();
    }

    public boolean isNearHearth(ServerLevel level, BlockPos pos, int radius) {
        String dim = level.dimension().location().toString();
        long r2 = (long) radius * radius;
        for (Hearth h : hearths) if (h.dim().equals(dim) && SafeZones.horizontalDistSqr(h.pos(), pos) <= r2) return true;
        return false;
    }

    public List<Hearth> all() {
        return List.copyOf(hearths);
    }
}
