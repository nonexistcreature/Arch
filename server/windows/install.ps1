# Arkhaven server on a Windows PC (no Docker). Run once in PowerShell *as administrator*:
#   powershell -ExecutionPolicy Bypass -File install.ps1 [-PackUrl <url>] [-Memory 10G] [-NoZeroTier]
# (or just double-click "Arkhaven-Server-Setup.cmd", which does exactly this)
# Installs into C:\Arkhaven: Java 21, NeoForge 21.1.259 server, packwiz bootstrap, firewall rules,
# an hourly backup task and a "start at logon" task, hosts the friends' ZeroTier network, makes the
# owner (found in the local launcher accounts) an operator and starts the server. Touches nothing else on the PC.
param(
    [string]$PackUrl = "",
    [string]$Dir = "C:\Arkhaven",
    [string]$Memory = "10G",
    [switch]$NoZeroTier,
    [switch]$NoStart
)
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
function Write-Utf8([string]$Path) { [IO.File]::WriteAllText($Path, ($input | Out-String), (New-Object Text.UTF8Encoding $false)) }  # no BOM: Java reads it as text
if (-not $PackUrl) { $PackUrl = (Get-Content "$PSScriptRoot\kit.json" -Raw | ConvertFrom-Json).pack_url }
New-Item -ItemType Directory -Force $Dir, "$Dir\server", "$Dir\backups" | Out-Null
Set-Location $Dir

if (-not (Test-Path "$Dir\java\bin\javac.exe")) {
    Remove-Item "$Dir\java" -Recurse -Force -ErrorAction SilentlyContinue   # an old JRE-only copy
    Write-Host "Downloading Java 21 (JDK: LanAnnounce.java runs from source)..."
    Invoke-WebRequest "https://api.adoptium.net/v3/binary/latest/21/ga/windows/x64/jdk/hotspot/normal/eclipse" -OutFile jre.zip
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
$pwbs = "https://github.com/packwiz/packwiz-installer-bootstrap/releases/latest/download/packwiz-installer-bootstrap.jar"
Invoke-WebRequest $pwbs -OutFile packwiz-installer-bootstrap.jar
"eula=true" | Set-Content eula.txt -Encoding ascii
if (-not (Test-Path server.properties)) {
@"
motd=\u00a76Arkhaven\u00a7r - дом для всех
online-mode=true
white-list=false
difficulty=normal
view-distance=10
simulation-distance=6
spawn-protection=0
allow-flight=true
max-tick-time=-1
enable-rcon=false
"@ | Write-Utf8 "$Dir\server\server.properties"
}
"-Xms4G -Xmx$Memory -XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200 -XX:+UnlockExperimentalVMOptions -XX:+DisableExplicitGC -XX:G1NewSizePercent=30 -XX:G1MaxNewSizePercent=40 -XX:G1HeapRegionSize=8M -XX:G1ReservePercent=20 -XX:InitiatingHeapOccupancyPercent=15" | Set-Content user_jvm_args.txt -Encoding ascii
$PackUrl | Set-Content "$Dir\pack_url.txt" -Encoding ascii
Copy-Item "$PSScriptRoot\start.cmd", "$PSScriptRoot\backup.ps1", "$PSScriptRoot\LanAnnounce.java", "$PSScriptRoot\zerotier-host.ps1" $Dir -Force

# Owner = the Minecraft account already signed in on this PC (Arkhaven/Prism launcher or the official launcher).
function Find-Owner {
    $files = @("$env:LOCALAPPDATA\Arkhaven\accounts.json", "$env:APPDATA\PrismLauncher\accounts.json",
               "$env:APPDATA\.minecraft\launcher_accounts_microsoft_store.json", "$env:APPDATA\.minecraft\launcher_accounts.json")
    foreach ($f in $files) {
        if (-not (Test-Path $f)) { continue }
        try { $j = Get-Content $f -Raw | ConvertFrom-Json } catch { continue }
        $profiles = @()
        if ($j.accounts -is [array]) { $profiles = $j.accounts | ForEach-Object { $_.profile } }
        elseif ($j.accounts) { $profiles = $j.accounts.PSObject.Properties.Value | ForEach-Object { $_.minecraftProfile } }
        $p = $profiles | Where-Object { $_.id -and $_.name } | Select-Object -First 1
        if ($p) { return $p }
    }
    return $null
}
if (-not (Test-Path "ops.json")) {
    $o = Find-Owner
    if ($o) {
        $u = $o.id -replace '-', ''
        $uuid = "{0}-{1}-{2}-{3}-{4}" -f $u.Substring(0, 8), $u.Substring(8, 4), $u.Substring(12, 4), $u.Substring(16, 4), $u.Substring(20)
        ConvertTo-Json -InputObject @(@{ uuid = $uuid; name = $o.name; level = 4; bypassesPlayerLimit = $true }) | Write-Utf8 "$Dir\server\ops.json"
        Write-Host "Admin (op): $($o.name)"
    } else {
        Write-Host "No signed-in Minecraft account found on this PC: type  op YourNick  in the server console once."
    }
}

Write-Host "Firewall: allowing Minecraft (25565/tcp) and voice chat (24454/udp) on private networks..."
New-NetFirewallRule -DisplayName "Arkhaven Minecraft" -Direction Inbound -Protocol TCP -LocalPort 25565 -Action Allow -Profile Private -ErrorAction SilentlyContinue | Out-Null
New-NetFirewallRule -DisplayName "Arkhaven Voice" -Direction Inbound -Protocol UDP -LocalPort 24454 -Action Allow -Profile Private -ErrorAction SilentlyContinue | Out-Null

Write-Host "Scheduled tasks: hourly backup + start at logon..."
$b = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$Dir\backup.ps1`""
$t = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(30) -RepetitionInterval (New-TimeSpan -Hours 1)
Register-ScheduledTask -TaskName "Arkhaven Backup" -Action $b -Trigger $t -Force | Out-Null
$s = New-ScheduledTaskAction -Execute "$Dir\start.cmd" -WorkingDirectory $Dir
Register-ScheduledTask -TaskName "Arkhaven Server" -Action $s -Trigger (New-ScheduledTaskTrigger -AtLogOn) -Force | Out-Null

if (-not $NoZeroTier) {
    Write-Host "ZeroTier: hosting the friends' network..."
    $nwid = (& "$Dir\zerotier-host.ps1" -Dir $Dir | Select-Object -Last 1)
    # if this kit runs from the Arkhaven repository, publish the network id for the players' installer
    $repo = Resolve-Path "$PSScriptRoot\..\.." -ErrorAction SilentlyContinue
    if ($nwid -and $repo -and (Test-Path "$repo\pack\pack.toml")) {
        @{ zerotier = $nwid; server = "10.77.0.1" } | ConvertTo-Json | Set-Content "$repo\pack\network.json" -Encoding ascii
        Write-Host "Network id written to pack\network.json (published with the next pack update)."
    }
}

Write-Host ""
Write-Host "Done. The server starts automatically when you log in ($Dir\start.cmd)."
if (-not $NoStart) { Start-Process "$Dir\start.cmd" -WorkingDirectory $Dir }
