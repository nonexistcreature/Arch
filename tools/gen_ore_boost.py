#!/usr/bin/env python3
"""More ore (owner, 2026-10-17: «увеличь спавнрейт руд редких или тех, что надо много»).
Copies the ore placed_features of vanilla and the mods below into pack/kubejs/data (KubeJS's datapack overrides mod data)
with more attempts per chunk (count x k) or a smaller rarity chance (chance / k). Only NEW chunks get it — the pregenerated
area keeps its ore, except Mekanism and IE, which do retrogen via their own configs (pack/config).
Reads the jars of the synced test server (tests/server_run: run tools/server_boot_test.py first).
Usage: gen_ore_boost.py"""
import glob, json, math, re, shutil, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUN = ROOT / "tests/server_run"
OUT = ROOT / "pack/kubejs/data"
MARK = "_arkhaven_ore_boost"   # written into every generated file so a rerun can clean up its own output

BOOST = {   # placed feature id (regex, full match) -> multiplier
    r"minecraft:ore_(iron_.*|copper.*|gold.*|emerald)": 2.0,
    r"minecraft:ore_diamond.*": 1.75,
    r"minecraft:ore_(redstone.*|lapis.*|quartz.*|ancient_debris_large|debris_small)": 1.5,
    r"create:zinc_ore": 2.0,
    r"tfmg:(lead|lithium|nickel)_ore": 2.0,
    r"create_new_age:thorium_ore": 2.0,
    r"createmetallurgy:wolframite_ore": 2.0,
    r"createnuclear:(lead|uranium|thorium|nitrate)_ore": 2.0,
    r"occultism:ore_(silver.*|iesnium)": 2.0,
    r"bigreactors:.*_ore": 2.0,
    r"irons_spellbooks:ore_mithril_placement": 2.0,
    r"undergarden:(cloggrum|froststeel|iron|gold|regalium|utherium|diamond)_ore": 2.0,
    r"aether:(zanite_ore|gravitite_ore.*)": 2.0,
    r"deep_aether:(more_)?skyjade_ore": 2.0,
    r"mysticalagriculture:(inferium|prosperity)_ore": 2.0,
}


def scale(v, k):
    if isinstance(v, int):
        return max(1, math.ceil(v * k))
    if isinstance(v, dict):
        t = v.get("type", "")
        if t in ("minecraft:uniform", "minecraft:biased_to_bottom", "minecraft:clamped"):
            return {**v, **{f: scale(v[f], k) for f in ("min_inclusive", "max_inclusive") if f in v}}
        if t == "minecraft:constant":
            return {**v, "value": scale(v["value"], k)}
        if t == "minecraft:weighted_list":
            return {**v, "distribution": [{**e, "data": scale(e["data"], k)} for e in v["distribution"]]}
    return v


def boost(placed, k):
    out = []
    for p in placed.get("placement", []):
        t = p.get("type")
        if t == "minecraft:count":
            p = {**p, "count": scale(p["count"], k)}
        elif t == "minecraft:rarity_filter":
            p = {**p, "chance": max(1, round(p["chance"] / k))}
        out.append(p)
    return {**placed, "placement": out, MARK: k}


def main():
    for f in OUT.glob("*/worldgen/placed_feature/**/*.json"):
        if MARK in f.read_text("utf8"):
            f.unlink()
    jars = sorted(glob.glob(str(RUN / "mods/*.jar"))) + glob.glob(str(RUN / "libraries/net/minecraft/server/1.21.1-*/server-1.21.1-*-extra.jar"))
    done = {}
    for j in jars:
        with zipfile.ZipFile(j) as z:
            for n in z.namelist():
                m = re.match(r"data/([\w.-]+)/worldgen/placed_feature/(.+)\.json$", n)
                if not m:
                    continue
                fid = f"{m.group(1)}:{m.group(2)}"
                k = next((v for rx, v in BOOST.items() if re.fullmatch(rx, fid)), None)
                if not k or fid in done:
                    continue
                data = boost(json.loads(z.read(n)), k)
                dst = OUT / m.group(1) / "worldgen/placed_feature" / f"{m.group(2)}.json"
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_text(json.dumps(data, indent=1), "utf8")
                done[fid] = k
    for fid, k in sorted(done.items()):
        print(f"x{k:<5} {fid}")
    print(len(done), "placed features boosted")


if __name__ == "__main__":
    main()
