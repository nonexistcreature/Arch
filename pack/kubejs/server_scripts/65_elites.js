// Arkhaven elites (docs/10_RPG_DANGER.md §6): difficulty grows with the place you choose, not with a world level.
// Zone 0-1 (overworld within 1000 blocks of spawn): nothing changes, the world stays calm.
// Beyond 1000 blocks EVERY natural monster is "wild": +100 % health / +50 % damage at 1000 blocks, growing linearly
// to +300 % / +150 % at 4000 blocks (owner: "сильно бафни мобов после 1к блоков"). Danger dimensions count as 2500.
// On top of that, elites: tier 1 (1000-2500 blocks, the Aether), tier 2 (beyond 2500, danger dimensions).
// Elites wear armour (visible on humanoids, never dropped), hit harder, have far more health, and drop extra loot.
// Spawners, eggs, breeding and /summon never make elites (tests call arkMakeElite directly).

const ARK_ELITE = {
  nearRadius: 1000, farRadius: 2500,
  chance: { 1: 0.2, 2: 0.33 },
  // wild buff for every monster past nearRadius: value at nearRadius -> value at wildMaxDist (linear, then flat)
  wild: { health: [1.0, 3.0], damage: [0.5, 1.5], speed: [0.05, 0.15], armor: [2, 8], maxDist: 4000, dimDist: 2500 },
  health: { 1: 1.5, 2: 2.5 },     // +150 % / +250 % max health
  damage: { 1: 0.5, 2: 1.0 },     // +50 % / +100 % attack damage
  speed: { 1: 0.1, 2: 0.15 },
  dangerDims: ['minecraft:the_nether', 'minecraft:the_end', 'twilightforest:twilight_forest', 'undergarden:undergarden', 'deeperdarker:otherside'],
  calmDims: ['aether:the_aether'],
  // big bosses and mini-bosses already have their own fights
  skipNamespaces: ['cataclysm', 'mowziesmobs', 'irons_spellbooks', 'aquamirae'],
  maxBaseHealth: 80
}

/** Distance from world spawn that counts for difficulty: real distance in the overworld, a fixed value in danger
 *  dimensions, 0 elsewhere (the Aether stays light). */
function arkWildDist(level, x, z) {
  const lvl = level.getLevel()
  const dim = String(lvl.dimension)
  if (ARK_ELITE.dangerDims.indexOf(dim) >= 0) return ARK_ELITE.wild.dimDist
  if (dim !== 'minecraft:overworld') return 0
  const s = lvl.getSharedSpawnPos()
  return Math.sqrt((x - s.getX()) * (x - s.getX()) + (z - s.getZ()) * (z - s.getZ()))
}

/** Wild buff for any natural monster past nearRadius; stronger the farther it is. */
function arkMakeWild(mob, dist) {
  const w = ARK_ELITE.wild
  const k = Math.min(1, Math.max(0, (dist - ARK_ELITE.nearRadius) / (w.maxDist - ARK_ELITE.nearRadius)))
  const lerp = r => r[0] + (r[1] - r[0]) * k
  const Attributes = Java.loadClass('net.minecraft.world.entity.ai.attributes.Attributes')
  const AttributeModifier = Java.loadClass('net.minecraft.world.entity.ai.attributes.AttributeModifier')
  const Op = Java.loadClass('net.minecraft.world.entity.ai.attributes.AttributeModifier$Operation')
  const RL = Java.loadClass('net.minecraft.resources.ResourceLocation')
  const add = (attr, amount, name, op) => {
    const inst = mob.getAttribute(attr)
    if (inst && amount > 0) inst.addPermanentModifier(new AttributeModifier(RL.fromNamespaceAndPath('arkhaven', 'wild_' + name), amount, op))
  }
  add(Attributes.MAX_HEALTH, lerp(w.health), 'health', Op.ADD_MULTIPLIED_BASE)
  add(Attributes.ATTACK_DAMAGE, lerp(w.damage), 'damage', Op.ADD_MULTIPLIED_BASE)
  add(Attributes.MOVEMENT_SPEED, lerp(w.speed), 'speed', Op.ADD_MULTIPLIED_BASE)
  add(Attributes.ARMOR, lerp(w.armor), 'armor', Op.ADD_VALUE)
  mob.setHealth(mob.getMaxHealth())
  mob.getPersistentData().putBoolean('ark_wild', true)
}

function arkEliteTier(level, x, z) {
  // level may be a WorldGenRegion (chunk generation): use the real ServerLevel; in KubeJS `dimension` is a property (its id)
  const lvl = level.getLevel()
  const dim = String(lvl.dimension)
  if (ARK_ELITE.dangerDims.indexOf(dim) >= 0) return 2
  if (ARK_ELITE.calmDims.indexOf(dim) >= 0) return 1
  if (dim !== 'minecraft:overworld') return 0
  const s = lvl.getSharedSpawnPos()
  const d = Math.sqrt((x - s.getX()) * (x - s.getX()) + (z - s.getZ()) * (z - s.getZ()))
  return d >= ARK_ELITE.farRadius ? 2 : d >= ARK_ELITE.nearRadius ? 1 : 0
}

