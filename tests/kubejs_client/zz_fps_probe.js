// TEST ONLY (copied into the test client by tools/bench_client.py): every 5 s in a world logs FPS and
// frame-time stability: p99 frame time, worst frame, frames slower than 33 ms / 50 ms (stutters).
let arkFpsTick = 0
let arkFt = []
let arkFtLast = 0
NativeEvents.onEvent('net.neoforged.neoforge.client.event.RenderFrameEvent$Post', e => {
  let now = Date.now()
  if (arkFtLast > 0) arkFt.push(now - arkFtLast)
  arkFtLast = now
})
ClientEvents.tick(e => {
  if (!Client.level || !Client.player) return
  // benchmark measures the world, not menus (origin picker, mod adverts): close whatever screen is open
  if (Client.screen && arkFpsTick > 300) Client.setScreen(null)
  if (++arkFpsTick % 100 !== 0) return
  let ft = arkFt
  arkFt = []
  if (ft.length < 2) return
  ft.sort((a, b) => a - b)
  let s33 = 0, s50 = 0, sum = 0
  for (let i = 0; i < ft.length; i++) { sum += ft[i]; if (ft[i] > 33.4) s33++; if (ft[i] > 50) s50++ }
  let p99 = ft[Math.min(ft.length - 1, Math.floor(ft.length * 0.99))]
  console.info('ARK_FPS ' + Client.getFps())
  console.info('ARK_FT fps=' + Math.round(ft.length * 1000 / sum) + ' p99=' + p99.toFixed(1) + ' max=' + ft[ft.length - 1].toFixed(1) + ' s33=' + s33 + ' s50=' + s50)
})
