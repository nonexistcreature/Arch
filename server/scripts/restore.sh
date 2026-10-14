#!/bin/bash
# Restore a restic snapshot: restore.sh <snapshot-id|latest> [--into DIR]
# Without --into: stops the server, moves the current world aside (never deleted), restores in place.
set -euo pipefail
SNAP=${1:?usage: restore.sh <snapshot|latest> [--into DIR]}
cd /opt/arkhaven/compose
source .env
if [[ "${2:-}" == "--into" ]]; then
  docker run --rm -e RESTIC_PASSWORD="$RCON_PASSWORD" -v /opt/arkhaven/backups:/backups -v "$3":/restore restic/restic -r /backups restore "$SNAP" --target /restore
  echo "restored $SNAP into $3"; exit 0
fi
docker compose stop mc
TS=$(date +%Y%m%d-%H%M%S)
mv /opt/arkhaven/data/world "/opt/arkhaven/data/world.before-restore-$TS"
docker run --rm -e RESTIC_PASSWORD="$RCON_PASSWORD" -v /opt/arkhaven/backups:/backups -v /opt/arkhaven/restore-tmp:/restore restic/restic -r /backups restore "$SNAP" --target /restore
mv /opt/arkhaven/restore-tmp/data/world /opt/arkhaven/data/world
rm -rf /opt/arkhaven/restore-tmp
docker compose start mc
echo "world restored from $SNAP; previous world kept at data/world.before-restore-$TS"
