#!/usr/bin/env python3
"""How much of each mod do the quests cover? Counts only *useful* item families (owner, 2026-10-16: decor and
building blocks that do nothing are not worth a quest). Useful = any non-block item (tools, weapons, armor, food,
materials, potions) except purely decorative ones, plus blocks that work (machines, stations, altars, storage,
ores, crops). One item in all its colours/woods/shapes = one family; spawn eggs, unfinished parts, creative and
technical items are skipped. A family is covered when any of its items is an item task or a quest icon.

Usage: quest_coverage.py [--min-items 5] [--below 80] [--json out.json]
       quest_coverage.py --key      coverage of the hand-picked key items (quests_spec/key_items.yaml)
Prints one row per mod namespace: families, covered, %, and the first uncovered families.
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from quest_sources import load_chapters  # noqa: E402

COLORS = ("white|orange|magenta|light_blue|yellow|lime|pink|gray|light_gray|cyan|purple|blue|brown|green|red|black|"
          "navy|tan|slate|forest|aqua|amber|maroon|lavender|crimson|indigo|sky|rose|mint|olive|teal|beige|coral")
WOODS = ("oak|spruce|birch|jungle|acacia|dark_oak|mangrove|cherry|bamboo|crimson|warped|ironwood|twilight_oak|canopy|"
         "mangrove|darkwood|timewood|transwood|minewood|sortwood|skyroot|golden_oak|wisewood|archwood|"
         "redwood|fir|pine|maple|willow|palm|baobab|cypress|ebony|aspen|jacaranda")
SHAPES = (r"_(stairs|slab|wall|fence_gate|fence|button|pressure_plate|door|trapdoor|hanging_sign|wall_hanging_sign|"
          r"wall_sign|sign|pane|carpet|banner|wall_banner|bed|candle|vertical_slab|pillar|tiles?|bricks?|"
          r"chiseled|cracked|mossy|polished|smooth|cut|block|log|wood|planks|leaves|sapling|boat|chest_boat|"
          r"stripped|glass|stained|concrete|terracotta|wool|shulker_box|lamp|light|post|beam)$")
SKIP = re.compile(r"(spawn_egg|^incomplete_|^unfinished_|^creative_|_creative$|^debug|^dummy|^test_|^fake_|"
                  r"^bounding|^invisible|placeholder|^technical|_wip$|^music_disc|^disc_fragment)")


FUNCTIONAL_BLOCK = re.compile(
    r"(machine|generator|furnace|smelter|table|bench|press|altar|chamber|factory|pump|tank|cell|port|valve|"
    r"bearing|engine|motor|mixer|crusher|grinder|centrifuge|controller|reactor|turbine|boiler|cauldron|anvil|"
    r"forge|workbench|station|crafter|assembler|infuser|apparatus|enchant|imbu|ritual|pedestal|relay|turret|"
    r"spawner|hive|nest|incubator|feeder|interface|terminal|drive|storage|vault|barrel|crate|chest|bin|"
    r"silo|keg|cask|oven|stove|grill|pot|skillet|kettle|press|tub|tap|brewer|still|distill|ferment|"
    r"charger|battery|capacitor|accumulator|conduit|cable|wire|pipe|tube|conveyor|belt|funnel|chute|depot|"
    r"drill|saw|harvester|planter|deployer|arm|ejector|deployer|link|scanner|radar|monitor|beacon|portal|"
    r"teleport|waystone|obelisk|totem|trap|launcher|cannon|mount|gun|reader|sensor|detector|observer|"
    r"jar|core|frame|catalyst|matrix|collector|extractor|sorter|router|hopper|dispenser|composter|"
    r"_ore$|^ore_|ore_|deepslate_.*ore|raw_.*_block|crop|seed|sapling|bush|vine|soil|farmland)")
DECOR_ITEM = re.compile(r"(painting|banner_pattern|pottery_sherd|plush|figure|statue|poster|sticker|"
                        r"_dye$|^dye_|record|cosmetic|skin|costume|hat_|_hat$|flag)")


def useful(path, is_block):
    if is_block:
        return bool(FUNCTIONAL_BLOCK.search(path))
    return not DECOR_ITEM.search(path)


def family(path):
    p = path
    for _ in range(3):
        p = re.sub(SHAPES, "", p)
        p = re.sub(rf"^({COLORS})_|_({COLORS})$", "", p)
        p = re.sub(rf"^(stripped_)?({WOODS})_|_({WOODS})$", "", p)
        p = re.sub(r"^(stripped|polished|smooth|cut|chiseled|cracked|mossy|large|small|tall)_", "", p)
    return p or path


def main():
    a = sys.argv[1:]
    min_items = int(a[a.index("--min-items") + 1]) if "--min-items" in a else 5
    below = float(a[a.index("--below") + 1]) if "--below" in a else 101
    regall = json.load(open(ROOT / "tests/out/registry.json", encoding="utf8"))
    reg, blocks = regall["item"], set(regall.get("block", []))
    used = set()
    for c in load_chapters():
        for q in c["quests"]:
            if q.get("icon"):
                used.add(q["icon"])
            for t in q.get("tasks", []):
                if t.get("item"):
                    used.add(t["item"])
    if "--key" in a:
        import yaml
        keys = yaml.safe_load(open(ROOT / "quests_spec/key_items.yaml", encoding="utf8"))
        ok = bad = 0
        for ns, items in keys.items():
            if isinstance(items, dict):  # {quested: true, add: [...]}: every item already in quests + the listed extras
                items = sorted({i.split(":", 1)[1] for i in used if i.startswith(ns + ":")} | set(items.get("add", [])))
            ids = [f"{ns}:{i}" for i in items]
            unknown = [i for i in ids if i not in reg]
            got = [i for i in ids if i in used]
            miss = [i.split(":")[1] for i in ids if i not in used and i in reg]
            pct = 100 * len(got) / max(1, len(ids) - len(unknown))
            ok += pct >= 80; bad += pct < 80
            print(f"{ns:28} {len(got):3}/{len(ids) - len(unknown):3} {pct:5.1f}%  missing: {', '.join(miss)}"
                  + (f"  UNKNOWN: {unknown}" if unknown else ""))
        print(f"\n{ok} mods >= 80%, {bad} below")
        return
    fams = defaultdict(lambda: defaultdict(list))
    for i in reg:
        ns, p = i.split(":", 1)
        if ns == "minecraft" or SKIP.search(p) or not useful(p, i in blocks):
            continue
        fams[ns][family(p)].append(i)
    rows = []
    for ns, fs in fams.items():
        n_items = sum(len(v) for v in fs.values())
        if n_items < min_items:
            continue
        cov = [f for f, items in fs.items() if any(x in used for x in items)]
        unc = sorted(f for f in fs if f not in cov)
        pct = 100 * len(cov) / len(fs)
        rows.append((pct, ns, n_items, len(fs), len(cov), unc))
    rows.sort()
    for pct, ns, n, nf, nc, unc in rows:
        if pct < below:
            print(f"{ns:34} items={n:5} families={nf:4} covered={nc:4} {pct:5.1f}%  missing: {', '.join(unc[:12])}")
    tot_f = sum(r[3] for r in rows); tot_c = sum(r[4] for r in rows)
    print(f"\n{len(rows)} mods, families {tot_f}, covered {tot_c} ({100 * tot_c / tot_f:.1f}%), "
          f"mods >= 80%: {sum(r[0] >= 80 for r in rows)}")
    if "--json" in a:
        json.dump({r[1]: {"pct": r[0], "items": r[2], "families": r[3], "covered": r[4], "missing": r[5]} for r in rows},
                  open(a[a.index("--json") + 1], "w", encoding="utf8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
