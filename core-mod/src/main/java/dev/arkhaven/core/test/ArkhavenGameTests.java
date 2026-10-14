package dev.arkhaven.core.test;

import dev.arkhaven.core.ArkhavenCore;
import dev.arkhaven.core.ModRegistry;
import dev.arkhaven.core.director.EventDirector;
import dev.arkhaven.core.ward.WardGeneratorBlockEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.monster.Creeper;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.gametest.GameTestHolder;
import net.neoforged.neoforge.gametest.PrefixGameTestTemplate;

/** GameTests required by docs/03_INTEGRATION.md §7. Run: ./gradlew runGameTestServer */
@GameTestHolder(ArkhavenCore.MODID)
@PrefixGameTestTemplate(false)
public final class ArkhavenGameTests {

    /** An explosion inside an active ward breaks nothing. */
    @GameTest(template = "empty", timeoutTicks = 100)
    public static void wardBlocksExplosion(GameTestHelper h) {
        BlockPos ward = new BlockPos(1, 1, 1);
        BlockPos stone = new BlockPos(5, 1, 5);
        h.setBlock(ward, ModRegistry.WARD_T1.get());
        h.setBlock(stone, Blocks.STONE);
        if (h.getBlockEntity(ward) instanceof WardGeneratorBlockEntity be) be.setFuelCrystals(1);
        h.runAfterDelay(10, () -> {
            Vec3 c = h.absoluteVec(Vec3.atCenterOf(stone));
            h.getLevel().explode(null, c.x, c.y + 1, c.z, 3.0f, Level.ExplosionInteraction.TNT);
            h.assertBlockPresent(Blocks.STONE, stone);
            h.succeed();
        });
    }

    /** Without fuel the same explosion breaks the block. */
    @GameTest(template = "empty", timeoutTicks = 100)
    public static void unfuelledWardDoesNothing(GameTestHelper h) {
        BlockPos ward = new BlockPos(1, 1, 1);
        BlockPos stone = new BlockPos(5, 1, 5);
        h.setBlock(ward, ModRegistry.WARD_T1.get());
        h.setBlock(stone, Blocks.STONE);
        h.runAfterDelay(10, () -> {
            Vec3 c = h.absoluteVec(Vec3.atCenterOf(stone));
            h.getLevel().explode(null, c.x, c.y + 0.5, c.z, 3.0f, Level.ExplosionInteraction.TNT);
            h.assertBlockNotPresent(Blocks.STONE, stone);
            h.succeed();
        });
    }

    /** Creeper explosions hurt but never break blocks. */
    @GameTest(template = "empty", timeoutTicks = 100)
    public static void creeperKeepsBlocks(GameTestHelper h) {
        BlockPos stone = new BlockPos(4, 1, 4);
        h.setBlock(stone, Blocks.STONE);
        Creeper creeper = h.spawn(EntityType.CREEPER, new BlockPos(4, 2, 4));
        Vec3 c = creeper.position();
        h.getLevel().explode(creeper, c.x, c.y, c.z, 3.0f, Level.ExplosionInteraction.MOB);
        h.assertBlockPresent(Blocks.STONE, stone);
        h.succeed();
    }

    /** The director never runs anything without players (the GameTest server has none). */
    @GameTest(template = "empty")
    public static void directorIdleWithoutPlayers(GameTestHelper h) {
        String reason = EventDirector.blockReason(h.getLevel().getServer());
        if (reason == null) h.fail("director would run with no players online");
        h.succeed();
    }
}
