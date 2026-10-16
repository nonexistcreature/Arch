// TEST ONLY (copied into the benchmark client by tools/bench_client.py): flies the player (spectator) 2 blocks above
// the ground in a circle around ARK_CX/ARK_CZ (filled in by bench_client.py) at ~6 blocks/s (sprint speed), so the
// benchmark sees chunk rebuilds, trees and mobs the way a walking player does, not a still frame.
let arkMoveT = 0
let arkHeightmap = Java.loadClass('net.minecraft.world.level.levelgen.Heightmap$Types')
ServerEvents.tick(e => {
  if (++arkMoveT < 200 || arkMoveT % 2 !== 0) return
  let lvl = e.server.overworld()
  e.server.players.forEach(p => {
    if (arkMoveT === 200) {
      e.server.runCommandSilent(`gamemode spectator ${p.username}`)
      // a fresh bench player in a copied world would sit in the origin picker: pick for them
      e.server.runCommandSilent(`origin set ${p.username} neoorigins:origin neoorigins:human`)
      e.server.runCommandSilent(`origin set ${p.username} neoorigins:class neoorigins:class_warrior`)
    }
    let a = (arkMoveT - 200) / 2 * 0.6 / ARK_R   // 0.6 block per step, 10 steps per second
    let x = ARK_CX + Math.cos(a) * ARK_R, z = ARK_CZ + Math.sin(a) * ARK_R
    let y = lvl.getHeight(arkHeightmap.MOTION_BLOCKING_NO_LEAVES, Math.floor(x), Math.floor(z)) + 2
    let yaw = a * 180 / Math.PI   // face along the circle
    e.server.runCommandSilent(`execute in minecraft:overworld run tp ${p.username} ${x.toFixed(2)} ${y} ${z.toFixed(2)} ${yaw.toFixed(1)} 5`)
  })
})
