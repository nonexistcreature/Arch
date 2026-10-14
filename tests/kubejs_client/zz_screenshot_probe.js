// TEST ONLY: in-game screenshots (only the game window, never the desktop). Copied into the test client by
// tools/e2e_test.py. Takes a screenshot whenever a screen (e.g. the quest book) has been open for 5 seconds.
let arkShotTicks = 0
let arkShotDone = false
ClientEvents.tick(e => {
  if (!Client.player) return
  if (Client.screen == null) { arkShotTicks = 0; arkShotDone = false; return }
  if (arkShotDone || ++arkShotTicks < 100) return
  arkShotDone = true
  const Screenshot = Java.loadClass('net.minecraft.client.Screenshot')
  Screenshot.grab(Client.gameDirectory, Client.getMainRenderTarget(), msg => console.info('ARK_SCREENSHOT ' + msg.getString()))
})
