#!/usr/bin/env python3
"""Richer structure chests (owner, 2026-10-17: «в обычных сундуках увеличь спавн рейт редкого лута, клеток для пчёл»).
Every structure chest loot table (vanilla + mods, ~700) additionally rolls arkhaven:chests/bonus through a NeoForge global
loot modifier (neoforge:add_table). Works with Lootr (per-player chests use the same loot pipeline).
Reads the jars of the synced test server (tests/server_run). Output: pack/kubejs/data/{arkhaven,neoforge}/...
Usage: gen_chest_bonus.py"""
import glob, json, re, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUN = ROOT / "tests/server_run"
DATA = ROOT / "pack/kubejs/data"
SKIP = re.compile(r"inject|/supply|_supply|dispenser|barrel_food|hero_of_the_village")   # inject tables, not real chests


def item(name, weight, lo=1, hi=1, extra=None):
    e = {"type": "minecraft:item", "name": name, "weight": weight}
    fn = []
    if hi > 1:
        fn.append({"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": lo, "max": hi}})
    fn += extra or []
    if fn:
        e["functions"] = fn
    return e


ENCHANT_RANDOM = [{"function": "minecraft:enchant_randomly"}]
ENCHANT_HIGH = [{"function": "minecraft:enchant_with_levels", "levels": 30, "options": "#minecraft:on_random_loot"}]

BONUS = {
    "type": "minecraft:chest",
    "pools": [
        {   # always one extra useful item
            "rolls": 1,
            "entries": [
                item("productivebees:bee_cage", 14, 1, 2),
                item("productivebees:sturdy_bee_cage", 5),
                item("minecraft:emerald", 12, 2, 5),
                item("minecraft:diamond", 7, 1, 2),
                item("minecraft:golden_apple", 7),
                item("minecraft:enchanted_golden_apple", 1),
                item("minecraft:book", 8, extra=ENCHANT_RANDOM),
                item("minecraft:name_tag", 4),
                item("minecraft:saddle", 3),
                item("minecraft:experience_bottle", 8, 3, 8),
                item("minecraft:netherite_scrap", 1),
                item("ars_nouveau:source_gem", 6, 2, 4),
                item("mekanism:ingot_osmium", 6, 2, 5),
                item("create:brass_ingot", 5, 2, 4),
            ],
        },
        {   # one in three chests: something rare on top
            "rolls": 1,
            "conditions": [{"condition": "minecraft:random_chance", "chance": 0.35}],
            "entries": [
                item("minecraft:diamond", 10, 1, 3),
                item("minecraft:book", 10, extra=ENCHANT_HIGH),
                item("productivebees:sturdy_bee_cage", 6, 1, 2),
                item("minecraft:netherite_scrap", 3),
                item("minecraft:totem_of_undying", 2),
                item("minecraft:heart_of_the_sea", 1),
                item("minecraft:emerald_block", 3),
                item("minecraft:enchanted_golden_apple", 2),
            ],
        },
    ],
}


def main():
    tables = set()
    for j in glob.glob(str(RUN / "mods/*.jar")) + glob.glob(str(RUN / "libraries/net/minecraft/server/1.21.1-*/server-1.21.1-*-extra.jar")):
        with zipfile.ZipFile(j) as z:
            for n in z.namelist():
                m = re.match(r"data/([\w.-]+)/loot_table/(chests?/.+)\.json$", n)
                if m and not SKIP.search(m.group(2)):
                    tables.add(f"{m.group(1)}:{m.group(2)}")
    (DATA / "arkhaven/loot_table/chests").mkdir(parents=True, exist_ok=True)
    (DATA / "arkhaven/loot_table/chests/bonus.json").write_text(json.dumps(BONUS, indent=1), "utf8")
    (DATA / "arkhaven/loot_modifiers").mkdir(parents=True, exist_ok=True)
    (DATA / "arkhaven/loot_modifiers/chest_bonus.json").write_text(json.dumps({
        "type": "neoforge:add_table",
        "conditions": [{"condition": "minecraft:any_of",
                        "terms": [{"condition": "neoforge:loot_table_id", "loot_table_id": t} for t in sorted(tables)]}],
        "table": "arkhaven:chests/bonus"}, indent=1), "utf8")
    (DATA / "neoforge/loot_modifiers").mkdir(parents=True, exist_ok=True)
    (DATA / "neoforge/loot_modifiers/global_loot_modifiers.json").write_text(json.dumps(
        {"replace": False, "entries": ["arkhaven:chest_bonus"]}, indent=1), "utf8")
    print(len(tables), "chest loot tables get arkhaven:chests/bonus")


if __name__ == "__main__":
    main()
