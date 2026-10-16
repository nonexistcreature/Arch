// Arkhaven: a written book with the key layout from client_scripts/07_keybinds.js, given once per layout version.
// Pages are translate components, so each player reads it in their own language (lang: arkhaven.keybook.*).
let ARK_KEYBOOK_VERSION = 2
let ARK_KEYBOOK_PAGES = 11
PlayerEvents.loggedIn(event => {
  let player = event.player
  if ((player.persistentData.arkKeybook || 0) >= ARK_KEYBOOK_VERSION) return
  player.persistentData.arkKeybook = ARK_KEYBOOK_VERSION
  let pages = []
  for (let i = 1; i <= ARK_KEYBOOK_PAGES; i++) pages.push(`'{"translate":"arkhaven.keybook.p${i}"}'`)
  let name = player.username
  event.server.scheduleInTicks(60, () => {
    event.server.runCommandSilent(`give ${name} minecraft:written_book[written_book_content={title:"Arkhaven",author:"Arkhaven",pages:[${pages.join(',')}]},custom_name='{"translate":"arkhaven.keybook.title","color":"gold","italic":false}']`)
    event.server.runCommandSilent(`tellraw ${name} {"translate":"arkhaven.keybook.given","color":"yellow"}`)
  })
})
