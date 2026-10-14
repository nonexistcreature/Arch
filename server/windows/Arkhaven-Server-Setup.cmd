@echo off
rem Arkhaven server: one double-click. Asks for admin rights once (Windows "Yes" prompt), then installs
rem everything into C:\Arkhaven, hosts the friends' ZeroTier network, makes you admin and starts the server.
rem Re-running is safe: it updates scripts and keeps the world.
chcp 65001 >nul
net session >nul 2>&1
if errorlevel 1 (
  powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
  exit /b
)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1" %*
if errorlevel 1 (
  echo.
  echo Что-то пошло не так — сообщение об ошибке выше. Окно можно закрыть.
  pause
)
