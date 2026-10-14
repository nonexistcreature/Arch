// Arkhaven handshakes (docs/03_INTEGRATION.md §4). Every `// HANDSHAKE:` line is collected by tools/handshake_report.py.
// Rule: main recipe needs two roles; a solo route exists but costs ~3x.

ServerEvents.recipes(event => {
  const mixing = (out, ins, heat, id) => event.custom({ type: 'create:mixing', heat_requirement: heat || 'none', ingredients: ins, results: [out] }).id(id)
  const imbue = (input, out, pedestals, source, id) => event.custom({ type: 'ars_nouveau:imbuement', input: input, output: out, pedestalItems: pedestals, source: source }).id(id)
  const filling = (input, fluid, mb, out, id) => event.custom({ type: 'create:filling', ingredients: [input, { type: 'fluid_stack', fluid: fluid, amount: mb }], results: [out] }).id(id)

  // --- 1. Levitite: renewable mage route (natural source stays). HANDSHAKE: mage -> engineer/builder
  imbue({ item: 'minecraft:calcite' }, { id: 'aeronautics:levitite', count: 2 },
    [{ item: 'ars_nouveau:source_gem' }, { item: 'minecraft:phantom_membrane' }, { item: 'minecraft:feather' }], 800, 'arkhaven:handshake/levitite_imbuement')

  // --- 2. Waxed canvas. HANDSHAKE: breeder (bee wax) -> engineer (envelopes); solo tech: plastic
  event.shapeless('2x arkhaven:waxed_canvas', ['#minecraft:wool', '#minecraft:wool', 'productivebees:wax', 'productivebees:wax']).id('arkhaven:handshake/waxed_canvas_wax')
  event.shapeless('2x arkhaven:waxed_canvas', ['meadow:linen', 'meadow:linen', 'productivebees:wax']).id('arkhaven:handshake/waxed_canvas_linen')
  event.shapeless('arkhaven:waxed_canvas', ['#minecraft:wool', '#minecraft:wool', 'mekanism:hdpe_sheet', 'mekanism:hdpe_sheet']).id('arkhaven:handshake/waxed_canvas_plastic_solo')
  event.shaped('12x aeronautics:white_envelope', ['CS', 'SC'], { C: 'arkhaven:waxed_canvas', S: 'minecraft:stick' }).id('arkhaven:handshake/envelope_from_canvas')

  // --- 3. Aero lubricant. HANDSHAKE: angler (fish oil) -> engineer; solo: TFMG/IE lubricant
  mixing({ id: 'arkhaven:aero_lubricant', count: 2 }, [{ tag: 'c:foods/raw_fish' }, { tag: 'c:foods/raw_fish' }, { tag: 'c:foods/raw_fish' }, { item: 'minecraft:glass_bottle' }, { item: 'minecraft:glass_bottle' }], 'heated', 'arkhaven:handshake/aero_lubricant_fish')
  filling({ item: 'minecraft:glass_bottle' }, 'tfmg:lubrication_oil', 250, { id: 'arkhaven:aero_lubricant' }, 'arkhaven:handshake/aero_lubricant_tfmg')
  filling({ item: 'minecraft:glass_bottle' }, 'immersivepetroleum:lubricant', 250, { id: 'arkhaven:aero_lubricant' }, 'arkhaven:handshake/aero_lubricant_ip')
  // Engines (Aeronautics mid tier) need lubricant: 3 loops instead of 8, but each loop deploys one lubricant.
  const inc = 'simulated:incomplete_engine_assembly'
  event.remove({ id: 'simulated:sequenced_assembly/engine_assembly' })
  event.custom({
    type: 'create:sequenced_assembly', ingredient: { tag: 'c:plates/iron' }, loops: 3,
    transitional_item: { id: inc },
    results: [{ chance: 50.0, id: 'simulated:engine_assembly' }, { chance: 16.0, id: 'create:iron_sheet' }, { chance: 15.0, id: 'minecraft:iron_nugget' },
      { chance: 10.0, id: 'create:industrial_iron_block' }, { chance: 8.0, id: 'minecraft:iron_bars' }],
    sequence: [
      { type: 'create:cutting', ingredients: [{ item: inc }], results: [{ id: inc }] },
      { type: 'create:deploying', ingredients: [{ item: inc }, { item: 'arkhaven:aero_lubricant' }], results: [{ id: inc }] },
      { type: 'create:pressing', ingredients: [{ item: inc }], results: [{ id: inc }] }
    ]
  }).id('arkhaven:handshake/engine_assembly_lubricated')

  // --- 4. Dragon plating. HANDSHAKE: breeder (crocodile scutes) -> engineer/warrior; solo tech: reinforced alloy x3
  event.shaped('2x arkhaven:dragon_plating', ['SCS', 'C C', 'SCS'], { S: '#c:ingots/steel', C: 'alexsmobs:crocodile_scute' }).id('arkhaven:handshake/dragon_plating')
  event.shaped('arkhaven:dragon_plating', ['SAS', 'A A', 'SAS'], { S: '#c:ingots/steel', A: 'mekanism:alloy_reinforced' }).id('arkhaven:handshake/dragon_plating_solo')
  event.shaped('dmr:dragon_armor', ['P P', 'PPP', 'P P'], { P: 'arkhaven:dragon_plating' }).id('arkhaven:handshake/dragon_armor_plating')

  // --- 5. Ward crystals (fuel for the arkhaven-core Ward Generator). HANDSHAKE: explorer (meteoric dust) + engineer/mage
  mixing({ id: 'arkhaven:ward_crystal_t1', count: 2 }, [{ item: 'minecraft:amethyst_shard' }, { item: 'minecraft:amethyst_shard' }, { item: 'arkhaven:meteoric_dust' }], 'heated', 'arkhaven:handshake/ward_t1_create')
  imbue({ item: 'minecraft:amethyst_shard' }, { id: 'arkhaven:ward_crystal_t1' }, [{ item: 'arkhaven:meteoric_dust' }], 300, 'arkhaven:handshake/ward_t1_ars')
  event.shapeless('arkhaven:ward_crystal_t2', ['arkhaven:ward_crystal_t1', 'ars_nouveau:source_gem', 'mekanism:alloy_infused']).id('arkhaven:handshake/ward_t2_tech_magic')
  event.shapeless('arkhaven:ward_crystal_t2', ['arkhaven:ward_crystal_t1', 'mekanism:alloy_infused', 'mekanism:alloy_infused', 'mekanism:alloy_reinforced']).id('arkhaven:handshake/ward_t2_tech_solo')
  event.shapeless('arkhaven:ward_crystal_t2', ['arkhaven:ward_crystal_t1', 'ars_nouveau:source_gem_block', 'ars_nouveau:source_gem', 'ars_nouveau:source_gem']).id('arkhaven:handshake/ward_t2_magic_solo')
  event.shapeless('arkhaven:ward_crystal_t3', ['arkhaven:ward_crystal_t2', 'arkhaven:ward_crystal_t2', 'arkhaven:exotic_matter']).id('arkhaven:handshake/ward_t3')

  // --- 10. Meteoric iron. HANDSHAKE: explorer -> everyone
  event.shapeless('arkhaven:meteoric_iron_ingot', ['arkhaven:meteoric_dust', 'arkhaven:meteoric_dust', 'arkhaven:meteoric_dust', 'arkhaven:meteoric_dust', 'minecraft:iron_ingot']).id('arkhaven:handshake/meteoric_iron')
  mixing({ id: 'arkhaven:meteoric_iron_ingot', count: 2 }, [{ item: 'arkhaven:meteoric_dust' }, { item: 'arkhaven:meteoric_dust' }, { item: 'arkhaven:meteoric_dust' }, { item: 'minecraft:iron_ingot' }, { item: 'minecraft:iron_ingot' }], 'superheated', 'arkhaven:handshake/meteoric_iron_create')

  // --- Exotic matter. Final route is the Ring Collider (MMR); this interim recipe keeps the chain completable.
  event.shaped('arkhaven:exotic_matter', ['AWA', 'NSN', 'AWA'], {
    A: 'mekanism:pellet_antimatter', W: 'arkhaven:ward_crystal_t2', N: 'minecraft:nether_star', S: 'ars_nouveau:source_gem_block'
  }).id('arkhaven:handshake/exotic_matter_interim')

  // --- Citadel heart: everyone contributes. HANDSHAKE: engineer + mage + breeder + builder
  event.shaped('arkhaven:citadel_heart', ['LCL', 'DWD', 'LGL'], {
    L: 'aeronautics:pearlescent_levitite', C: 'arkhaven:waxed_canvas', D: 'arkhaven:dragon_plating',
    W: 'arkhaven:ward_crystal_t2', G: 'ars_nouveau:source_gem_block'
  }).id('arkhaven:handshake/citadel_heart')

  // --- Traveler's charm (also a chapter 0a reward)
  event.shaped('arkhaven:travelers_charm', [' S ', 'LEL', ' F '], { S: 'minecraft:string', L: 'herbalbrews:lavender', E: 'minecraft:emerald', F: 'minecraft:feather' }).id('arkhaven:travelers_charm')

  // --- Mekanism bio-fuel from kitchen waste. HANDSHAKE: gardener/cook -> engineer (built-in, shown in EMI)
})
