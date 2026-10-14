# Arkhaven: join the friends' ZeroTier network (virtual LAN over the internet), so the game finds the server
# even when the player is not at the owner's home. Run by the client installer; can be re-run any time:
#   powershell -ExecutionPolicy Bypass -File zerotier-join.ps1 [-Network <16 hex>] [-NetworkUrl <url of network.json>]
# Installs ZeroTier One if missing (asks for admin rights itself), joins the network and allows only the LAN
# discovery packets (UDP 4445) from the ZeroTier subnet. Nothing else on the PC is opened or changed.
param(
    [string]$Network = "",
    [string]$NetworkUrl = ""
)
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
$Subnet = "10.77.0.0/24"

if (-not $Network -and $NetworkUrl) {
    try { $Network = (Invoke-RestMethod $NetworkUrl -TimeoutSec 15).zerotier } catch { $Network = "" }
}
if ($Network -notmatch '^[0-9a-fA-F]{16}$') {
    Write-Host "Сеть ZeroTier ещё не создана владельцем сервера — пропускаю (в домашней сети всё работает и так)."
    exit 0
}

$admin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $admin) {
    Start-Process powershell.exe -Verb RunAs -Wait -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`" -Network $Network"
    exit 0
}

function Find-Cli { @("${env:ProgramFiles(x86)}\ZeroTier\One\zerotier-cli.bat", "$env:ProgramFiles\ZeroTier\One\zerotier-cli.bat") | Where-Object { Test-Path $_ } | Select-Object -First 1 }
$cli = Find-Cli
if (-not $cli) {
    Write-Host "Устанавливаю ZeroTier One..."
    $msi = Join-Path $env:TEMP "ZeroTierOne.msi"
    Invoke-WebRequest "https://download.zerotier.com/dist/ZeroTier%20One.msi" -OutFile $msi
    Start-Process msiexec.exe -ArgumentList "/i `"$msi`" /qn /norestart" -Wait
    Remove-Item $msi -ErrorAction SilentlyContinue
    $cli = Find-Cli
    if (-not $cli) { throw "ZeroTier не установился — поставь вручную с https://www.zerotier.com/download/ и запусти скрипт снова" }
}

Write-Host "Подключаюсь к сети друзей $Network..."
for ($i = 0; $i -lt 10; $i++) {   # the service needs a few seconds after a fresh install
    & $cli join $Network | Out-Null
    if ($LASTEXITCODE -eq 0) { break }
    Start-Sleep -Seconds 3
}
Remove-NetFirewallRule -DisplayName "Arkhaven ZT discovery" -ErrorAction SilentlyContinue
New-NetFirewallRule -DisplayName "Arkhaven ZT discovery" -Direction Inbound -Protocol UDP -LocalPort 4445 -RemoteAddress $Subnet -Action Allow -Profile Any | Out-Null
for ($i = 0; $i -lt 20; $i++) {
    $st = (& $cli -j listnetworks | Out-String | ConvertFrom-Json) | Where-Object { $_.nwid -eq $Network.ToLower() }
    if ($st -and $st.status -eq "OK") { Write-Host "В сети друзей: $($st.assignedAddresses -join ', ')"; break }
    Start-Sleep -Seconds 2
}
Write-Host "Готово."
