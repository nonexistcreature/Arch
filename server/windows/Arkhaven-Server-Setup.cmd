@echo off
rem Arkhaven server: one double-click. Asks for admin rights once (Windows "Yes" prompt), then installs
rem everything into C:\Arkhaven, hosts the friends' ZeroTier network, makes you admin and starts the server.
rem Re-running is safe: it updates scripts and keeps the world.
rem Keep this file ASCII with CRLF line endings: cmd.exe misreads UTF-8/LF batch files.
net session >nul 2>&1
if errorlevel 1 (
  powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
  exit /b
)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1" %*
if errorlevel 1 (
  echo.
  echo Setup failed - see the error above.
  pause
)
