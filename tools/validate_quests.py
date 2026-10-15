#!/usr/bin/env python3
"""Validate quests_src/*.yaml against tests/out/registry.json + anti-grind rules (docs/04_QUESTS.md §4, §7).
Writes docs/reports/quests_summary.md. Exit 1 on errors."""
import collections, json, sys
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent
reg = json.loads((ROOT / "tests/out/registry.json").read_text("utf8"))
items, ents = set(reg["item"]), set(reg["entity_type"])
structs = set(reg.get("structure", []))
errs, warns = [], []
chapters, allq = [], {}
sys.path.insert(0, str(ROOT / "tools"))
from quest_sources import load_chapters
for d in load_chapters():
    chapters.append((d["_file"], d))
    for x in d["quests"]:
        if x["id"] in allq: errs.append(f"duplicate quest id {x['id']}")
        allq[x["id"]] = (d["_file"], x)

def chk_item(where, i):
    if i not in items: errs.append(f"{where}: unknown item {i}")

roles = collections.Counter()
for fn, d in chapters:
    for lang in ("ru", "en"):
        if not d["chapter"].get(lang, {}).get("title"): errs.append(f"{fn}: chapter {lang} title missing")
    if d["chapter"].get("icon"): chk_item(fn, d["chapter"]["icon"])
    for x in d["quests"]:
        w = f"{fn}:{x['id']}"
        for lang in ("ru", "en"):
            t = x.get(lang) or {}
            if not t.get("title"): errs.append(f"{w}: {lang} title missing")
            n = len((t.get("text") or "").strip().splitlines())
            if n > 9: warns.append(f"{w}: {lang} text {n} lines (>8)")
        if x.get("icon"): chk_item(w, x["icon"])
        for dep in x.get("deps", []):
            if dep not in allq: errs.append(f"{w}: unknown dep {dep}")
        for t in x.get("tasks") or []:
            if t["type"] == "item":
                chk_item(w, t["item"])
                if t.get("count", 1) > 64: errs.append(f"{w}: anti-grind: count {t['count']} > 64")
            if t["type"] == "structure" and structs and t["structure"].lstrip("#") not in structs and not t["structure"].startswith("#"):
                errs.append(f"{w}: unknown structure {t['structure']}")
            if t["type"] == "kill":
                if t["entity"] not in ents: errs.append(f"{w}: unknown entity {t['entity']}")
                if t.get("count", 1) > 10: errs.append(f"{w}: anti-grind: kill {t['count']} > 10")
        for r in x.get("rewards") or []:
            if r["type"] == "item": chk_item(w, r["item"])
        for r in x.get("roles", []): roles[r] += 1

# cycles
state = {}
def visit(i, stack=()):
    if state.get(i) == 2: return
    if i in stack: errs.append(f"cycle: {' -> '.join(stack + (i,))}"); return
    for dep in allq[i][1].get("deps", []):
        if dep in allq: visit(dep, stack + (i,))
    state[i] = 2
for i in allq: visit(i)

rep = ["# quests_summary (авто, tools/validate_quests.py)\n", f"Всего квестов: **{len(allq)}**, глав: {len(chapters)}\n",
       "| файл | глава | квестов |", "|---|---|---|"]
for fn, d in chapters:
    rep.append(f"| {fn} | {d['chapter']['ru']['title']} | {len(d['quests'])} |")
rep += ["", "Роли: " + ", ".join(f"{k}: {v}" for k, v in roles.most_common()), "", f"Ошибок: {len(errs)}, предупреждений: {len(warns)}"]
rep += [f"- ⚠ {w}" for w in warns]
(ROOT / "docs/reports/quests_summary.md").write_text("\n".join(rep) + "\n", "utf8")
print(f"{len(allq)} quests, {len(errs)} errors, {len(warns)} warnings")
for e in errs: print(" ERR", e)
for w in warns[:20]: print(" warn", w)
sys.exit(1 if errs else 0)
