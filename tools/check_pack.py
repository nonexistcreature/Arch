#!/usr/bin/env python3
"""Level-1 static checks: banned mods, sides, hashes, duplicates by name."""
import sys, tomllib, hashlib
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
BANNED = ("apotheosis", "apothic", "immersive-portals", "immersiveportals", "epic-fight", "valkyrien", "villagers-reborn",
          "journeymap", "refined-storage", "functional-storage", "travelers-backpack", "ftb-chunks", "tough-as-nails")
errs, n = [], 0
files = sorted((ROOT / "pack/mods").glob("*.pw.toml"))
fnames = {}
for f in files:
    n += 1
    d = tomllib.loads(f.read_text("utf8"))
    low = (f.stem + d.get("filename", "")).lower()
    if any(b in low for b in BANNED): errs.append(f"banned: {f.name}")
    if d.get("side") not in ("client", "server", "both"): errs.append(f"bad side: {f.name}")
    if not d.get("download", {}).get("hash"): errs.append(f"no hash: {f.name}")
    fnames.setdefault(d.get("filename"), []).append(f.name)
for k, v in fnames.items():
    if len(v) > 1: errs.append(f"duplicate file {k}: {v}")
idx = (ROOT / "pack/index.toml").read_bytes()
pk = tomllib.loads((ROOT / "pack/pack.toml").read_text("utf8"))
if pk["index"]["hash"] != hashlib.sha256(idx).hexdigest(): errs.append("index hash mismatch (run packwiz refresh)")
print(f"{n} mods checked, {len(errs)} problems")
for e in errs: print(" -", e)
sys.exit(1 if errs else 0)
