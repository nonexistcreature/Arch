@echo off
rem Arkhaven server (Windows). Updates the modpack, announces itself on the LAN and restarts after a crash.
chcp 65001 >nul
cd /d "%~dp0"
set JAVA=%~dp0java\bin\java.exe
set /p PACK_URL=<"%~dp0pack_url.txt"
start "Arkhaven LAN" /min "%JAVA%" "%~dp0LanAnnounce.java" 25565 Arkhaven
:loop
cd /d "%~dp0server"
echo [Arkhaven] Updating the modpack...
"%JAVA%" -jar packwiz-installer-bootstrap.jar -g -s server "%PACK_URL%"
echo [Arkhaven] Starting the server. Type "stop" to shut it down.
"%JAVA%" @user_jvm_args.txt @libraries/net/neoforged/neoforge/21.1.259/win_args.txt nogui
if exist "%~dp0stop.flag" (del "%~dp0stop.flag" & goto :eof)
echo [Arkhaven] The server stopped. Restarting in 10 seconds (create stop.flag to prevent)...
timeout /t 10 >nul
goto loop
