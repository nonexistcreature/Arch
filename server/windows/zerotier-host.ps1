# Arkhaven: make this PC the host of the friends' ZeroTier network — no zerotier.com account needed.
# ZeroTier One has a built-in network controller; we use it to create the network "arkhaven" (10.77.0.0/24),
# give this PC the fixed address 10.77.0.1 and let friends join automatically (they still need a Minecraft
# account and the server's whitelist/claims apply). Idempotent: the network id is kept in <Dir>\zerotier_network.txt.
#   powershell -ExecutionPolicy Bypass -File zerotier-host.ps1 [-Dir C:\Arkhaven]     (as administrator)
param([string]$Dir = "C:\Arkhaven")
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
$Subnet = "10.77.0.0/24"; $HostIp = "10.77.0.1"

function Find-Cli { @("${env:ProgramFiles(x86)}\ZeroTier\One\zerotier-cli.bat", "$env:ProgramFiles\ZeroTier\One\zerotier-cli.bat") | Where-Object { Test-Path $_ } | Select-Object -First 1 }
$cli = Find-Cli
if (-not $cli) {
    Write-Host "Устанавливаю ZeroTier One..."
    $msi = Join-Path $env:TEMP "ZeroTierOne.msi"
    Invoke-WebRequest "https://download.zerotier.com/dist/ZeroTier%20One.msi" -OutFile $msi
    Start-Process msiexec.exe -ArgumentList "/i `"$msi`" /qn /norestart" -Wait
    Remove-Item $msi -ErrorAction SilentlyContinue
    $cli = Find-Cli
    if (-not $cli) { throw "ZeroTier не установился" }
}

$tokenFile = "$env:ProgramData\ZeroTier\One\authtoken.secret"
for ($i = 0; $i -lt 20 -and -not (Test-Path $tokenFile); $i++) { Start-Sleep -Seconds 2 }
$h = @{ "X-ZT1-Auth" = (Get-Content $tokenFile -Raw).Trim() }
$api = "http://127.0.0.1:9993"
$node = $null
for ($i = 0; $i -lt 20 -and -not $node; $i++) {
    try { $node = (Invoke-RestMethod "$api/status" -Headers $h).address } catch { Start-Sleep -Seconds 2 }
}
if (-not $node) { throw "служба ZeroTier не отвечает" }

$idFile = Join-Path $Dir "zerotier_network.txt"
$nwid = if (Test-Path $idFile) { (Get-Content $idFile -Raw).Trim() } else { $null }
$exists = $false
if ($nwid) { try { Invoke-RestMethod "$api/controller/network/$nwid" -Headers $h | Out-Null; $exists = $true } catch {} }
$cfg = @{
    name = "arkhaven"; private = $false; enableBroadcast = $true; multicastLimit = 64
    v4AssignMode = @{ zt = $true }
    ipAssignmentPools = @(@{ ipRangeStart = "10.77.0.10"; ipRangeEnd = "10.77.0.250" })
    routes = @(@{ target = $Subnet })
} | ConvertTo-Json -Depth 5
if ($exists) {
    Invoke-RestMethod "$api/controller/network/$nwid" -Method Post -Headers $h -Body $cfg -ContentType "application/json" | Out-Null
} else {
    $nwid = (Invoke-RestMethod "$api/controller/network/${node}______" -Method Post -Headers $h -Body $cfg -ContentType "application/json").id
    New-Item -ItemType Directory -Force $Dir | Out-Null
    $nwid | Set-Content $idFile -Encoding ascii
}
& $cli join $nwid | Out-Null
$member = @{ authorized = $true; ipAssignments = @($HostIp) } | ConvertTo-Json
Invoke-RestMethod "$api/controller/network/$nwid/member/$node" -Method Post -Headers $h -Body $member -ContentType "application/json" | Out-Null

# game ports from the ZeroTier subnet only (any firewall profile: the adapter stays "Public", nothing else is opened)
foreach ($r in @(@("Arkhaven ZT Minecraft", "TCP", 25565), @("Arkhaven ZT Voice", "UDP", 24454), @("Arkhaven ZT discovery", "UDP", 4445))) {
    Remove-NetFirewallRule -DisplayName $r[0] -ErrorAction SilentlyContinue
    New-NetFirewallRule -DisplayName $r[0] -Direction Inbound -Protocol $r[1] -LocalPort $r[2] -RemoteAddress $Subnet -Action Allow -Profile Any | Out-Null
}
Write-Host "ZeroTier: сеть $nwid, адрес сервера $HostIp"
$nwid
