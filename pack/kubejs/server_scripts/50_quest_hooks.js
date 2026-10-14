// Arkhaven: quest -> event director hooks (docs/04_QUESTS.md ch.18, docs/03_INTEGRATION.md §7).
// Finishing the "meet the event" quest of the Elements chapter tells arkhaven-core the group is trained for it.
// Quest ids are the generator's stable hex ids (sha1 of "arkhaven:quest:<id>"), see tools/build_quests.py.

const ARK_TRAIN_QUESTS = {
  // filled by tools/build_quests.py -> kubejs/server_scripts/generated/quest_ids.js (ARK_QUEST_IDS)
  el_meteor_meet: 'strike',
  el_rift_meet: 'rift',
  el_shower_meet: 'shower'
}

FTBQuestsEvents.completed(event => {
  const ids = global.ARK_QUEST_IDS || {}
  Object.keys(ARK_TRAIN_QUESTS).forEach(name => {
    if (ids[name] && String(event.object.codeString) === ids[name]) {
      event.server.runCommandSilent(`arkhaven train ${ARK_TRAIN_QUESTS[name]}`)
      event.server.tell(Text.translate('arkhaven.trained', Text.translate(`arkhaven.event.${ARK_TRAIN_QUESTS[name]}`)).gold())
    }
  })
})

// Everyone joins the shared "Arkhaven" FTB team on first login (docs/04_QUESTS.md §2).
PlayerEvents.loggedIn(event => {
  const p = event.player
  if (p.persistentData.arkhavenTeamJoined) return
  const server = event.server
  // The first player creates the party; others are added by the owner command form.
  server.runCommandSilent(`execute as ${p.username} run ftbteams party create Arkhaven`)
  server.runCommandSilent(`ftbteams force-add ${p.username} Arkhaven`)
  p.persistentData.arkhavenTeamJoined = true
})
