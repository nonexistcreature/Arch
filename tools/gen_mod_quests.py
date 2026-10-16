#!/usr/bin/env python3
"""quests_spec/<mod>.yaml -> quests_src/more/<file>_gen.yaml (then build_quests.py as usual).

A spec lists quests in the order and with the links *we* choose, and only a short «why» line written by us;
titles and descriptions come from the mod's own guide texts (lang files: ru_ru for RU, en_us for EN, or guide
markdown pages for English-only guides such as AE2), so quests cover what the mod's book covers and stay accurate.

Spec format:
  extends: ars                      # chapter to add to (or `chapter: {...}` like quests_src files)
  lang: [ars_nouveau]               # namespaces whose lang files are read (jar assets)
  autodoc: description              # optional: quests without doc use <autodoc>.<ns>.<first item path>;
                                    # or a list of templates like "item.{ns}.{path}.tooltip.summary"
  out: ars_gen                      # output file name (quests_src/more/<out>.yaml)
  quests:
    - id: ars_turret                # unique
      deps: [ars_apparatus]
      items: [ars_nouveau:basic_spell_turret, "minecraft:redstone*4"]   # item tasks (id*count); none -> checkmark
      tasks: [...]                  # extra raw tasks (kill, structure, ...)
      icon: ...                     # default: first item
      doc: page1.basic_spell_turret # lang key (relative to the first lang namespace), md:<path inside a jar> or ponder:<scene>
      doc2: ...                     # optional second paragraph
      why: {ru: "...", en: "..."}   # optional first line (written by us)
      text: {ru: "...", en: "..."}  # optional closing paragraph (written by us)
      title: {ru: "...", en: "..."} # optional, default = item name from lang
      subtitle: {ru: "...", en: "..."}
      roles: [mage]; shape: gear; rewards: [...]   # passed through
RU never shows an English guide paragraph when the spec has a Russian «why» line.
"""
import json
import re
import sys
import zipfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
JAR_DIRS = [ROOT / "tests/server_run/mods", ROOT / "tests/client_run/game/mods"]
FMT = re.compile(r"\$\([^)]*\)|§.|\{\{[^}]*\}\}")
NL = "\n"


def lang_for(namespaces):
    ru, en = {}, {}
    for ns in namespaces:
        for d in JAR_DIRS:
            for j in d.glob("*.jar"):
                try:
                    with zipfile.ZipFile(j) as z:
                        for loc, tgt in (("en_us", en), ("ru_ru", ru)):
                            n = f"assets/{ns}/lang/{loc}.json"
                            if n in z.namelist():
                                raw = z.read(n).decode("utf8", "replace")
                                try:
                                    tgt.update(json.loads(raw))
                                except json.JSONDecodeError:  # some mods ship broken lang json: read "key": "value" lines
                                    tgt.update({m.group(1): json.loads('"' + m.group(2) + '"')
                                                for m in re.finditer(r'^\s*"([^"]+)"\s*:\s*"((?:[^"\\]|\\.)*)"', raw, re.M)})
                except zipfile.BadZipFile:
                    pass
    return ru, en


