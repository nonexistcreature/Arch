#!/usr/bin/env python3
"""Print mod ids reported missing/unsupported in tests/server_run/boot.log."""
import re
from pathlib import Path
t = (Path(__file__).resolve().parent.parent / "tests/server_run/boot.log").read_text("utf8", "replace")
for m in re.finditer(r"Mod ID: '([^']+)', Requested by: '([^']+)', Expected range: '([^']+)', Actual version: '([^']+)'", t):
    print(m.group(1), "<-", m.group(2), m.group(3), "have", m.group(4))
for m in re.finditer(r"Duplicate mod.*|Mod file .* is missing.*|requires .*", t): print(m.group(0)[:200])
