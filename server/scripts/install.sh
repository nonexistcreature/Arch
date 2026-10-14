#!/bin/bash
# One-time setup on Ubuntu 24.04 (run as a sudoer). Creates user `arkhaven`, /opt/arkhaven, Docker, systemd units.
# Touches nothing else on the box. Idempotent.
set -euo pipefail
command -v docker >/dev/null || { curl -fsSL https://get.docker.com | sh; }
id arkhaven >/dev/null 2>&1 || sudo useradd --system --create-home --home-dir /opt/arkhaven --shell /usr/sbin/nologin arkhaven
sudo usermod -aG docker arkhaven
sudo mkdir -p /opt/arkhaven/{compose/extras,data,backups,scripts}
sudo cp "$(dirname "$0")/../docker-compose.yml" /opt/arkhaven/compose/
sudo cp "$(dirname "$0")"/*.sh /opt/arkhaven/scripts/ && sudo chmod +x /opt/arkhaven/scripts/*.sh
[ -f /opt/arkhaven/compose/.env ] || sudo cp "$(dirname "$0")/../.env.example" /opt/arkhaven/compose/.env
[ -f "$(dirname "$0")/../server-icon.png" ] && sudo cp "$(dirname "$0")/../server-icon.png" /opt/arkhaven/compose/extras/
sudo chown -R arkhaven:arkhaven /opt/arkhaven
sudo tee /etc/systemd/system/arkhaven.service >/dev/null <<UNIT
[Unit]
Description=Arkhaven Minecraft server (docker compose)
Requires=docker.service
After=docker.service network-online.target
[Service]
Type=oneshot
RemainAfterExit=yes
User=arkhaven
WorkingDirectory=/opt/arkhaven/compose
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
[Install]
WantedBy=multi-user.target
UNIT
sudo tee /etc/systemd/system/arkhaven-restart.service >/dev/null <<UNIT
[Unit]
Description=Arkhaven nightly restart
[Service]
Type=oneshot
User=arkhaven
ExecStart=/opt/arkhaven/scripts/nightly_restart.sh
UNIT
sudo tee /etc/systemd/system/arkhaven-restart.timer >/dev/null <<UNIT
[Unit]
Description=Arkhaven nightly restart at 06:00
[Timer]
OnCalendar=*-*-* 06:00:00
Persistent=false
[Install]
WantedBy=timers.target
UNIT
sudo systemctl daemon-reload
sudo systemctl enable --now arkhaven.service arkhaven-restart.timer
if command -v ufw >/dev/null && sudo ufw status | grep -q active; then
  sudo ufw allow 25565/tcp comment arkhaven; sudo ufw allow 24454/udp comment arkhaven-voice
fi
echo "Arkhaven installed. Edit /opt/arkhaven/compose/.env, then: sudo systemctl restart arkhaven"
