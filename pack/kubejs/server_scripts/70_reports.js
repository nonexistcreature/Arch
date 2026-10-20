// Arkhaven: complaint book. Any player types /жалоба <text> (or /report <text>) and it is saved with their name,
// time and position to kubejs/reports.json, so the owner can go through the list later and fix things.
// Ops: /жалобы lists open reports, /жалоба_готово <id> marks one fixed.
const ARK_REPORTS_FILE = 'kubejs/reports.json'
let arkReports = null

function arkReportsLoad() {
  if (arkReports) return arkReports
  arkReports = []
  try {
    let arkRepFile = JsonIO.read(ARK_REPORTS_FILE)
    if (arkRepFile && arkRepFile.reports) arkRepFile.reports.forEach(r => arkReports.push(r))
  } catch (err) {
    console.error('[Arkhaven reports] could not read ' + ARK_REPORTS_FILE + ': ' + err)
  }
  return arkReports
}

function arkReportsSave() {
  JsonIO.write(ARK_REPORTS_FILE, { reports: arkReports })
}

// Rhino here shares one scope across scripts, so locals use `let` and an ark prefix to avoid "redeclaration" errors.
function arkReportAdd(ctx) {
  let arkSrc = ctx.source
  let arkText = String(Java.loadClass('com.mojang.brigadier.arguments.StringArgumentType').getString(ctx, 'text')).trim()
  let arkWho = arkSrc.player ? String(arkSrc.player.username) : String(arkSrc.textName)
  // Logged first, so the text survives in latest.log even if saving fails below.
  console.info(`[Arkhaven reports] incoming from ${arkWho}: ${arkText}`)
  if (arkText.length < 3) {
    arkSrc.sendFailure(Text.of('Опишите проблему хотя бы парой слов.'))
    return 0
  }
  try {
    let arkList = arkReportsLoad()
    let arkId = arkList.reduce((m, r) => Math.max(m, Number(r.id) || 0), 0) + 1
    let arkPos = arkSrc.position
    let arkEntry = {
      id: arkId,
      time: new Date().toISOString(),
      player: arkWho,
      dimension: String(arkSrc.level.dimension),
      x: Math.floor(arkPos.x()), y: Math.floor(arkPos.y()), z: Math.floor(arkPos.z()),
      text: arkText.substring(0, 1000),
      status: 'new'
    }
    arkList.push(arkEntry)
    arkReportsSave()
    console.info(`[Arkhaven reports] #${arkId} from ${arkWho} @ ${arkEntry.x} ${arkEntry.y} ${arkEntry.z}: ${arkEntry.text}`)
    arkSrc.sendSystemMessage(Text.of(`Ваша жалоба #${arkId} была рассмотрена — пошёл нахуй.`).green())
    return 1
  } catch (err) {
    console.error(`[Arkhaven reports] could not save report from ${arkWho} (${arkText}): ${err}`)
    arkSrc.sendFailure(Text.of('Не удалось записать жалобу. Сообщите владельцу сервера.'))
    return 0
  }
}

ServerEvents.commandRegistry(e => {
  const { commands: Commands } = e
  const StringArg = Java.loadClass('com.mojang.brigadier.arguments.StringArgumentType')
  const IntArg = Java.loadClass('com.mojang.brigadier.arguments.IntegerArgumentType')

  for (const name of ['жалоба', 'report']) {
    e.register(Commands.literal(name)
      .executes(ctx => {
        ctx.source.sendSystemMessage(Text.of(`Напишите /${name} и что не так, например: /${name} у базы чёрный туман`).yellow())
        return 1
      })
      .then(Commands.argument('text', StringArg.greedyString()).executes(ctx => arkReportAdd(ctx))))
  }

  e.register(Commands.literal('жалобы').requires(s => s.hasPermission(2)).executes(ctx => {
    let arkOpen = arkReportsLoad().filter(r => r.status !== 'done')
    if (!arkOpen.length) {
      ctx.source.sendSystemMessage(Text.of('Открытых жалоб нет.').green())
      return 1
    }
    ctx.source.sendSystemMessage(Text.of(`Открытых жалоб: ${arkOpen.length}. Последние:`).gold())
    arkOpen.slice(-10).forEach(r => {
      ctx.source.sendSystemMessage(Text.of(`#${r.id} ${r.player} (${r.x} ${r.y} ${r.z}): ${r.text}`))
    })
    return arkOpen.length
  }))

  e.register(Commands.literal('жалоба_готово').requires(s => s.hasPermission(2))
    .then(Commands.argument('id', IntArg.integer(1)).executes(ctx => {
      let arkDoneId = IntArg.getInteger(ctx, "id")
      let arkDone = arkReportsLoad().find(x => Number(x.id) === arkDoneId)
      if (!arkDone) {
        ctx.source.sendFailure(Text.of(`Жалобы #${arkDoneId} нет.`))
        return 0
      }
      arkDone.status = 'done'
      arkReportsSave()
      ctx.source.sendSystemMessage(Text.of(`Жалоба #${arkDoneId} отмечена как исправленная.`).green())
      return 1
    })))
})

// Announcement: online players who have not heard about the complaint book get it when the script loads (/reload),
// and anyone who missed it gets it once on their next login.
function arkReportsAnnounce(player) {
  player.persistentData.arkReportsTold = true
  player.tell(Text.of('[Arkhaven] ').gold().append(Text.of('Появилась жалобная книга! Если что-то сломалось или чего-то не хватает, напишите ').white())
    .append(Text.of('/жалоба <текст>').yellow().clickSuggestCommand('/жалоба '))
    .append(Text.of(' (или /report). Ник и координаты запишутся сами, потом всё разберём и починим.').white()))
}

function arkReportsAnnounceAll(server) {
  if (server) server.playerList.players.forEach(p => { if (!p.persistentData.arkReportsTold) arkReportsAnnounce(p) })
}

PlayerEvents.loggedIn(e => {
  if (!e.player.persistentData.arkReportsTold) e.server.scheduleInTicks(100, () => arkReportsAnnounce(e.player))
})

try {
  arkReportsAnnounceAll(Java.loadClass('net.neoforged.neoforge.server.ServerLifecycleHooks').getCurrentServer())
} catch (err) {
  console.warn('[Arkhaven reports] reload announcement skipped: ' + err)
}
