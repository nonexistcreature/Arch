#!/usr/bin/env python3
"""quests_spec/<mod>.yaml -> quests_src/more/<file>_gen.yaml (then build_quests.py as usual).

A spec lists quests in the order and with the links *we* choose, and only a short «why» line written by us;
titles and descriptions come from the mod's own guide texts (lang files: ru_ru for RU, en_us for EN), so quests
cover everything the mod's book covers and stay accurate.

Spec format:
  extends: ars                      # chapter to add to (or `chapter: {...}` like quests_src files)
  lang: [ars_nouveau]               # namespaces whose lang files are read (jar assets)
  out: ars_gen                      # output file name (quests_src/more/<out>.yaml)
  quests:
    - id: ars_turret                # unique
      deps: [ars_apparatus]
      items: [ars_nouveau:basic_spell_turret, "minecraft:redstone*4"]   # item tasks (id*count); none -> checkmark
      icon: ...                     # default: first item
      doc: page1.basic_spell_turret # lang key (relative to the first lang namespace, or absolute with a dot-prefix-free full key)
      doc2: page2.basic_spell_turret   # optional second paragraph
      why: {ru: "...", en: "..."}   # optional first line
      title: {ru: "...", en: "..."} # optional, default = item name from lang
      subtitle: {ru: "...", en: "..."}
      roles: [mage]; shape: gear; rewards: [...]   # passed through
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
                                tgt.update(json.loads(z.read(n).decode("utf8", "replace")))
                except zipfile.BadZipFile:
                    pass
    return ru, en


def clean(t, limit=700):
    t = FMT.sub("", t or "").replace("\\n", "\n").replace('\\"', '"').strip()
    t = re.sub(r"\n{3,}", "\n\n", t)
    if len(t) > limit:
        cut = t[:limit]
        t = cut[:max(cut.rfind(". "), cut.rfind(".\n"), limit // 2) + 1].strip()
    return t


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
                full = key if key.count(".") >= 2 and key.split(".")[0] in ns else f"{ns[0]}.{key}"
                alts = [full, full.replace(".page1.", ".page."), full.replace(".page.", ".page1.")]
                return next((clean(lang[a]) for a in alts if len(lang.get(a, "")) > 12), "")

            res = {"id": q["id"], "tasks": tasks}
            for k in ("deps", "roles", "shape", "rewards", "pos", "optional", "repeatable"):
                if k in q:
                    res[k] = q[k]
            res["icon"] = q.get("icon") or (items[0].split("*")[0] if items else "minecraft:book")
            for loc, lang, other in (("ru", ru, en), ("en", en, None)):
                title = (q.get("title") or {}).get(loc) or (item_name(items[0].split("*")[0], lang) if items else None) \
                    or (item_name(items[0].split("*")[0], other) if items and other else None) or q["id"]
                body = []
                why = (q.get("why") or {}).get(loc)
                if why:
                    body.append(f"**Зачем:** {why}" if loc == "ru" else f"**Why:** {why}")
                # no Russian page text: fall back to English only when we have no Russian «why» line of our own
                fb = other if (other and not why) else None
                d1 = doc(q.get("doc"), lang) or (doc(q.get("doc"), fb) if fb else "")
                d2 = doc(q.get("doc2"), lang) or (doc(q.get("doc2"), fb) if fb else "")
                if q.get("doc") and not d1 and not why:
                    missing.append(f"{q['id']}: {q['doc']}")
                body += [x for x in (d1, d2) if x]
                extra = (q.get("text") or {}).get(loc)
                if extra:
                    body.append(extra)
                res[loc] = {"title": title, "subtitle": (q.get("subtitle") or {}).get(loc, ""), "text": "\n".join(body) or title}
            out_q.append(res)
        doc_out = {k: spec[k] for k in ("extends", "chapter") if k in spec}
        doc_out["quests"] = out_q
        out = ROOT / "quests_src/more" / f"{spec['out']}.yaml"
        out.write_text("# GENERATED by tools/gen_mod_quests.py from " + spec_path.name + " — edit the spec, not this file\n"
                       + yaml.safe_dump(doc_out, allow_unicode=True, sort_keys=False, width=200), "utf8")
        print(f"{spec_path.name}: {len(out_q)} quests -> {out.relative_to(ROOT)}" + (f"; missing docs: {missing}" if missing else ""))


if __name__ == "__main__":
    main()
