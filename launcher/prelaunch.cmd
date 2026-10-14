@echo off
rem Arkhaven pre-launch: %1 = java.exe, %2 = instance dir, %3 = pack.toml URL
cd /d "%~dp0"
rem 1) find the server on the local network (updates servers.dat / auto-join address)
"%~1" "%~dp0Discover.java" "%~2"
rem 2) update the modpack (never block the game if the update host is unreachable)
"%~1" -jar "%~dp0packwiz-installer-bootstrap.jar" -s client "%~3"
exit /b 0
