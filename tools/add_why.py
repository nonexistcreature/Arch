#!/usr/bin/env python3
"""add_why.py <spec.yaml> <data.yaml>: add our RU/EN lines to quests of a quests_spec file.
data.yaml maps quest id -> [ru, en] (a `why` line) or -> {why: [ru, en], title: [ru, en]}.
An existing title is replaced; ids that are not in this spec are skipped, so one data file serves several specs."""
import re
import sys

import yaml


def flow(ru, en):
    return yaml.safe_dump({"ru": ru, "en": en}, allow_unicode=True, default_flow_style=True, width=10000).strip()


spec, data = sys.argv[1], sys.argv[2]
add = yaml.safe_load(open(data, encoding="utf8"))
s = open(spec, encoding="utf8").read()
n = 0
for k, v in add.items():
    head = f"  - id: {k}\n"
    if head not in s:
        continue
    n += 1
    fields = v if isinstance(v, dict) else {"why": v}
    i = s.index(head)
    j = s.find("\n  - id:", i + 5)
    j = len(s.rstrip("\n")) if j < 0 else j
    block = s[i:j]
    if "title" in fields:
        block = re.sub(r"\n    title: [^\n]*", "", block)
        block = block.replace(head, head + f"    title: {flow(*fields['title'])}\n", 1)
    if "why" in fields:
        block = re.sub(r"\n    why: [^\n]*", "", block) + f"\n    why: {flow(*fields['why'])}"
    s = s[:i] + block + s[j:]
open(spec, "w", encoding="utf8").write(s)
print(n, "quests updated")
