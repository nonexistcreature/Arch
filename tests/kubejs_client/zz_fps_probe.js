// TEST ONLY (copied into the test client by tools/bench_client.py): logs FPS every 5 s while in a world.
let arkFpsTick = 0
ClientEvents.tick(e => {
  if (!Client.level || !Client.player) return
  if (++arkFpsTick % 100 === 0) console.info('ARK_FPS ' + Client.getFps())
})
