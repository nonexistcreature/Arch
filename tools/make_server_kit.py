#!/usr/bin/env python3
"""Pack the server deployment kit: launcher/dist/Arkhaven-Server-Kit.zip
(Linux/Docker files, Windows scripts, LAN announcer, Russian how-to)."""
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "launcher/dist/Arkhaven-Server-Kit.zip"
FILES = [
    "server/КАК_РАЗВЕРНУТЬ.md", "server/README.md", "server/docker-compose.yml", "server/.env.example",
    "server/lan_announce.py", "server/server-icon.png",
    "server/scripts/install.sh", "server/scripts/nightly_restart.sh", "server/scripts/restore.sh", "server/scripts/preflight.sh",
    "server/windows/install.ps1", "server/windows/start.cmd", "server/windows/backup.ps1", "server/windows/LanAnnounce.java",
]
OUT.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    for f in FILES:
        p = ROOT / f
        info = zipfile.ZipInfo(f, date_time=(2026, 1, 1, 0, 0, 0))
        info.external_attr = (0o755 if f.endswith(".sh") else 0o644) << 16
        z.writestr(info, p.read_bytes().replace(b"\r\n", b"\n") if f.endswith(".sh") else p.read_bytes())
print(OUT, OUT.stat().st_size // 1024, "KB")
