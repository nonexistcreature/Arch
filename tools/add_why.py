#!/usr/bin/env python3
"""add_why.py <spec.yaml> <why.yaml>: insert `why: {ru, en}` lines into quests of a quests_spec file.
why.yaml maps quest id -> [ru, en]."""
import sys, yaml
spec, data = sys.argv[1], sys.argv[2]
add = yaml.safe_load(open(data, encoding="utf8"))
s = open(spec, encoding="utf8").read()
for k, (ru, en) in add.items():
    i = s.index(f"  - id: {k}\n")
    j = s.find("\n  - id:", i + 5)
    j = len(s.rstrip("\n")) if j < 0 else j
    line = "    why: " + yaml.safe_dump({"ru": ru, "en": en}, allow_unicode=True, default_flow_style=True, width=10000).strip()
    s = s[:j] + "\n" + line + s[j:]
open(spec, "w", encoding="utf8").write(s)
print(len(add), "why lines added")
