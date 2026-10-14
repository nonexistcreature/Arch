#!/bin/bash
# Make this Linux box the host of the friends' ZeroTier network (no zerotier.com account needed):
# ZeroTier One's built-in controller creates network "arkhaven" 10.77.0.0/24, this box gets 10.77.0.1,
# friends join automatically. Idempotent; network id kept in /opt/arkhaven/zerotier_network.txt.
# Run as a sudoer: bash zerotier-host.sh
set -euo pipefail
SUBNET=10.77.0.0/24; HOST_IP=10.77.0.1; ID_FILE=/opt/arkhaven/zerotier_network.txt
command -v zerotier-cli >/dev/null || curl -fsSL https://install.zerotier.com | sudo bash
TOKEN=$(sudo cat /var/lib/zerotier-one/authtoken.secret)
api() { curl -fsS -H "X-ZT1-Auth: $TOKEN" "http://127.0.0.1:9993$1" "${@:2}"; }
for _ in $(seq 20); do NODE=$(api /status 2>/dev/null | python3 -c 'import json,sys;print(json.load(sys.stdin)["address"])' 2>/dev/null) && break; sleep 2; done
CFG='{"name":"arkhaven","private":false,"enableBroadcast":true,"multicastLimit":64,"v4AssignMode":{"zt":true},
"ipAssignmentPools":[{"ipRangeStart":"10.77.0.10","ipRangeEnd":"10.77.0.250"}],"routes":[{"target":"'$SUBNET'"}]}'
NWID=$(sudo cat "$ID_FILE" 2>/dev/null || true)
if [ -n "$NWID" ] && api "/controller/network/$NWID" >/dev/null 2>&1; then
  api "/controller/network/$NWID" -X POST -d "$CFG" >/dev/null
else
  NWID=$(api "/controller/network/${NODE}______" -X POST -d "$CFG" | python3 -c 'import json,sys;print(json.load(sys.stdin)["id"])')
  echo "$NWID" | sudo tee "$ID_FILE" >/dev/null
fi
sudo zerotier-cli join "$NWID" >/dev/null
api "/controller/network/$NWID/member/$NODE" -X POST -d '{"authorized":true,"ipAssignments":["'$HOST_IP'"]}' >/dev/null
if command -v ufw >/dev/null && sudo ufw status | grep -q active; then
  sudo ufw allow from $SUBNET to any port 25565 proto tcp comment arkhaven-zt
  sudo ufw allow from $SUBNET to any port 24454 proto udp comment arkhaven-zt-voice
fi
echo "ZeroTier: network $NWID, server address $HOST_IP"
