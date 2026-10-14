#!/bin/bash
# Read-only inventory of the server box. Output goes to stdout (agent saves it to docs/reports/server_preflight.md).
echo "## OS"; (lsb_release -ds 2>/dev/null || cat /etc/os-release | head -2); uname -r
echo "## CPU"; lscpu | grep -E 'Model name|^CPU\(s\)|Thread|MHz' 
echo "## RAM"; free -h
echo "## Disks"; lsblk -o NAME,SIZE,TYPE,ROTA,MOUNTPOINT; df -h / /opt 2>/dev/null
echo "## Docker"; docker --version 2>/dev/null || echo "no docker"; docker compose version 2>/dev/null || true
echo "## Ports in use"; ss -tulpn 2>/dev/null | grep -E ':25565|:24454|:25575|:80 |:443 ' || echo "none of ours"
echo "## Network"; ip -4 addr show scope global | grep inet; curl -s -m 5 https://api.ipify.org && echo " (public IP)"
echo "## Firewall"; (sudo -n ufw status 2>/dev/null || echo "ufw: n/a or needs sudo")
