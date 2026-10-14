// Arkhaven: full armour set bonuses (docs/10_RPG_DANGER.md §4). Only sets without a native bonus.
// Effects are refreshed every 2 s for 3 s, so they vanish shortly after a piece comes off.
const ARK_SETS = {
  'twilightforest:ironwood':   [['minecraft:regeneration', 0]],
  'twilightforest:steeleaf':   [['minecraft:haste', 0]],
  'twilightforest:knightmetal':[['minecraft:resistance', 0]],
  'twilightforest:arctic':     [['minecraft:speed', 0]],
  'immersiveengineering:armor_steel': [['minecraft:resistance', 0]],
  'mekanismtools:steel':       [['minecraft:resistance', 0]],
  'mekanismtools:osmium':      [['minecraft:haste', 0]],
  'mekanismtools:bronze':      [['minecraft:speed', 0]],
  'mekanismtools:refined_obsidian': [['minecraft:resistance', 1]],
  'mekanismtools:refined_glowstone': [['minecraft:night_vision', 0]],
  'undergarden:cloggrum':      [['minecraft:haste', 0]],
  'undergarden:froststeel':    [['minecraft:fire_resistance', 0]],
  'undergarden:utherium':      [['minecraft:strength', 0]],
  'deeperdarker:resonarium':   [['minecraft:night_vision', 0]],
  'meadow:fur':                [['minecraft:regeneration', 0]],
  'born_in_chaos_v1:dark_metal_armor': [['minecraft:strength', 0]],
}
const ARK_SLOTS = ['head', 'chest', 'legs', 'feet']
const ARK_PIECES = ['helmet', 'chestplate', 'leggings', 'boots']

PlayerEvents.tick(e => {
  const p = e.player
  if (p.age % 40 !== 0) return
  const ids = ARK_SLOTS.map(s => String(p.getItemBySlot(s).id))
  Object.keys(ARK_SETS).forEach(set => {
    if (ARK_PIECES.every((piece, i) => ids[i] === `${set}_${piece}`)) {
      ARK_SETS[set].forEach(([fx, amp]) => p.potionEffects.add(fx, 60, amp, true, false))
    }
  })
})
