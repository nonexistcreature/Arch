// Arkhaven custom items (handshake materials, docs/03_INTEGRATION.md §4). Textures: tools/make_textures.py.

StartupEvents.registry('item', event => {
  event.create('arkhaven:waxed_canvas')          // HANDSHAKE 2: breeder wax / engineer plastic -> airship envelopes
  event.create('arkhaven:aero_lubricant')        // HANDSHAKE 3: angler fish oil / engineer lubricant -> propellers & engines
  event.create('arkhaven:dragon_plating')        // HANDSHAKE 4: breeder dragon / tech alloy -> warship armour
  event.create('arkhaven:ward_crystal_t1').glow(false)   // HANDSHAKE 5: ward generator fuel
  event.create('arkhaven:ward_crystal_t2').rarity('uncommon')
  event.create('arkhaven:ward_crystal_t3').rarity('rare').glow(true)
  event.create('arkhaven:meteoric_dust')         // from meteor craters (arkhaven-core events)
  event.create('arkhaven:meteoric_iron_ingot').rarity('uncommon')  // HANDSHAKE 10: explorer -> everyone
  event.create('arkhaven:exotic_matter').rarity('epic').glow(true) // Ring Collider output
  event.create('arkhaven:citadel_heart').rarity('epic').maxStackSize(1)
  event.create('arkhaven:star_carp').rarity('rare')                // HANDSHAKE 9: angler during meteor showers
    .food(food => food.nutrition(6).saturation(1.2).effect('minecraft:luck', 6000, 0, 1.0))
  event.create('arkhaven:travelers_charm').maxStackSize(1).rarity('uncommon') // halves hostile aggro range
})
