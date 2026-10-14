// Traveler's Charm: while carried, hostile mobs only start chasing you from half their usual range.
NativeEvents.onEvent('net.neoforged.neoforge.event.entity.living.LivingChangeTargetEvent', e => {
  const target = e.getNewAboutToBeSetTarget()
  if (!target || !target.isPlayer()) return
  if (!target.inventory.contains('arkhaven:travelers_charm')) return
  const mob = e.getEntity()
  const range = mob.getAttributeValue('minecraft:generic.follow_range')
  if (mob.distanceToEntity(target) > range / 2) e.setCanceled(true)
})
