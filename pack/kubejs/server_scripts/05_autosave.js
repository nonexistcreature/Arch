// Explicit full save every 15 minutes (owner's request), on top of vanilla's 5-minute autosave.
// "save-all flush" writes every loaded chunk to disk right away, so a crash loses at most a few minutes.
const ARK_SAVE_EVERY_TICKS = 15 * 60 * 20

ServerEvents.tick(event => {
  const server = event.server
  if (server.tickCount % ARK_SAVE_EVERY_TICKS !== 0 || server.tickCount === 0) return
  try {
    server.runCommandSilent('save-all flush')
    console.info('[Arkhaven] autosave: world saved (every 15 min)')
  } catch (err) {
    console.error('[Arkhaven] autosave failed: ' + err)
  }
})
