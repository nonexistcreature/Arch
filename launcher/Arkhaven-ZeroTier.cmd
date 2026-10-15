@echo off
rem Arkhaven: join the friends' ZeroTier network (virtual LAN), so the game finds the server from anywhere.
rem Double-click, answer "Yes" to the admin prompt. Safe to run again. ASCII + CRLF on purpose (cmd.exe).
setlocal
set NET=5de652dcca0e488b
net session >nul 2>&1
if errorlevel 1 (
  powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
  exit /b
)
title Arkhaven - ZeroTier
echo [Arkhaven] Checking the current network id...
for /f "usebackq delims=" %%i in (`powershell -NoProfile -Command "try { (Invoke-RestMethod 'https://nonexistcreature.github.io/Arch/network.json' -TimeoutSec 10).zerotier } catch { }"`) do set NET=%%i
echo [Arkhaven] Network: %NET%

set "CLI=%ProgramFiles(x86)%\ZeroTier\One\zerotier-cli.bat"
if not exist "%CLI%" set "CLI=%ProgramFiles%\ZeroTier\One\zerotier-cli.bat"
if exist "%CLI%" goto :join

echo [Arkhaven] Installing ZeroTier One (about 20 MB)...
curl.exe -L -s -o "%TEMP%\ZeroTierOne.msi" "https://download.zerotier.com/dist/ZeroTier%%20One.msi"
msiexec /i "%TEMP%\ZeroTierOne.msi" /qn /norestart
del "%TEMP%\ZeroTierOne.msi" >nul 2>&1
timeout /t 10 /nobreak >nul
set "CLI=%ProgramFiles(x86)%\ZeroTier\One\zerotier-cli.bat"
if not exist "%CLI%" set "CLI=%ProgramFiles%\ZeroTier\One\zerotier-cli.bat"
if not exist "%CLI%" goto :fail

:join
echo [Arkhaven] Joining the network...
set TRIES=0
:retry
call "%CLI%" join %NET% >nul 2>&1
if not errorlevel 1 goto :joined
set /a TRIES+=1
if %TRIES% GEQ 10 goto :fail
timeout /t 3 /nobreak >nul
goto :retry

:joined
rem only LAN discovery packets from the ZeroTier subnet; nothing else is opened
netsh advfirewall firewall delete rule name="Arkhaven ZT discovery" >nul 2>&1
netsh advfirewall firewall add rule name="Arkhaven ZT discovery" dir=in action=allow protocol=UDP localport=4445 remoteip=10.77.0.0/24 >nul
echo [Arkhaven] Waiting for an address (up to 30 s)...
set TRIES=0
:wait
call "%CLI%" listnetworks | find "%NET%" | find " OK " >nul && goto :ok
set /a TRIES+=1
if %TRIES% GEQ 10 goto :pending
timeout /t 3 /nobreak >nul
goto :wait

:ok
echo.
call "%CLI%" listnetworks | find "%NET%"
echo.
echo [Arkhaven] Done! You are in the friends' network. The server is 10.77.0.1 - the game connects by itself.
goto :end

:pending
echo.
echo [Arkhaven] Joined, but no address yet. It usually appears within a minute;
echo            if not, make sure the server PC is on and send this window to the admin.
goto :end

:fail
echo.
echo [Arkhaven] Could not install or start ZeroTier. Install it by hand from https://www.zerotier.com/download/
echo            and run this file again.

:end
echo.
pause
