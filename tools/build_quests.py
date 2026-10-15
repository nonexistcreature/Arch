#!/usr/bin/env python3
"""quests_src/*.yaml -> pack/config/ftbquests/quests/{chapters/*.snbt, chapter_groups.snbt, data.snbt, lang/*.snbt}

Source format (one chapter per file):
  chapter: {id: welcome, order: 0, icon: minecraft:compass, ru: {title, subtitle}, en: {title, subtitle}}
  quests:
    - id: welcome_start            # globally unique
      icon: minecraft:book         # optional
      deps: [other_quest_id]       # optional, any chapter
      tier: T0                     # optional, used by validator
      roles: [cook]                # optional
      shape: gear                  # optional
      pos: [x, y]                  # optional, otherwise auto-layout by dependency depth
      tasks:   [{type: item, item: minecraft:stick, count: 4}, {type: checkmark}, {type: dimension, dimension: ...},
                {type: advancement, advancement: ...}, {type: kill, entity: ..., count: 1},
                {type: observation, block: ...} | {type: observation, entity: ...}, {type: structure, structure: ns:id}]
      rewards: [{type: item, item: ..., count: 8}, {type: xp_levels, count: 2}, {type: xp, count: 100},
                {type: command, command: "/say hi"}]
      ru: {title, subtitle, text}
      en: {title, subtitle, text}
Re-runnable; output is fully regenerated.
"""
import hashlib, json, re, shutil, sys
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "quests_src"
OUT = ROOT / "pack/config/ftbquests/quests"


def hid(*parts):
    # FTB Quests ids are signed longs: ids with the top bit set (8..F first digit) lose their translations,
    # so keep every id in the positive range (first hex digit 0..7).
    h = int(hashlib.sha1(("arkhaven:" + ":".join(parts)).encode()).hexdigest()[:16], 16) & 0x7FFFFFFFFFFFFFFF
    return f"{h:016X}"


def q(s):
    return json.dumps(str(s), ensure_ascii=False)


def fmt(line):
    line = re.sub(r"\*\*(.+?)\*\*", r"&l\1&r", line)
    line = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"&o\1&r", line)
    return line


def desc_lines(text):
    lines = [fmt(l.rstrip()) for l in (text or "").strip("\n").split("\n")]
    return lines


def snbt(v, ind=0):
    p = "\t" * ind
    if isinstance(v, dict):
        if not v:
            return "{ }"
        body = "\n".join(f"{p}\t{k}: {snbt(x, ind + 1)}" for k, x in v.items())
        return "{\n" + body + f"\n{p}}}"
    if isinstance(v, list):
        if not v:
            return "[ ]"
        if all(isinstance(x, str) for x in v):
            return "[\n" + "\n".join(f"{p}\t{q(x)}" for x in v) + f"\n{p}]"
        return "[\n" + "\n".join(f"{p}\t{snbt(x, ind + 1)}" for x in v) + f"\n{p}]"
    if isinstance(v, Raw):
        return v.s
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, str):
        return q(v)
    return str(v)


class Raw:
    def __init__(self, s): self.s = s


def D(x): return Raw(f"{float(x)}d")
def L(x): return Raw(f"{int(x)}L")


def item(i, c=1):
    return {"count": int(c), "id": i}


def task(t, qid, n):
    tid = hid("task", qid, str(n))
    k = t["type"]
    if k == "item":
        out = {"id": tid, "type": "item", "item": item(t["item"])}
        if t.get("count", 1) > 1: out["count"] = L(t["count"])
        if t.get("consume"): out["consume_items"] = True
        return out
    if k == "checkmark":
        return {"id": tid, "type": "checkmark"}
    if k == "dimension":
        return {"id": tid, "type": "dimension", "dimension": t["dimension"]}
    if k == "advancement":
        return {"id": tid, "type": "advancement", "advancement": t["advancement"], "criterion": t.get("criterion", "")}
    if k == "kill":
        return {"id": tid, "type": "kill", "entity": t["entity"], "value": L(t.get("count", 1))}
    if k == "structure":  # stand inside a structure (dungeon, castle...) — "#ns:tag" works too
        return {"id": tid, "type": "structure", "structure": t["structure"]}
    if k == "observation":
        if "block" in t:
            return {"id": tid, "type": "observation", "observe_type": 0, "to_observe": t["block"], "timer": L(t.get("ticks", 20))}
        return {"id": tid, "type": "observation", "observe_type": 5, "to_observe": t["entity"], "timer": L(t.get("ticks", 20))}
    raise ValueError(f"{qid}: unknown task type {k}")


