// .mrpack imports (Prism, Modrinth App, TLauncher...) can't carry JVM memory settings: launchers default to 2-4 GB,
// which on 300+ mods means constant garbage collection = 0.5-1 s freezes every few seconds (bench: 5 GB heap -> 2-70 FPS).
// KubeJS's class filter hides java.lang.Runtime, but Minecraft's own SystemReport prints "Memory: ... up to N bytes (M MiB)".
// Read once while the game loads; tell the player once per session if the heap is too small.
let arkMemMb = -1
try {
  let arkReport = '' + new (Java.loadClass('net.minecraft.SystemReport'))().toLineSeparatedString()
  let arkMemMatch = arkReport.match(/up to \d+ bytes \((\d+) MiB\)/)
  if (arkMemMatch) arkMemMb = parseInt(arkMemMatch[1])
} catch (err) { }
console.info('ARK_MEM max heap ' + arkMemMb + ' MB')
let arkMemWarned = false
let arkMemTicks = 0
ClientEvents.tick(e => {
  if (arkMemWarned || arkMemMb < 0 || arkMemMb >= 5800 || !Client.player) return
  if (++arkMemTicks < 200) return
  arkMemWarned = true
  Client.player.tell(Text.translate('arkhaven.memory.low', String(arkMemMb)).gold())
  Client.player.tell(Text.translate('arkhaven.memory.how').yellow())
})
