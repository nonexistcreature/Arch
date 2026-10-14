@echo off
rem Arkhaven into your own launcher (official Minecraft Launcher etc.). Double-click; see install-to-launcher.ps1.
chcp 65001 >nul
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install-to-launcher.ps1" %*
echo.
pause
