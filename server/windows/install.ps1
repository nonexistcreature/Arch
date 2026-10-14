# Arkhaven server on a Windows PC (no Docker). Run once in PowerShell *as administrator*:
#   powershell -ExecutionPolicy Bypass -File install.ps1 -PackUrl https://<user>.github.io/<repo>/pack.toml
# Installs into C:\Arkhaven: Java 21, NeoForge 21.1.259 server, packwiz bootstrap, firewall rules,
# an hourly backup task and a "start at logon" task. Touches nothing else on the PC.
param(
    [Parameter(Mandatory = $true)][string]$PackUrl,
    [string]$Dir = "C:\Arkhaven",
    [string]$Memory = "10G"
)
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
New-Item -ItemType Directory -Force $Dir, "$Dir\server", "$Dir\backups" | Out-Null
Set-Location $Dir

if (-not (Test-Path "$Dir\java\bin\java.exe")) {
    Write-Host "Downloading Java 21..."
    Invoke-WebRequest "https://api.adoptium.net/v3/binary/latest/21/ga/windows/x64/jre/hotspot/normal/eclipse" -OutFile jre.zip
    Expand-Archive jre.zip -DestinationPath java-tmp -Force
    Move-Item (Get-ChildItem java-tmp | Select-Object -First 1).FullName "$Dir\java"
    Remove-Item jre.zip, java-tmp -Recurse -Force
}
$java = "$Dir\java\bin\java.exe"

Set-Location "$Dir\server"
if (-not (Test-Path "libraries\net\neoforged\neoforge\21.1.259")) {
    Write-Host "Installing NeoForge 21.1.259 server..."
    Invoke-WebRequest "https://maven.neoforged.net/releases/net/neoforged/neoforge/21.1.259/neoforge-21.1.259-installer.jar" -OutFile installer.jar
    & $java -jar installer.jar --installServer | Out-Null
    Remove-Item installer.jar, installer.jar.log -ErrorAction SilentlyContinue
}
$pwbs = (Invoke-RestMethod "https://api.github.com/repos/packwiz/packwiz-installer-bootstrap/releases/latest").assets[0].browser_download_url
Invoke-WebRequest $pwbs -OutFile packwiz-installer-bootstrap.jar
"eula=true" | Set-Content eula.txt -Encoding ascii
if (-not (Test-Path server.properties)) {
@"
motd=\u00a76Arkhaven\u00a7r - дом для всех
online-mode=true
white-list=true
enforce-whitelist=true
difficulty=normal
view-distance=10
simulation-distance=6
spawn-protection=0
allow-flight=true
max-tick-time=-1
enable-rcon=false
"@ | Set-Content server.properties -Encoding utf8
}
"-Xms4G -Xmx$Memory -XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200 -XX:+UnlockExperimentalVMOptions -XX:+DisableExplicitGC -XX:G1NewSizePercent=30 -XX:G1MaxNewSizePercent=40 -XX:G1HeapRegionSize=8M -XX:G1ReservePercent=20 -XX:InitiatingHeapOccupancyPercent=15" | Set-Content user_jvm_args.txt -Encoding ascii
$PackUrl | Set-Content "$Dir\pack_url.txt" -Encoding ascii
Copy-Item "$PSScriptRoot\start.cmd", "$PSScriptRoot\backup.ps1", "$PSScriptRoot\LanAnnounce.java" $Dir -Force

Write-Host "Firewall: allowing Minecraft (25565/tcp) and voice chat (24454/udp) on private networks..."
New-NetFirewallRule -DisplayName "Arkhaven Minecraft" -Direction Inbound -Protocol TCP -LocalPort 25565 -Action Allow -Profile Private -ErrorAction SilentlyContinue | Out-Null
New-NetFirewallRule -DisplayName "Arkhaven Voice" -Direction Inbound -Protocol UDP -LocalPort 24454 -Action Allow -Profile Private -ErrorAction SilentlyContinue | Out-Null

Write-Host "Scheduled tasks: hourly backup + start at logon..."
$b = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$Dir\backup.ps1`""
$t = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(30) -RepetitionInterval (New-TimeSpan -Hours 1)
Register-ScheduledTask -TaskName "Arkhaven Backup" -Action $b -Trigger $t -Force | Out-Null
$s = New-ScheduledTaskAction -Execute "$Dir\start.cmd" -WorkingDirectory $Dir
Register-ScheduledTask -TaskName "Arkhaven Server" -Action $s -Trigger (New-ScheduledTaskTrigger -AtLogOn) -Force | Out-Null

Write-Host ""
Write-Host "Done. Start the server now with: $Dir\start.cmd  (it also starts automatically when you log in)."
