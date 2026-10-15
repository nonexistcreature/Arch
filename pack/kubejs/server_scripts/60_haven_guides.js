// Arkhaven: guides of the Haven (docs/04_QUESTS.md §6). Placed once around world spawn on first server start
// (or by an op with /arkhaven_haven). Right-click a guide: a short line in the player's language + a button
// that opens the quest book. Texts live in kubejs/assets/arkhaven/lang (arkhaven.guide.<id>.*).
const ARK_GUIDES = [
  { id: 'keeper', model: 'easy_npc:humanoid', item: 'minecraft:compass' },
  { id: 'marta', model: 'easy_npc:humanoid_slim', item: 'farmersdelight:cooking_pot' },
  { id: 'luka', model: 'easy_npc:humanoid', item: 'minecraft:iron_hoe' },
  { id: 'vera', model: 'easy_npc:humanoid_slim', item: 'tide:fishing_journal' },
  { id: 'gustav', model: 'easy_npc:humanoid', item: 'create:wrench' },
  { id: 'iris', model: 'easy_npc:humanoid_slim', item: 'ars_nouveau:novice_spell_book' },
  { id: 'dan', model: 'easy_npc:humanoid', item: 'minecraft:iron_sword' },
  { id: 'ada', model: 'easy_npc:humanoid_slim', item: 'minecolonies:blockhuttownhall' }
]

function arkPlaceGuides(server) {
  const level = server.overworld()
  const spawn = level.sharedSpawnPos
  level.getChunk(spawn.x >> 4, spawn.z >> 4)
  ARK_GUIDES.forEach((g, i) => {
    const a = (Math.PI * 2 * i) / ARK_GUIDES.length
    const x = Math.floor(spawn.x + Math.cos(a) * 7) + 0.5
    const z = Math.floor(spawn.z + Math.sin(a) * 7) + 0.5
    level.getChunk(Math.floor(x) >> 4, Math.floor(z) >> 4) // make sure the chunk is generated before reading its height
    const y = level.getHeight('motion_blocking_no_leaves', Math.floor(x), Math.floor(z))
    const yaw = (Math.atan2(spawn.z - z, spawn.x - x) * 180) / Math.PI - 90
    server.runCommandSilent(`kill @e[tag=ark_guide_${g.id}]`)
    server.runCommandSilent(
      `summon ${g.model} ${x} ${y} ${z} {Tags:["ark_guide","ark_guide_${g.id}"],NoAI:1b,Invulnerable:1b,PersistenceRequired:1b,Silent:1b,` +
      `Rotation:[${yaw.toFixed(1)}f,0f],CustomNameVisible:1b,CustomName:'{"translate":"arkhaven.guide.${g.id}.name","color":"gold"}',` +
      `HandItems:[{id:"${g.item}",count:1},{}]}`)
  })
  server.persistentData.arkHavenBuilt = true
  console.info(`Haven guides placed around ${spawn.x} ${spawn.y} ${spawn.z}`)
}

ServerEvents.loaded(e => {
  if (e.server.persistentData.arkHavenBuilt) return
  e.server.scheduleInTicks(200, () => arkPlaceGuides(e.server))
})

ServerEvents.commandRegistry(e => {
  const { commands: Commands } = e
  e.register(Commands.literal('arkhaven_haven').requires(s => s.hasPermission(2)).executes(ctx => {
    arkPlaceGuides(ctx.source.server)
    return 1
  }))
})

// Right-click goes through NeoForge's player interaction events directly: Easy NPC can consume the click in
// interactAt before KubeJS's ItemEvents.entityInteracted fires, so we listen to both events, cancel them so the
// NPC's own editor/dialog does not open, and answer once per click (both events and both hands fire).
const arkGuideLastTalk = {}

function arkGuideInteract(e) {
  if (e.level.isClientSide()) return
  let target = e.target
  if (!target || !target.tags || !target.tags.contains('ark_guide')) return
  let g = ARK_GUIDES.find(x => target.tags.contains(`ark_guide_${x.id}`))
  if (!g) return
  e.setCanceled(true)
  e.setCancellationResult(Java.loadClass('net.minecraft.world.InteractionResult').SUCCESS)
  let p = e.entity
  let key = String(p.uuid)
  let now = e.level.gameTime
  if (arkGuideLastTalk[key] !== undefined && now - arkGuideLastTalk[key] < 10) return
  arkGuideLastTalk[key] = now
  p.tell(Text.translate(`arkhaven.guide.${g.id}.name`).gold().append(Text.of(': ').white()).append(Text.translate(`arkhaven.guide.${g.id}.line`).white()))
  p.tell(Text.translate('arkhaven.guide.open_book').green().underlined().clickRunCommand(`/ftbquests open_book`))
  console.info(`[Arkhaven] guide ${g.id} talked to ${p.username}`)
}

NativeEvents.onEvent('net.neoforged.neoforge.event.entity.player.PlayerInteractEvent$EntityInteractSpecific', e => {
  try { arkGuideInteract(e) } catch (err) { console.error('[Arkhaven guides] ' + err) }
})
NativeEvents.onEvent('net.neoforged.neoforge.event.entity.player.PlayerInteractEvent$EntityInteract', e => {
  try { arkGuideInteract(e) } catch (err) { console.error('[Arkhaven guides] ' + err) }
})
