#!/usr/bin/env python3
"""Add CurseForge-only mods listed in tools/modlist_cf.txt via packwiz (idempotent). Lines: slug | wave | role"""
import subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
PW = ROOT / "tools" / "bin" / "packwiz.exe"
for line in (ROOT / "tools/modlist_cf.txt").read_text("utf8").splitlines():
    slug = line.split("#")[0].split("|")[0].strip()
    if not slug: continue
    r = subprocess.run([str(PW), "cf", "add", slug, "-y"], cwd=ROOT / "pack", capture_output=True, text=True, encoding="utf8", errors="replace")
    out = (r.stdout + r.stderr).strip().splitlines()
    print(("OK   " if r.returncode == 0 else "FAIL ") + slug, "|", out[-1] if out else "")
