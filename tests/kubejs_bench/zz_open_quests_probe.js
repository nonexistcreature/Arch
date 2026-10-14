// TEST ONLY (copied into the benchmark client by tools/bench_client.py): opens the quest book ~100 s after login
// so the benchmark screenshot shows chapter titles.
PlayerEvents.loggedIn(e => {
  const name = e.player.username
  e.server.scheduleInTicks(2000, () => e.server.runCommandSilent(`ftbquests open_book ${name}`))
})
