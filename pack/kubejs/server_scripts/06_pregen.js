// World pre-generation with Chunky, only while nobody is online (owner's request: no lag while exploring).
// Overworld, square of radius ARK_PREGEN_RADIUS around world spawn. Other dimensions generate as usual on visit.
// Every 30 s: nobody online -> start (first time) or continue; someone joined -> pause. Chunky saves progress
// on pause and on shutdown, so the job resumes across restarts until it is done.
const ARK_PREGEN_RADIUS = 2000
const ARK_PREGEN_CHECK_TICKS = 30 * 20
let arkPregenRunning = false

ServerEvents.tick(event => {
  const server = event.server
  if (server.tickCount % ARK_PREGEN_CHECK_TICKS !== 0 || server.tickCount < 60 * 20) return
  try {
    const data = server.persistentData
    if (data.getBoolean('ark_pregen_done')) return
    const online = server.getPlayerCount()
    if (online > 0 && arkPregenRunning) {
      server.runCommandSilent('chunky pause')
      arkPregenRunning = false
      console.info('[Arkhaven] pregen: paused, players online')
    } else if (online === 0 && !arkPregenRunning) {
      if (!data.getBoolean('ark_pregen_started')) {
        server.runCommandSilent('chunky world minecraft:overworld')
        server.runCommandSilent('chunky shape square')
        server.runCommandSilent('chunky spawn')
        server.runCommandSilent('chunky radius ' + ARK_PREGEN_RADIUS)
        server.runCommandSilent('chunky start')
        data.putBoolean('ark_pregen_started', true)
        console.info('[Arkhaven] pregen: started, overworld radius ' + ARK_PREGEN_RADIUS)
      } else {
        server.runCommandSilent('chunky continue')
        console.info('[Arkhaven] pregen: continued, nobody online')
      }
      arkPregenRunning = true
    }
  } catch (err) {
    console.error('[Arkhaven] pregen failed: ' + err)
  }
})

// `/arkpregen done` (op) stops the automation for good, e.g. once Chunky reports the task complete.
ServerEvents.commandRegistry(event => {
  const { commands: Commands } = event
  event.register(Commands.literal('arkpregen').requires(s => s.hasPermission(2))
    .then(Commands.literal('done').executes(ctx => {
      const server = ctx.source.server
      server.persistentData.putBoolean('ark_pregen_done', true)
      server.runCommandSilent('chunky cancel')
      server.runCommandSilent('chunky confirm')
      arkPregenRunning = false
      return 1
    })))
})
