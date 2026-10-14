#!/usr/bin/env python3
"""Fail if pack/index.toml hashes don't match the files on disk (a stale index makes packwiz-installer
abort the WHOLE update for players and the server). Runs in CI before publishing. Usage: verify_index.py [pack_dir]"""
import hashlib
import sys
import tomllib
from pathlib import Path

pack = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "pack")
packtoml = tomllib.loads((pack / "pack.toml").read_text("utf8"))
idx_path = pack / packtoml["index"]["file"]
bad = []
if hashlib.sha256(idx_path.read_bytes()).hexdigest() != packtoml["index"]["hash"]:
    bad.append(f"{idx_path.name}: hash in pack.toml is stale")
index = tomllib.loads(idx_path.read_text("utf8"))
for f in index["files"]:
    p = pack / f["file"]
    if not p.exists():
        bad.append(f"{f['file']}: missing")
        continue
    algo = f.get("hash-format", index["hash-format"])
    if hashlib.new(algo, p.read_bytes()).hexdigest() != f["hash"]:
        bad.append(f"{f['file']}: hash mismatch")
for b in bad:
    print("STALE", b)
print(f"{len(index['files'])} files checked, {len(bad)} problems")
sys.exit(1 if bad else 0)
