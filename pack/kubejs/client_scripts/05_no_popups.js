// Enhanced Celestials 6.0.2.6 opens an "Enhanced Celestials 2 is here!" advert on every world join (EC2 is 26.x-only,
// there is no config switch). It covers the game for players and hangs in front of benchmarks: never let it open.
let arkEc2Screen = null
try { arkEc2Screen = Java.loadClass('dev.corgitaco.enhancedcelestials.client.gui.EC2AnnouncementScreen') } catch (err) { }
if (arkEc2Screen) {
  NativeEvents.onEvent('net.neoforged.neoforge.client.event.ScreenEvent$Opening', e => {
    if (e.getNewScreen() instanceof arkEc2Screen) e.setCanceled(true)
  })
}
