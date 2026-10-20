"""Vintage ships its Crafts & Additions rolling recipes in the old format (input/result), which
createaddition 1.7 no longer reads, so all of them fail to load. This rewrites each one into the
current format (ingredients/results) as a datapack override under pack/kubejs/data/vintage/.

Usage: python tools/fix_vintage_rolling.py <path to vintage-*.jar>
Re-run after updating Vintage; if Vintage fixes the format upstream, delete the generated folder.
"""
import json
import pathlib
import sys
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "pack" / "kubejs" / "data" / "vintage" / "recipe" / "rolling"
PREFIX = "data/vintage/recipe/rolling/"


def convert(recipe: dict) -> dict | None:
    if recipe.get("type") != "createaddition:rolling" or "input" not in recipe:
        return None
    fixed = {"type": "createaddition:rolling", "ingredients": [recipe["input"]], "results": [recipe["result"]]}
    if "neoforge:conditions" in recipe:
        fixed["neoforge:conditions"] = recipe["neoforge:conditions"]
    return fixed


def main() -> None:
    jar = zipfile.ZipFile(sys.argv[1])
    OUT.mkdir(parents=True, exist_ok=True)
    count = 0
    for name in jar.namelist():
        if not name.startswith(PREFIX) or not name.endswith(".json"):
            continue
        fixed = convert(json.loads(jar.read(name)))
        if fixed is None:
            continue
        (OUT / name[len(PREFIX):]).write_text(json.dumps(fixed, indent=2) + "\n", encoding="utf-8")
        count += 1
    print(f"wrote {count} rolling overrides to {OUT}")


if __name__ == "__main__":
    main()
