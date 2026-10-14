#!/bin/bash
# Nightly restart with in-game warnings. Installed as a systemd timer (see server/README.md).
set -euo pipefail
cd /opt/arkhaven/compose
rcon() { docker exec arkhaven-mc rcon-cli "$@" >/dev/null 2>&1 || true; }
rcon 'tellraw @a {"text":"[Arkhaven] Ночной перезапуск через 5 минут / Nightly restart in 5 minutes","color":"gold"}'
sleep 240
rcon 'tellraw @a {"text":"[Arkhaven] Перезапуск через 1 минуту / Restart in 1 minute","color":"red"}'
sleep 60
rcon save-all flush
docker compose restart mc
