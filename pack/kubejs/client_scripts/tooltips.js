// Arkhaven tooltips: handshake hints ("Valued by …") and custom item explanations.
const ARK_VALUED = {
  'arkhaven:waxed_canvas': 'engineer', 'arkhaven:aero_lubricant': 'engineer', 'arkhaven:dragon_plating': 'warrior',
  'arkhaven:meteoric_iron_ingot': 'everyone', 'arkhaven:meteoric_dust': 'engineer_mage',
  'productivebees:wax': 'engineer', 'alexsmobs:crocodile_scute': 'warrior', 'aeronautics:levitite': 'builder',
  'herbalbrews:lavender': 'alchemist', 'crittersandcompanions:koi_fish': 'alchemist', 'ars_nouveau:source_gem': 'alchemist',
  'mekanism:ingot_lead': 'alchemist', 'farmersdelight:organic_compost': 'alchemist', 'cataclysm:ancient_metal_nugget': 'alchemist'
}

ItemEvents.modifyTooltips(e => {
  Object.keys(ARK_VALUED).forEach(id => {
    e.add(id, Text.translate('tooltip.arkhaven.valued_by', Text.translate(`role.arkhaven.${ARK_VALUED[id]}`)).color(0xd9b45b))
  })
  e.add('arkhaven:travelers_charm', Text.translate('tooltip.arkhaven.travelers_charm').gray())
  e.add(['arkhaven:ward_crystal_t1', 'arkhaven:ward_crystal_t2', 'arkhaven:ward_crystal_t3'], Text.translate('tooltip.arkhaven.ward_crystal').gray())
  e.add('arkhaven:star_carp', Text.translate('tooltip.arkhaven.star_carp').gray())
})
