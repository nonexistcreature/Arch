#!/usr/bin/env python3
"""Pull a mod's own reference material out of its jar, as input for writing quests:
in-game guide pages (lang keys of doc/page/entry/ponder type, Modonomicon/Patchouli/GuideME files),
item names (ru/en) and the list of items. Writes tools/.cache/guides/<ns>.md.

Usage: guide_material.py <namespace> [<namespace> ...]   (jars are read from tests/server_run/mods and the client mods)
"""
import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "tools/.cache/guides"
JAR_DIRS = [ROOT / "tests/server_run/mods", ROOT / "tests/client_run/game/mods"]
DOC_KEY = re.compile(r"(\.page\d*\.|\.section\.|\.entry\.|\.category\.|\.ponder\.|\.guide\.|\.desc(ription)?$|_desc\.|\.tooltip\.|\.lore|\.info)")


def jars_for(ns):
    seen = set()
    for d in JAR_DIRS:
        for j in sorted(d.glob("*.jar")):
            if j.name in seen:
                continue
            try:
                with zipfile.ZipFile(j) as z:
                    if any(n.startswith(f"assets/{ns}/") or n.startswith(f"data/{ns}/") for n in z.namelist()):
                        seen.add(j.name)
                        yield j
            except zipfile.BadZipFile:
                pass


def load_json(z, name):
    try:
        return json.loads(z.read(name).decode("utf8", "replace"))
    except Exception:
        return {}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    reg = json.load(open(ROOT / "tests/out/registry.json", encoding="utf8"))
    for ns in sys.argv[1:]:
        en, ru, books = {}, {}, []
        for j in jars_for(ns):
            with zipfile.ZipFile(j) as z:
                names = z.namelist()
                en.update(load_json(z, f"assets/{ns}/lang/en_us.json"))
                ru.update(load_json(z, f"assets/{ns}/lang/ru_ru.json"))
                for n in names:  # guide books: modonomicon / patchouli / guideme markdown
                    low = n.lower()
                    if (("modonomicon/books" in low or "patchouli_books" in low) and low.endswith(".json") and "/en_us/" in low or "/entries/" in low) \
                            or ("guide" in low and low.endswith(".md") and ("/en_us" in low or "ru_ru" not in low)):
                        books.append((n, z.read(n).decode("utf8", "replace")))
        items = sorted(i for i in reg["item"] if i.startswith(ns + ":"))
        lines = [f"# {ns}: {len(items)} items, {len(en)} en keys, {len(ru)} ru keys, {len(books)} book files", ""]
        lines.append("## Items (id | ru | en)")
        for i in items:
            p = i.split(":")[1]
            k = next((f"{t}.{ns}.{p}" for t in ("item", "block") if f"{t}.{ns}.{p}" in en), None)
            lines.append(f"- {i} | {ru.get(k, '') if k else ''} | {en.get(k, '') if k else ''}")
        lines += ["", "## Guide / description keys (ru, else en)"]
        for k in sorted(en):
            if DOC_KEY.search(k) and len(en[k]) > 25:
                lines.append(f"- {k}: {ru.get(k) or en[k]}")
        if books:
            lines += ["", "## Book files"]
            for n, text in books[:400]:
                text = re.sub(r"\s+", " ", text)
                lines.append(f"### {n}\n{text[:1500]}")
        (OUT / f"{ns}.md").write_text("\n".join(lines), "utf8")
        print(f"{ns}: {len(items)} items, {sum(1 for k in en if DOC_KEY.search(k))} doc keys, {len(books)} book files -> {OUT / (ns + '.md')}")


if __name__ == "__main__":
    main()
