// Arkhaven progression gates (owner: «больше челленджа, больше пересечений между занятиями, без гринда»).
// Rule: a top-tier item gets ONE ingredient from another role's branch (or a boss/other-world trophy).
// No new crafting chains: the swapped part is something that branch already makes. Every gate is listed in
// the «Path» quest «Вершины требуют друзей» so players know in advance.

ServerEvents.recipes(event => {
  // Gunsmith table: steel (smelter) + precision mechanism (Create engineer) instead of an iron block.
  // GATE: warrior <- engineer
  event.remove({ id: 'tacz:gun_smith_table' })
  event.shaped('tacz:gun_smith_table', ['LLL', 'SPS', 'S S'], {
    L: '#minecraft:logs', S: '#c:ingots/steel', P: 'create:precision_mechanism'
  }).id('arkhaven:gate/gun_smith_table')

  // ME controller: one precision mechanism instead of one fluix crystal. GATE: AE2 <- Create
  event.remove({ id: 'ae2:network/blocks/controller' })
  event.shaped('ae2:controller', ['aba', 'bcb', 'apa'], {
    a: 'ae2:smooth_sky_stone_block', b: 'ae2:fluix_crystal', c: 'ae2:engineering_processor', p: 'create:precision_mechanism'
  }).id('arkhaven:gate/me_controller')

  // Aircraft engine: aero lubricant (angler's fish oil / oil worker) instead of the top cobblestone.
  // GATE: pilot <- angler / oil
  event.remove({ id: 'immersive_aircraft:engine' })
  event.shaped('immersive_aircraft:engine', [' L ', 'PFP', 'CIC'], {
    L: 'arkhaven:aero_lubricant', P: 'minecraft:piston', F: 'minecraft:blast_furnace', C: 'minecraft:cobblestone', I: 'immersive_aircraft:boiler'
  }).id('arkhaven:gate/aircraft_engine')

  // Reinforced reactor controller: an elite control circuit (Mekanism) instead of the comparator.
  // GATE: Extreme Reactors <- Mekanism
  event.remove({ id: 'bigreactors:reactor/reinforced/controller_ingots_yellorium' })
  event.remove({ id: 'bigreactors:reactor/reinforced/controller_ingots_uranium' })
  event.shaped('bigreactors:reinforced_reactorcontroller', ['CXC', 'YDY', 'CRC'], {
    C: 'bigreactors:reinforced_reactorcasing', X: '#c:circuits/elite', Y: '#c:ingots/yellorium',
    D: '#c:storage_blocks/diamond', R: '#c:dusts/redstone'
  }).id('arkhaven:gate/reinforced_reactor_controller')

  // MEGA 256M cell component: a reinforced echo shard from the Otherside instead of vibrant glass.
  // GATE: engineer <- explorer (Deeper Darker)
  event.remove({ id: 'megacells:cells/cell_component_256m' })
  event.shaped('megacells:cell_component_256m', ['aba', 'cdc', 'aca'], {
    a: 'ae2:matter_ball', b: 'megacells:accumulation_processor', c: 'megacells:cell_component_64m', d: 'deeperdarker:reinforced_echo_shard'
  }).id('arkhaven:gate/cell_component_256m')

  // Fusion reactor controller: a nether star (the Wither) instead of the glass pane. GATE: engineer <- warrior
  event.remove({ id: 'mekanismgenerators:reactor/controller' })
  event.shaped('mekanismgenerators:fusion_reactor_controller', ['CNC', 'FTF', 'FFF'], {
    C: '#c:circuits/ultimate', N: 'minecraft:nether_star', F: 'mekanismgenerators:fusion_reactor_frame', T: 'mekanism:basic_chemical_tank'
  }).id('arkhaven:gate/fusion_controller')
})