def reward(r, qid, n):
    rid = hid("reward", qid, str(n))
    k = r["type"]
    if k == "item":
        return {"id": rid, "type": "item", "item": item(r["item"], r.get("count", 1))}
    if k == "xp_levels":
        return {"id": rid, "type": "xp_levels", "xp_levels": int(r["count"])}
    if k == "xp":
        return {"id": rid, "type": "xp", "xp": int(r["count"])}
    if k == "command":
        return {"id": rid, "type": "command", "command": r["command"], "elevate_perms": True, "silent": True}
    raise ValueError(f"{qid}: unknown reward type {k}")


def load_sources():
    from quest_sources import load_chapters
    return load_chapters()


def layout(quests):
    by = {x["id"]: x for x in quests}
    depth = {}
    def dp(i, seen=()):
        if i in depth: return depth[i]
        if i in seen: raise ValueError(f"dependency cycle at {i}")
        ds = [d for d in by[i].get("deps", []) if d in by]
        depth[i] = 0 if not ds else 1 + max(dp(d, seen + (i,)) for d in ds)
        return depth[i]
    for x in quests: dp(x["id"])
    # Layered top-down layout (Sugiyama-style): a quest's row is its dependency depth; inside a row quests are
    # ordered and shifted towards the middle of their parents (sweeping down) and of their children (sweeping
    # up), so every line is short and lines rarely cross. Rows keep a minimum gap between quests.
    HX, DY, SWEEPS = 1.5, 2.0, 12
    parents = {x["id"]: [d for d in x.get("deps", []) if d in by] for x in quests}
    children = {x["id"]: [] for x in quests}
    for i, ps in parents.items():
        for d in ps:
            children[d].append(i)
    rows = {}
    seen = set()

    def visit(i):  # depth-first order keeps each branch together for the first placement
        if i in seen:
            return
        seen.add(i)
        rows.setdefault(depth[i], []).append(i)
        for c in children[i]:
            if max(parents[c], key=lambda d: depth[d]) == i:
                visit(c)

    for x in quests:
        if not parents[x["id"]]:
            visit(x["id"])
    for x in quests:
        visit(x["id"])
    xpos = {}
    for d, row in rows.items():
        for n, i in enumerate(row):
            xpos[i] = (n - (len(row) - 1) / 2) * HX

    def settle(row, want):
        """Order a row by wanted x, then place with at least HX between neighbours, as close to wanted as possible."""
        row.sort(key=lambda i: want[i])
        xs = [want[i] for i in row]
        for n in range(1, len(xs)):
            xs[n] = max(xs[n], xs[n - 1] + HX)
        shift = sum(want[i] - x for i, x in zip(row, xs)) / len(xs)
        for i, x in zip(row, xs):
            xpos[i] = x + shift

    order = sorted(rows)
    for sweep in range(SWEEPS):
        down = sweep % 2 == 0
        for d in (order[1:] if down else order[-2::-1]):
            row = rows[d]
            want = {}
            for i in row:
                nb = parents[i] if down else children[i]
                want[i] = sum(xpos[j] for j in nb) / len(nb) if nb else xpos[i]
            settle(row, want)
    xs = list(xpos.values())
    mid = (min(xs) + max(xs)) / 2 if xs else 0
    pos = {i: (round(xpos[i] - mid, 2), round(depth[i] * DY, 2)) for i in xpos}
    for x in quests:
        if "pos" in x:
            pos[x["id"]] = tuple(x["pos"])
    return pos


