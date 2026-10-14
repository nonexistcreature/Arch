// Arkhaven: world rules. Calm by default; danger is opt-in (docs/10_RPG_DANGER.md §6).
ServerEvents.loaded(event => {
  const server = event.server
  // Creeper explosions never break blocks: handled by arkhaven-core (config zones.creepersKeepBlocks).
  server.runCommandSilent('gamerule doInsomnia false')       // no phantoms
  server.runCommandSilent('gamerule playersSleepingPercentage 50')
  server.runCommandSilent('gamerule keepInventory false')    // gravestones handle deaths
  server.runCommandSilent('difficulty normal')
})