def clean(t, limit=700):
    t = FMT.sub("", t or "").replace("\\n", NL).replace('\\"', '"').strip()
    t = re.sub(r"\[\[[^\]]*\]\]\s*", "", t)  # Twilight Forest note headers
    t = re.sub(r"\n{3,}", NL + NL, t)
    t = re.sub(r"(?<!\w)_([^_\n]+)_(?!\w)", r"\1", t)  # Create tooltip highlight markup
    if len(t) > limit:
        cut = t[:limit]
        t = cut[:max(cut.rfind(". "), cut.rfind("." + NL), limit // 2) + 1].strip()
    return t


def md_doc(path, limit=650):
    """First paragraphs of a guide page inside any jar, without markup: GuideME/AE2 markdown, IE manual .txt,
    or a Patchouli entry .json (`path.json#N` starts at page N; two pages are taken)."""
    path, _, page = path.partition("#")
    for d in JAR_DIRS:
        for j in d.glob("*.jar"):
            try:
                with zipfile.ZipFile(j) as z:
                    if path not in z.namelist():
                        continue
                    s = z.read(path).decode("utf8", "replace").replace("\r", "")
            except zipfile.BadZipFile:
                continue
            if path.endswith(".json"):
                pages = [x.get("text", "") for x in json.loads(s).get("pages", []) if isinstance(x, dict)]
                s = (NL + NL).join(x for x in pages[int(page or 0):int(page or 0) + 2] if x).replace("$(br)", NL + NL)
            if path.endswith(".txt"):  # Immersive Engineering manual: title, subtitle, then text with <br> and <&anchors>
                s = (NL + NL).join(s.split(NL)[2:]).replace("<br>", NL + NL)
            s = re.sub(r"<link;[^;>]*;([^>]*)>", lambda m: m.group(1), s).replace("<np>", NL + NL)
            s = re.sub(r'<ItemLink id="([^"]+)"[^>]*>', lambda m: m.group(1).split(":")[-1].replace("_", " "), s)
            s = re.sub(r"<[^>]+>", "", s)
            s = re.sub(r"\[([^\]]+)\]\([^)]*\)", lambda m: m.group(1), s)
            paras = [" ".join(x.split()) for x in re.split(r"\n\s*\n", s)]
            paras = [x for x in paras if x and not x.startswith("#") and not x.startswith("!")]
            return clean(NL.join(paras[:3]), limit)
    return ""


def item_name(iid, lang):
    ns, p = iid.split(":", 1)
    for k in (f"item.{ns}.{p}", f"block.{ns}.{p}", f"entity.{ns}.{p}"):
        if k in lang:
            return clean(lang[k], 120)
    return None


def main():
    for spec_path in [Path(a) for a in sys.argv[1:]] or sorted((ROOT / "quests_spec").glob("*.yaml")):
        spec = yaml.safe_load(open(spec_path, encoding="utf8"))
        ns = spec["lang"]
        ru, en = lang_for(ns)
        out_q = []
        missing = []
        for q in spec["quests"]:
            items = q.get("items") or []
            tasks = []
            for it in items:
                iid, _, cnt = str(it).partition("*")
                tasks.append({"type": "item", "item": iid, **({"count": int(cnt)} if cnt else {})})
            tasks += q.get("tasks", [])
            if not tasks:
                tasks = [{"type": "checkmark"}]

            def doc(key, lang):
                if not key:
                    return ""
                if key.startswith("md:"):  # guide pages: English, or a ru_ru copy of the page when the mod ships one
                    return md_doc(key[3:]) if lang is en else md_doc(key[3:].replace("/en_us/", "/ru_ru/")) if "/en_us/" in key else ""
                if key.startswith("ponder:"):  # Create-style ponder scene: its lines text_1..text_N, joined
                    sns, _, sname = key[7:].rpartition(":")  # ponder:<scene> or ponder:<namespace>:<scene>
                    scene = f"{sns or ns[0]}.ponder.{sname}"
                    lines = [clean(lang[f"{scene}.text_{i}"], 300) for i in range(1, 9) if f"{scene}.text_{i}" in lang]
                    return clean(" ".join(x if x.endswith((".", "!", "?")) else x + "." for x in lines), 600)
                full = key if (key.split(".")[0] in ns or key.startswith(("book.", "item.", "block.", "entity.", "tooltip.", "description.", "advancements.", "advancement.", "info.", "guide.", "spell.", "effect.", "com.", "jei.", "ability.", "lore."))) else f"{ns[0]}.{key}"
                alts = [full, full.replace(".page1.", ".page."), full.replace(".page.", ".page1.")]
                ok = [a for a in alts if len(lang.get(a, "")) > 12 and not re.search(r"%(\d\$)?[sd]", lang[a])]  # skip texts with %s slots
                return clean(lang[ok[0]]) if ok else ""

            res = {"id": q["id"], "tasks": tasks}
            for k in ("deps", "roles", "shape", "rewards", "pos", "optional", "repeatable"):
                if k in q:
                    res[k] = q[k]
            res["icon"] = q.get("icon") or (items[0].split("*")[0] if items else "minecraft:book")
            for loc, lang, other in (("ru", ru, en), ("en", en, None)):
                first = items[0].split("*")[0] if items else None
                title = (q.get("title") or {}).get(loc) or (item_name(first, lang) if first else None) \
                    or (item_name(first, other) if first and other else None) or q["id"]
                body = []
                why = (q.get("why") or {}).get(loc)
                if why:
                    body.append(f"**Зачем:** {why}" if loc == "ru" else f"**Why:** {why}")
                fb = other if (other and not why) else None  # RU: English guide text only when we wrote no RU line
                d1 = doc(q.get("doc"), lang) or (doc(q.get("doc"), fb) if fb else "")
                d2 = doc(q.get("doc2"), lang) or (doc(q.get("doc2"), fb) if fb else "")
                if q.get("doc") and not d1 and not why:
                    missing.append(f"{q['id']}({loc}): {q['doc']}")
                if not q.get("doc") and spec.get("autodoc") and first:  # e.g. autodoc: description -> description.<ns>.<path>
                    fns, fp = first.split(":", 1)
                    ad = spec["autodoc"] if isinstance(spec["autodoc"], list) else [spec["autodoc"]]
                    keys = [(t if "{" in t else t + ".{ns}.{path}").format(ns=fns, path=v) for t in ad
                            for v in (fp, re.sub(r"^(module_|basic_|advanced_|elite_|ultimate_)", "", fp))]
                    d1 = next((x for x in (doc(k, lang) or (doc(k, fb) if fb else "") for k in keys) if x), "")
                    if not d1:  # last resort: the mod's advancement about this item ("craft/obtain the X")
                        stem = re.sub(r"_(\d+|helmet|chestplate|leggings|boots)$", "", fp)
                        adv = re.compile(rf"advancements?\.{re.escape(fns)}\.[a-z0-9_.]*{re.escape(stem)}[a-z0-9_]*\.desc(ription)?$")
                        for src in (lang, fb) if fb else (lang,):
                            hit = next((k for k in sorted(src) if adv.match(k)), None)
                            if hit and not d1:
                                d1 = doc(hit, src)
                body += [x for x in (d1, d2) if x]
                extra = (q.get("text") or {}).get(loc)
                if extra:
                    body.append(extra)
                res[loc] = {"title": title, "subtitle": (q.get("subtitle") or {}).get(loc, ""), "text": NL.join(body) or title}
            out_q.append(res)
        doc_out = {k: spec[k] for k in ("extends", "chapter") if k in spec}
        doc_out["quests"] = out_q
        out = ROOT / "quests_src/more" / f"{spec['out']}.yaml"
        out.write_text("# GENERATED by tools/gen_mod_quests.py from " + spec_path.name + " - edit the spec, not this file" + NL
                       + yaml.safe_dump(doc_out, allow_unicode=True, sort_keys=False, width=200), "utf8")
        print(f"{spec_path.name}: {len(out_q)} quests -> {out.relative_to(ROOT)}" + (f"; missing docs: {missing}" if missing else ""))


if __name__ == "__main__":
    main()
