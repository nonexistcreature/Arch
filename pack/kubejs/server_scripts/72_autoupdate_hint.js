// Arkhaven: one-time hint for players who still import the .mrpack by hand. The Prism instance from Releases
// updates itself before every launch (packwiz pre-launch), so they never need to download a new .mrpack again.
const ARK_RELEASES_URL = 'https://github.com/nonexistcreature/Arch/releases/latest'

function arkAutoupdateHint(player) {
  player.persistentData.arkAutoupdateTold = true
  player.tell(Text.of('[Arkhaven] ').gold().append(Text.of('Надоело каждый раз качать .mrpack? Импортируй в Prism ').white())
    .append(Text.of('Arkhaven-Prism-Instance.zip').aqua().underlined().clickOpenUrl(ARK_RELEASES_URL))
    .append(Text.of(' (Добавить экземпляр → Импорт). Он сам обновляется перед каждым запуском. Старый экземпляр после этого можно удалить.').white()))
}

PlayerEvents.loggedIn(e => {
  if (!e.player.persistentData.arkAutoupdateTold) e.server.scheduleInTicks(200, () => arkAutoupdateHint(e.player))
})

try {
  let arkHintServer = Java.loadClass('net.neoforged.neoforge.server.ServerLifecycleHooks').getCurrentServer()
  if (arkHintServer) arkHintServer.playerList.players.forEach(p => { if (!p.persistentData.arkAutoupdateTold) arkAutoupdateHint(p) })
} catch (err) {
  console.warn('[Arkhaven autoupdate hint] reload announcement skipped: ' + err)
}
