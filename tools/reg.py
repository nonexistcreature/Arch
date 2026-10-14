#!/usr/bin/env python3
"""Grep the registry dump: reg.py [-t item|block|entity_type|fluid|mob_effect] pattern [pattern...] (all must match)"""
import json, sys
from pathlib import Path
a = sys.argv[1:]; kind = "item"
if a and a[0] == "-t": kind, a = a[1], a[2:]
d = json.loads((Path(__file__).resolve().parent.parent / "tests/out/registry.json").read_text("utf8"))
hits = sorted(i for i in d[kind] if all(p in i for p in a))
print(len(hits), " ".join(hits[:400]))
