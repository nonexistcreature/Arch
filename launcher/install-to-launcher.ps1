# Arkhaven for players who keep their own launcher (official Minecraft Launcher or any launcher that uses a
# standard .minecraft folder). Installs NeoForge 21.1.259 into the launcher's .minecraft, downloads the modpack
# (mods, configs, quests, shaders, resource packs) into a SEPARATE game folder so your other worlds/mods are untouched,
# and adds an "Arkhaven" profile to the official launcher. Re-run (or use "Arkhaven — обновить") to update.
#   powershell -ExecutionPolicy Bypass -File install-to-launcher.ps1 [-McDir <.minecraft>] [-GameDir <folder>]
param(
    [string]$McDir = "$env:APPDATA\.minecraft",
    [string]$GameDir = "$env:APPDATA\.arkhaven",
    [string]$PackUrl = "https://nonexistcreature.github.io/Arch/pack.toml",
    [string]$NetworkUrl = "https://nonexistcreature.github.io/Arch/network.json",
    [string]$NeoForge = "21.1.259",
    [switch]$UpdateOnly,
    [switch]$NoShortcut   # tests: no desktop shortcut, no ZeroTier
)
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
$Tools = "$env:LOCALAPPDATA\Arkhaven-Tools"
New-Item -ItemType Directory -Force $Tools, $GameDir, $McDir | Out-Null
function Write-Utf8([string]$Path, [string]$Text) { [IO.File]::WriteAllText($Path, $Text, (New-Object Text.UTF8Encoding $false)) }

# 1) Java 21 (own copy, the system is not touched)
$java = "$Tools\java\bin\java.exe"
if (-not (Test-Path $java)) {
    Write-Host "Скачиваю Java 21..."
    Invoke-WebRequest "https://api.adoptium.net/v3/binary/latest/21/ga/windows/x64/jre/hotspot/normal/eclipse" -OutFile "$Tools\jre.zip"
    Expand-Archive "$Tools\jre.zip" -DestinationPath "$Tools\jre-tmp" -Force
    Move-Item (Get-ChildItem "$Tools\jre-tmp" | Select-Object -First 1).FullName "$Tools\java"
    Remove-Item "$Tools\jre.zip", "$Tools\jre-tmp" -Recurse -Force
}

# 2) NeoForge into the launcher's .minecraft (the installer adds a "NeoForge" profile to launcher_profiles.json)
$ver = "neoforge-$NeoForge"
if (-not $UpdateOnly -and -not (Test-Path "$McDir\versions\$ver\$ver.json")) {
    Write-Host "Ставлю NeoForge $NeoForge..."
    $lp = "$McDir\launcher_profiles.json"
    if (-not (Test-Path $lp)) { Write-Utf8 $lp '{"profiles":{},"settings":{},"version":3}' }
    Invoke-WebRequest "https://maven.neoforged.net/releases/net/neoforged/neoforge/$NeoForge/neoforge-$NeoForge-installer.jar" -OutFile "$Tools\neoforge-installer.jar"
    & $java -jar "$Tools\neoforge-installer.jar" --install-client "$McDir" | Out-Null
    if (-not (Test-Path "$McDir\versions\$ver\$ver.json")) { throw "NeoForge не установился (подробности: $Tools\neoforge-installer.jar.log)" }
    $freshNeo = $true
}

# 3) The modpack into the separate game folder (packwiz keeps it in sync with the server)
$pwbs = "$GameDir\packwiz-installer-bootstrap.jar"
if (-not (Test-Path $pwbs)) {
    $u = (Invoke-RestMethod "https://api.github.com/repos/packwiz/packwiz-installer-bootstrap/releases/latest").assets[0].browser_download_url
    Invoke-WebRequest $u -OutFile $pwbs
}
Write-Host "Скачиваю/обновляю сборку (первый раз 5–15 минут)..."
Push-Location $GameDir
& $java -jar $pwbs -s client $PackUrl
Pop-Location

# 4) "Arkhaven" profile in the official launcher: NeoForge version + separate game folder + memory
if (-not $UpdateOnly) {
    $lp = "$McDir\launcher_profiles.json"
    Copy-Item $lp "$lp.arkhaven-backup" -Force
    $j = Get-Content $lp -Raw | ConvertFrom-Json
    $ramMb = [int]((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1MB)
    $mem = [Math]::Max(6144, [Math]::Min(12288, [int]($ramMb / 2)))
    $p = [ordered]@{
        name = "Arkhaven"; type = "custom"; lastVersionId = $ver; gameDir = $GameDir; icon = "Grass"
        javaArgs = "-Xmx$($mem)M -Xms4G -XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=50 -XX:+UnlockExperimentalVMOptions -XX:+DisableExplicitGC -XX:G1NewSizePercent=30 -XX:G1MaxNewSizePercent=40 -XX:G1HeapRegionSize=16M"
        lastUsed = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.fffZ"); created = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
    }
    if ($freshNeo -and $j.profiles.NeoForge -and $j.profiles.NeoForge.lastVersionId -eq $ver) { $j.profiles.PSObject.Properties.Remove("NeoForge") }  # ours replaces the installer's
    $j.profiles | Add-Member -NotePropertyName "arkhaven" -NotePropertyValue ([pscustomobject]$p) -Force
    Write-Utf8 $lp ($j | ConvertTo-Json -Depth 20)

    # update shortcut: re-downloads changes and refreshes the server address before you start the game
    Copy-Item $PSCommandPath "$GameDir\install-to-launcher.ps1" -Force
    if (Test-Path "$PSScriptRoot\Discover.jar") { Copy-Item "$PSScriptRoot\Discover.jar" "$GameDir\Discover.jar" -Force }
    Write-Utf8 "$GameDir\update.cmd" "@echo off`r`npowershell -NoProfile -ExecutionPolicy Bypass -File `"%~dp0install-to-launcher.ps1`" -UpdateOnly -McDir `"$McDir`" -GameDir `"$GameDir`"`r`n"
    if (-not $NoShortcut) {
        $ws = New-Object -ComObject WScript.Shell
        $lnk = $ws.CreateShortcut("$([Environment]::GetFolderPath('Desktop'))\Arkhaven — обновить.lnk")
        $lnk.TargetPath = "$GameDir\update.cmd"; $lnk.WorkingDirectory = $GameDir; $lnk.Save()
        # ZeroTier for friends outside the owner's home network (skipped silently if the owner hasn't set it up)
        if (Test-Path "$PSScriptRoot\zerotier-join.ps1") {
            Copy-Item "$PSScriptRoot\zerotier-join.ps1" "$GameDir\zerotier-join.ps1" -Force
            & "$PSScriptRoot\zerotier-join.ps1" -NetworkUrl $NetworkUrl
        }
    }
}

# 5) server address: LAN announcement first (or a server on this PC), otherwise the ZeroTier address from the pack
if (Test-Path "$GameDir\Discover.jar") { & $java -jar "$GameDir\Discover.jar" $GameDir | Out-Host }

Write-Host ""
Write-Host "Готово. В лаунчере выбери профиль/версию «Arkhaven» ($ver) и нажми «Играть»."
Write-Host "Другой лаунчер: версия $ver, папка игры $GameDir. Обновления — ярлык «Arkhaven — обновить»."
