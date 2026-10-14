// Arkhaven: show the full-set bonus on each armour piece (server logic: server_scripts/45_set_bonuses.js).
const ARK_SET_TIPS = {
  'twilightforest:ironwood': 'regeneration', 'twilightforest:steeleaf': 'haste', 'twilightforest:knightmetal': 'resistance',
  'twilightforest:arctic': 'speed', 'immersiveengineering:armor_steel': 'resistance', 'mekanismtools:steel': 'resistance',
  'mekanismtools:osmium': 'haste', 'mekanismtools:bronze': 'speed', 'mekanismtools:refined_obsidian': 'resistance2',
  'mekanismtools:refined_glowstone': 'night_vision', 'undergarden:cloggrum': 'haste', 'undergarden:froststeel': 'fire_resistance',
  'undergarden:utherium': 'strength', 'deeperdarker:resonarium': 'night_vision', 'meadow:fur': 'regeneration',
  'born_in_chaos_v1:dark_metal_armor': 'strength'
}

ItemEvents.modifyTooltips(e => {
  Object.keys(ARK_SET_TIPS).forEach(set => {
    const pieces = ['helmet', 'chestplate', 'leggings', 'boots'].map(p => `${set}_${p}`)
    e.add(pieces, Text.translate('tooltip.arkhaven.set_bonus', Text.translate(`tooltip.arkhaven.bonus.${ARK_SET_TIPS[set]}`)).color(0x7fc8f8))
  })
})
