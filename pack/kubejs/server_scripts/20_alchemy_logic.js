// Arkhaven alchemy: effect behaviour + recipes. Recipes are shapeless "alchemy" crafts from a water bottle;
// ingredients come from different roles (docs/10_RPG_DANGER.md §3 table).

const ARK_CLEANSED = ['minecraft:poison', 'minecraft:nausea', 'minecraft:wither', 'minecraft:blindness', 'minecraft:darkness']
const ARK_CROPS = /(crop|wheat|carrots|potatoes|beetroots|sapling|grape|tomato|cabbage|onion|rice|berry|mysticalagriculture|bush)/

// Quiet: hostile mobs can't pick you as a target; striking a mob ends the effect.
NativeEvents.onEvent('net.neoforged.neoforge.event.entity.living.LivingChangeTargetEvent', e => {
  const target = e.getNewAboutToBeSetTarget()
  if (target && target.isPlayer() && target.hasEffect('arkhaven:quiet')) e.setCanceled(true)
})
EntityEvents.afterHurt(e => {
  const src = e.source.player
  if (src && !e.entity.isPlayer() && src.hasEffect('arkhaven:quiet')) src.removeEffect('arkhaven:quiet')
})

PlayerEvents.tick(e => {
  const p = e.player
  if (p.age % 40 !== 0) return
  const level = p.level
  if (p.hasEffect('arkhaven:clean_breath')) ARK_CLEANSED.forEach(id => { if (p.hasEffect(id)) p.removeEffect(id) })
  if (p.hasEffect('arkhaven:lead_blood') && p.age % 200 === 0) p.server.runCommandSilent(`mek radiation reduce 0.25 ${p.username}`)
  if (p.hasEffect('arkhaven:star_sight')) {
    level.getEntitiesWithin(p.boundingBox.inflate(48)).forEach(en => {
      if (en.isLiving() && en.isMonster()) en.potionEffects.add('minecraft:glowing', 60, 0, true, false)
    })
  }
  if (p.hasEffect('arkhaven:fertility')) {
    for (let i = 0; i < 6; i++) {
      const b = level.getBlock(p.x + Math.floor(Math.random() * 13) - 6, p.y + Math.floor(Math.random() * 5) - 2, p.z + Math.floor(Math.random() * 13) - 6)
      if (ARK_CROPS.test(b.id)) {
        b.blockState.randomTick(level, b.pos, level.random)
        level.spawnParticles('minecraft:happy_villager', true, b.x + 0.5, b.y + 0.7, b.z + 0.5, 0.3, 0.3, 0.3, 4, 0)
      }
    }
  }
  if (p.hasEffect('arkhaven:beast_trust')) {
    level.getEntitiesWithin(p.boundingBox.inflate(8)).forEach(en => {
      if (en.isAnimal() && en.isBaby()) en.ageUp(20) // +20 s of growth every 2 s
    })
  }
})

ServerEvents.recipes(event => {
  const potion = id => Item.of('minecraft:potion', `[potion_contents={potion:"${id}"}]`)
  const water = 'minecraft:potion[potion_contents={potion:"minecraft:water"}]'
  const alchemy = (id, ingredients) => event.shapeless(potion(id), [water].concat(ingredients)).id(`arkhaven:alchemy/${id.split(':')[1]}`)
  // HANDSHAKE: gardener (lavender) + breeder (feather) -> everyone
  alchemy('arkhaven:quiet', ['herbalbrews:lavender', 'minecraft:feather', 'minecraft:amethyst_shard'])
  // HANDSHAKE: angler (fish) -> angler
  alchemy('arkhaven:sea_wolf', ['#c:foods/raw_fish', 'minecraft:prismarine_crystals', 'minecraft:glow_ink_sac'])
  // HANDSHAKE: breeder (honey) + cook (compost) -> gardener
  alchemy('arkhaven:fertility', ['minecraft:honey_bottle', 'minecraft:bone_meal', 'farmersdelight:organic_compost'])
  // HANDSHAKE: angler (koi) -> breeder
  alchemy('arkhaven:beast_trust', ['crittersandcompanions:koi_fish', 'minecraft:golden_carrot', 'minecraft:wheat'])
  // HANDSHAKE: explorer (ancient metal from Cataclysm ruins) -> engineer
  alchemy('arkhaven:forge_heat', ['minecraft:blaze_powder', 'cataclysm:ancient_metal_nugget', 'minecraft:magma_cream'])
  // HANDSHAKE: mage (source gem) -> everyone during smog
  alchemy('arkhaven:clean_breath', ['ars_nouveau:source_gem', 'minecraft:moss_block', 'minecraft:kelp'])
  // HANDSHAKE: engineer (lead) + mage (source gem) -> engineer
  alchemy('arkhaven:lead_blood', ['mekanism:ingot_lead', 'ars_nouveau:source_gem', 'minecraft:milk_bucket'])
  // HANDSHAKE: warrior (ender eye) -> explorer
  alchemy('arkhaven:star_sight', ['minecraft:ender_eye', 'minecraft:glowstone_dust', 'minecraft:spyglass'])
})
