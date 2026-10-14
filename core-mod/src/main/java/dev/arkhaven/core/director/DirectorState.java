package dev.arkhaven.core.director;

import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.StringTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.saveddata.SavedData;

import java.util.HashSet;
import java.util.Set;

/** Persistent director state (overworld data folder, arkhaven_director.dat). */
public final class DirectorState extends SavedData {
    long firstGameTime = -1;
    boolean vacation;
    final Set<String> trained = new HashSet<>();
    final Set<String> seen = new HashSet<>();
    long onlineTicksSinceStrike;
    long lastPlannedDay = -1;
    boolean tonightShower, tonightRift;
    boolean showerDone, riftDone;
    long showerEndTick;
    // pending strike
    boolean strikePending;
    BlockPos strikeTarget = BlockPos.ZERO;
    int strikeTicksLeft;
    boolean strikeTutorial;

    public static DirectorState get(MinecraftServer server) {
        return server.overworld().getDataStorage().computeIfAbsent(
                new SavedData.Factory<>(DirectorState::new, DirectorState::load, null), "arkhaven_director");
    }

    private static DirectorState load(CompoundTag t, HolderLookup.Provider registries) {
        DirectorState s = new DirectorState();
        s.firstGameTime = t.getLong("FirstGameTime");
        s.vacation = t.getBoolean("Vacation");
        readSet(t.getList("Trained", Tag.TAG_STRING), s.trained);
        readSet(t.getList("Seen", Tag.TAG_STRING), s.seen);
        s.onlineTicksSinceStrike = t.getLong("OnlineTicks");
        s.lastPlannedDay = t.getLong("LastPlannedDay");
        s.tonightShower = t.getBoolean("TonightShower");
        s.tonightRift = t.getBoolean("TonightRift");
        s.showerDone = t.getBoolean("ShowerDone");
        s.riftDone = t.getBoolean("RiftDone");
        s.strikePending = t.getBoolean("StrikePending");
        s.strikeTarget = BlockPos.of(t.getLong("StrikeTarget"));
        s.strikeTicksLeft = t.getInt("StrikeTicksLeft");
        s.strikeTutorial = t.getBoolean("StrikeTutorial");
        return s;
    }

    private static void readSet(ListTag list, Set<String> out) {
        for (int i = 0; i < list.size(); i++) out.add(list.getString(i));
    }

    private static ListTag writeSet(Set<String> in) {
        ListTag list = new ListTag();
        in.forEach(s -> list.add(StringTag.valueOf(s)));
        return list;
    }

    @Override
    public CompoundTag save(CompoundTag t, HolderLookup.Provider registries) {
        t.putLong("FirstGameTime", firstGameTime);
        t.putBoolean("Vacation", vacation);
        t.put("Trained", writeSet(trained));
        t.put("Seen", writeSet(seen));
        t.putLong("OnlineTicks", onlineTicksSinceStrike);
        t.putLong("LastPlannedDay", lastPlannedDay);
        t.putBoolean("TonightShower", tonightShower);
        t.putBoolean("TonightRift", tonightRift);
        t.putBoolean("ShowerDone", showerDone);
        t.putBoolean("RiftDone", riftDone);
        t.putBoolean("StrikePending", strikePending);
        t.putLong("StrikeTarget", strikeTarget.asLong());
        t.putInt("StrikeTicksLeft", strikeTicksLeft);
        t.putBoolean("StrikeTutorial", strikeTutorial);
        return t;
    }
}