/** Turns a freshly spawned monster into an elite of the given tier (1 or 2). */
function arkMakeElite(mob, tier) {
  const Attributes = Java.loadClass('net.minecraft.world.entity.ai.attributes.Attributes')
  const AttributeModifier = Java.loadClass('net.minecraft.world.entity.ai.attributes.AttributeModifier')
  const Op = Java.loadClass('net.minecraft.world.entity.ai.attributes.AttributeModifier$Operation')
  const RL = Java.loadClass('net.minecraft.resources.ResourceLocation')
  const boost = (attr, amount, name) => {
    const inst = mob.getAttribute(attr)
    if (inst && amount > 0) inst.addPermanentModifier(new AttributeModifier(RL.fromNamespaceAndPath('arkhaven', 'elite_' + name), amount, Op.ADD_MULTIPLIED_BASE))
  }
  boost(Attributes.MAX_HEALTH, ARK_ELITE.health[tier], 'health')
  boost(Attributes.ATTACK_DAMAGE, ARK_ELITE.damage[tier], 'damage')
  boost(Attributes.MOVEMENT_SPEED, ARK_ELITE.speed[tier], 'speed')
  mob.setHealth(mob.getMaxHealth())

  // visible armour, never dropped (no free gear farming)
  const Slot = Java.loadClass('net.minecraft.world.entity.EquipmentSlot')
  const head = tier === 2 ? 'minecraft:iron_helmet' : 'minecraft:chainmail_helmet'
  const chest = tier === 2 ? 'minecraft:iron_chestplate' : 'minecraft:chainmail_chestplate'
  if (mob.getItemBySlot(Slot.HEAD).isEmpty()) { mob.setItemSlot(Slot.HEAD, Item.of(head)); mob.setDropChance(Slot.HEAD, 0) }
  if (mob.getItemBySlot(Slot.CHEST).isEmpty()) { mob.setItemSlot(Slot.CHEST, Item.of(chest)); mob.setDropChance(Slot.CHEST, 0) }
  mob.getPersistentData().putInt('ark_elite', tier)
}

/** Registry id of an entity, e.g. "minecraft:spider". */
function arkEntityId(entity) {
  const Reg = Java.loadClass('net.minecraft.core.registries.BuiltInRegistries')
  return String(Reg.ENTITY_TYPE.getKey(entity.getType()))
}

// A scripting mistake here must never take the server down (it did once): log it and spawn the mob normally.
NativeEvents.onEvent('net.neoforged.neoforge.event.entity.living.FinalizeSpawnEvent', e => {
  try { arkOnFinalizeSpawn(e) } catch (err) { console.error('[Arkhaven elites] ' + err) }
})

function arkOnFinalizeSpawn(e) {
  const mob = e.getEntity()
  const Enemy = Java.loadClass('net.minecraft.world.entity.monster.Enemy')
  if (!(mob instanceof Enemy)) return
  const type = String(e.getSpawnType())
  if (['NATURAL', 'CHUNK_GENERATION', 'STRUCTURE', 'PATROL'].indexOf(type) < 0) return
  const id = arkEntityId(mob)
  if (ARK_ELITE.skipNamespaces.indexOf(id.split(':')[0]) >= 0) return
  const Attr = Java.loadClass('net.minecraft.world.entity.ai.attributes.Attributes')
  if (mob.getAttributeBaseValue(Attr.MAX_HEALTH) > ARK_ELITE.maxBaseHealth) return
  const dist = arkWildDist(e.getLevel(), e.getX(), e.getZ())
  if (dist >= ARK_ELITE.nearRadius) arkMakeWild(mob, dist)
  const tier = arkEliteTier(e.getLevel(), e.getX(), e.getZ())
  if (tier === 0) return
  if (Math.random() >= ARK_ELITE.chance[tier]) return
  arkMakeElite(mob, tier)
}

// Extra loot when a player kills an elite: worth the fight, never a farm (natural spawns only).
EntityEvents.death(event => {
  try { arkEliteLoot(event) } catch (err) { console.error('[Arkhaven elites] ' + err) }
})

function arkEliteLoot(event) {
  const mob = event.entity
  if (!mob || mob.isPlayer()) return
  const tier = mob.getPersistentData().getInt('ark_elite')
  if (!tier || !event.source.player) return
  const drop = (id, n) => mob.spawnAtLocation(Item.of(id, n))
  if (Math.random() < 0.6) drop('arkhaven:meteoric_dust', tier)
  if (Math.random() < 0.2) drop('minecraft:emerald', tier)
  if (tier === 2 && Math.random() < 0.1) drop('minecraft:diamond', 1)
  if (tier === 2 && Math.random() < 0.05) drop('arkhaven:rift_shard', 1)
  const Orb = Java.loadClass('net.minecraft.world.entity.ExperienceOrb')
  mob.level.addFreshEntity(new Orb(mob.level, mob.x, mob.y, mob.z, 10 * tier))
}
