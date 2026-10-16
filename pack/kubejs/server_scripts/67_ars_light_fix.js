// Ars Nouveau magic lights (ars_nouveau:light_block, the Light glyph) emit glow particles non-stop. With Particle Core's
// async particle ticking (packs <= 0.1.10) every such particle makes C2ME log a ConcurrentModificationException with a full
// stack trace on the client; near a few dozen lights the client hangs > 30 s and gets kicked ("Timed out").
// Server-side fix that needs no client update: every 5 s, in the chunks around each player, swap those lights for the
// vanilla invisible light block (same light level 15, no particles). Lights cast later get swapped the same way.
let arkLightTick = 0
let arkLightClasses = null

function arkLightInit() {
  arkLightClasses = {
    Reg: Java.loadClass('net.minecraft.core.registries.BuiltInRegistries'),
    Blocks: Java.loadClass('net.minecraft.world.level.block.Blocks')
  }
}

function arkSwapArsLights(server) {
  if (!arkLightClasses) arkLightInit()
  let swapped = 0
  server.players.forEach(p => {
    let level = p.level
    let source = level.getChunkSource()
    let cx = Math.floor(p.x) >> 4
    let cz = Math.floor(p.z) >> 4
    let found = []
    for (let dx = -6; dx <= 6; dx++) {
      for (let dz = -6; dz <= 6; dz++) {
        let chunk = source.getChunkNow(cx + dx, cz + dz)
        if (!chunk) continue
        chunk.getBlockEntities().values().forEach(be => {
          if (String(arkLightClasses.Reg.BLOCK_ENTITY_TYPE.getKey(be.getType())) === 'ars_nouveau:light_block') found.push(be.getBlockPos())
        })
      }
    }
    found.forEach(pos => {
      level.setBlock(pos, arkLightClasses.Blocks.LIGHT.defaultBlockState(), 3)
      swapped++
    })
  })
  if (swapped > 0) console.info('[Arkhaven] swapped ' + swapped + ' Ars magic lights for vanilla light blocks')
}

ServerEvents.tick(event => {
  if (++arkLightTick % 100 !== 0) return
  try { arkSwapArsLights(event.server) } catch (err) { console.error('[Arkhaven ars lights] ' + err) }
})
