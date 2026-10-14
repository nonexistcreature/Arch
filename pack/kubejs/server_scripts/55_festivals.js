// Arkhaven: seasonal festivals (docs/03_INTEGRATION.md §9). When Serene Seasons switches season,
// everyone online gets a title + chat note pointing to the Festivals chapter and a small festive gift.
const ARK_FEST = {
  SPRING: { key: 'spring', gift: 'minecraft:bone_meal', n: 16 },
  SUMMER: { key: 'summer', gift: 'farmersdelight:melon_popsicle', n: 2 },
  AUTUMN: { key: 'autumn', gift: 'minecraft:pumpkin_pie', n: 2 },
  WINTER: { key: 'winter', gift: 'minecraft:firework_rocket', n: 8 }
}
let arkSeasonHelper = null
try { arkSeasonHelper = Java.loadClass('sereneseasons.api.season.SeasonHelper') } catch (err) { console.warn('Serene Seasons API not available: ' + err) }

ServerEvents.tick(e => {
  if (!arkSeasonHelper || e.server.tickCount % 200 !== 0) return
  const level = e.server.overworld()
  const season = String(arkSeasonHelper.getSeasonState(level).getSeason())
  const data = e.server.persistentData
  if (data.arkSeason === season) return
  const first = !data.arkSeason
  data.arkSeason = season
  const f = ARK_FEST[season]
  if (!f || first) return // don't celebrate on the very first check after world creation
  e.server.players.forEach(p => {
    p.server.runCommandSilent(`title ${p.username} title {"translate":"arkhaven.festival.${f.key}.title","color":"gold"}`)
    p.tell(Text.translate(`arkhaven.festival.${f.key}.chat`).gold())
    p.give(Item.of(f.gift, f.n))
  })
})
