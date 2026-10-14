// Arkhaven alchemy: custom effects + potions (docs/10_RPG_DANGER.md §3).
// Behaviour of marker effects lives in server_scripts/20_alchemy_logic.js.

StartupEvents.registry('mob_effect', event => {
  event.create('arkhaven:quiet').color(0x8fa9c7).beneficial()        // hostiles ignore you until you strike
  event.create('arkhaven:fertility').color(0x6fbf4a).beneficial()    // crops around you grow
  event.create('arkhaven:beast_trust').color(0xd9a35b).beneficial()  // young animals grow faster
  event.create('arkhaven:clean_breath').color(0xbfe7ef).beneficial() // clears smog/acid side effects
  event.create('arkhaven:lead_blood').color(0x5d6470).beneficial()   // slowly removes Mekanism radiation
  event.create('arkhaven:star_sight').color(0xf2d16b).beneficial()   // highlights hostiles nearby
})

StartupEvents.registry('potion', event => {
  const MIN = 1200
  event.create('arkhaven:quiet').effect('arkhaven:quiet', 8 * MIN, 0)
  event.create('arkhaven:sea_wolf')
    .effect('minecraft:luck', 8 * MIN, 1)
    .effect('minecraft:water_breathing', 8 * MIN, 0)
    .effect('minecraft:night_vision', 8 * MIN, 0)
  event.create('arkhaven:fertility').effect('arkhaven:fertility', 5 * MIN, 0)
  event.create('arkhaven:beast_trust').effect('arkhaven:beast_trust', 8 * MIN, 0)
  event.create('arkhaven:forge_heat')
    .effect('minecraft:fire_resistance', 8 * MIN, 0)
    .effect('minecraft:haste', 8 * MIN, 1)
  event.create('arkhaven:clean_breath').effect('arkhaven:clean_breath', 10 * MIN, 0)
  event.create('arkhaven:lead_blood').effect('arkhaven:lead_blood', 3 * MIN, 0)
  event.create('arkhaven:star_sight').effect('arkhaven:star_sight', 5 * MIN, 0)
})
