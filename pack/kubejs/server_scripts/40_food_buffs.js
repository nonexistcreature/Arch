// Arkhaven: dishes with role buffs (docs/03_INTEGRATION.md §4.8). Cooks feed miners, warriors and mages.
// Effects stack by type: eating the same dish again only refreshes its timer.
// HANDSHAKE: cook -> miner/engineer (haste), warrior (resistance), mage (mana), explorer (luck)

const ARK_MIN = 1200
const ARK_DISHES = {
  'farmersdelight:shepherds_pie':        [['minecraft:haste', 5, 1]],                                 // "miner's pie"
  'farmersdelight:steak_and_potatoes':   [['minecraft:strength', 5, 0]],
  'farmersdelight:beef_stew':            [['minecraft:resistance', 5, 0], ['minecraft:fire_resistance', 5, 0]], // "brave stew"
  'farmersdelight:fish_stew':            [['minecraft:water_breathing', 8, 0]],
  'farmersdelight:baked_cod_stew':       [['minecraft:dolphins_grace', 3, 0]],
  'farmersdelight:pasta_with_meatballs': [['minecraft:health_boost', 10, 0]],
  'farmersdelight:mushroom_rice':        [['minecraft:night_vision', 8, 0]],
  'farmersdelight:squid_ink_pasta':      [['minecraft:night_vision', 8, 0], ['minecraft:water_breathing', 4, 0]],
  'brewinandchewin:quiche_slice':        [['minecraft:absorption', 3, 1]],
  'brewinandchewin:fiery_fondue':        [['minecraft:fire_resistance', 8, 0]],
  'mynethersdelight:spicy_curry':        [['minecraft:fire_resistance', 10, 0], ['minecraft:speed', 3, 0]],
  'ends_delight:dragon_meat_stew':       [['minecraft:resistance', 8, 1], ['minecraft:regeneration', 1, 1]],
  'farm_and_charm:farmers_breakfast':    [['minecraft:speed', 5, 0], ['minecraft:haste', 5, 0]],
  'meadow:cheese_tart_slice':            [['minecraft:regeneration', 1, 0]],
  'oceansdelight:fugu_roll':             [['minecraft:luck', 10, 0]],
  'herbalbrews:green_tea':               [['irons_spellbooks:instant_mana', 0.05, 1]],              // focus tea for mages
  'arkhaven:star_carp':                  [['minecraft:luck', 20, 0], ['arkhaven:star_sight', 2, 0]] // "dinner under the stars"
}

ItemEvents.foodEaten(e => {
  const fx = ARK_DISHES[e.item.id]
  if (!fx) return
  fx.forEach(([id, minutes, amp]) => e.player.potionEffects.add(id, Math.max(1, Math.round(minutes * ARK_MIN)), amp, false, true))
})
