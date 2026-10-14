package dev.arkhaven.core.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import dev.arkhaven.core.ArkhavenCore;
import dev.arkhaven.core.ModRegistry;
import dev.arkhaven.core.meteor.MeteorEntity;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.NoopRenderer;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.inventory.InventoryMenu;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.event.EntityRenderersEvent;

@EventBusSubscriber(modid = ArkhavenCore.MODID, bus = EventBusSubscriber.Bus.MOD, value = Dist.CLIENT)
public final class ArkhavenClient {
    @SubscribeEvent
    public static void renderers(EntityRenderersEvent.RegisterRenderers event) {
        event.registerEntityRenderer(ModRegistry.METEOR.get(), MeteorRenderer::new);
        event.registerEntityRenderer(ModRegistry.RIFT.get(), NoopRenderer::new);
    }

    /** Renders the meteor as a tumbling magma/ore rock, scaled by size. Fire and smoke come from client particles. */
    static final class MeteorRenderer extends EntityRenderer<MeteorEntity> {
        MeteorRenderer(EntityRendererProvider.Context ctx) {
            super(ctx);
            shadowRadius = 0.0f;
        }

        @Override
        public void render(MeteorEntity e, float yaw, float partial, PoseStack pose, MultiBufferSource buffers, int light) {
            float s = 0.6f + 0.5f * e.size();
            BlockState state = e.size() >= 3 ? ModRegistry.METEORITE_ORE.get().defaultBlockState() : Blocks.MAGMA_BLOCK.defaultBlockState();
            pose.pushPose();
            pose.scale(s, s, s);
            float spin = (e.tickCount + partial) * 9f;
            pose.mulPose(Axis.YP.rotationDegrees(spin));
            pose.mulPose(Axis.XP.rotationDegrees(spin * 0.7f));
            pose.translate(-0.5, -0.5, -0.5);
            net.minecraft.client.Minecraft.getInstance().getBlockRenderer().renderSingleBlock(state, pose, buffers, 0xF000F0, OverlayTexture.NO_OVERLAY);
            pose.popPose();
            super.render(e, yaw, partial, pose, buffers, light);
        }

        @Override
        public ResourceLocation getTextureLocation(MeteorEntity e) {
            return InventoryMenu.BLOCK_ATLAS;
        }
    }

    private ArkhavenClient() {}
}