def main():
    chapters = load_sources()
    allq = {}
    for c in chapters:
        for x in c["quests"]:
            if x["id"] in allq: sys.exit(f"duplicate quest id {x['id']}")
            allq[x["id"]] = x
    if OUT.exists(): shutil.rmtree(OUT)
    (OUT / "chapters").mkdir(parents=True)
    (OUT / "lang").mkdir()
    lang = {"ru_ru": {}, "en_us": {}}
    for c in chapters:
        ch = c["chapter"]; cid = hid("chapter", ch["id"])
        for loc, k in (("ru_ru", "ru"), ("en_us", "en")):
            lang[loc][f"chapter.{cid}.title"] = ch[k]["title"]
            if ch[k].get("subtitle"): lang[loc][f"chapter.{cid}.chapter_subtitle"] = [ch[k]["subtitle"]]
        pos = layout(c["quests"])
        qs = []
        for x in c["quests"]:
            qid = hid("quest", x["id"])
            o = {"id": qid, "x": D(pos[x["id"]][0]), "y": D(pos[x["id"]][1])}
            if x.get("shape"): o["shape"] = x["shape"]
            if x.get("icon"): o["icon"] = {"id": x["icon"], "count": 1}
            deps = [hid("quest", d) for d in x.get("deps", [])]
            for d in x.get("deps", []):
                if d not in allq: sys.exit(f"{x['id']}: unknown dependency {d}")
            if deps: o["dependencies"] = deps
            if x.get("optional"): o["optional"] = True
            if x.get("repeatable"): o["can_repeat"] = True
            o["tasks"] = [task(t, x["id"], i) for i, t in enumerate(x.get("tasks") or [{"type": "checkmark"}])]
            if x.get("rewards"): o["rewards"] = [reward(r, x["id"], i) for i, r in enumerate(x["rewards"])]
            qs.append(o)
            for loc, k in (("ru_ru", "ru"), ("en_us", "en")):
                t = x[k]
                lang[loc][f"quest.{qid}.title"] = t["title"]
                if t.get("subtitle"): lang[loc][f"quest.{qid}.quest_subtitle"] = t["subtitle"]
                if t.get("text"): lang[loc][f"quest.{qid}.quest_desc"] = desc_lines(t["text"])
        doc = {"id": cid, "group": "", "order_index": int(round(float(ch["order"]) * 10)), "filename": ch["id"],
               "icon": {"id": ch.get("icon", "minecraft:book"), "count": 1},
               "default_quest_shape": "", "default_hide_dependency_lines": False, "quests": qs}
        (OUT / "chapters" / f"{ch['id']}.snbt").write_text(snbt(doc) + "\n", "utf8", newline="\n")
    (OUT / "data.snbt").write_text(snbt({
        "version": 13, "default_reward_team": True, "default_consume_items": False,
        "default_autoclaim_rewards": "disabled", "default_quest_shape": "circle",
        "default_quest_disable_jei": False, "emergency_items_cooldown": 300, "drop_loot_crates": False,
        "disable_gui": False, "grid_scale": D(0.5), "pause_game": False,
        "lock_message": "", "progression_mode": "flexible", "detection_delay": 20,
        "show_lock_icons": True, "drop_book_on_death": False,
    }) + "\n", "utf8", newline="\n")
    (OUT / "chapter_groups.snbt").write_text("{\n\tchapter_groups: [ ]\n}\n", "utf8", newline="\n")
    for loc, m in lang.items():
        (OUT / "lang" / f"{loc}.snbt").write_text(snbt(m) + "\n", "utf8", newline="\n")
    gen = ROOT / "pack/kubejs/server_scripts/generated"
    gen.mkdir(parents=True, exist_ok=True)
    ids = {q: hid("quest", q) for q in allq}
    header = "// GENERATED by tools/build_quests.py - quest name -> FTB Quests hex id\n"
    (gen / "quest_ids.js").write_text(header + "const ARK_QUEST_IDS = " + json.dumps(ids, indent=1) + "\n", "utf8", newline="\n")
    print(f"{len(chapters)} chapters, {len(allq)} quests -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
