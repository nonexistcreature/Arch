#!/usr/bin/env python3
"""add_why.py <spec.yaml> <why.yaml>: insert `why: {ru, en}` lines into quests of a quests_spec file.
why.yaml maps quest id -> [ru, en]; ids that are not in this spec are skipped, so one why file can serve several specs."""
import sys
import yaml

spec, data = sys.argv[1], sys.argv[2]
add = yaml.safe_load(open(data, encoding="utf8"))
s = open(spec, encoding="utf8").read()
n = 0
for k, (ru, en) in add.items():
    head = f"  - id: {k}\n"
    if head not in s:
        continue
    n += 1
    i = s.index(head)
    j = s.find("\n  - id:", i + 5)
    j = len(s.rstrip("\n")) if j < 0 else j
    line = "    why: " + yaml.safe_dump({"ru": ru, "en": en}, allow_unicode=True, default_flow_style=True, width=10000).strip()
    s = s[:j] + "\n" + line + s[j:]
open(spec, "w", encoding="utf8").write(s)
print(n, "why lines added")
