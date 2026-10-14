#!/usr/bin/env python3
"""Resolve tools/modlist.txt against Modrinth -> pack/mods/*.pw.toml + index.toml + pack.toml.

Re-runnable. Format of modlist.txt: `slug | wave | role` (# comments).
Writes docs/reports/modlist_resolved.md and docs/reports/unresolved.md.
"""
import hashlib, json, os, sys, time, urllib.parse, urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACK = ROOT / "pack"
CACHE = ROOT / "tools" / ".cache"
CACHE.mkdir(exist_ok=True)
MC, LOADER, NEO = "1.21.1", "neoforge", "21.1.259"
UA = {"User-Agent": "arkhaven-pack/0.1 (danspite7@gmail.com)"}
BANNED = {"apotheosis", "apothic-enchanting", "apothic-spawners", "apothic-attributes",
          "immersive-portals", "immersiveportals", "epic-fight", "valkyrien-skies",
          "villagers-reborn", "journeymap", "rei", "refined-storage", "functional-storage",
          "travelers-backpack", "ftb-chunks", "vein-mining", "tough-as-nails", "corpse"}
BANNED_SUBSTR = ("apotheosis", "apothic")

def get(path, params=None):
    url = "https://api.modrinth.com/v2" + path
    if params:
        url += "?" + urllib.parse.urlencode({k: json.dumps(v) if isinstance(v, list) else v for k, v in params.items()})
    key = hashlib.md5(url.encode()).hexdigest()
    cf = CACHE / key
    if cf.exists() and time.time() - cf.stat().st_mtime < 6 * 3600:
        return json.loads(cf.read_text("utf8"))
    for attempt in range(4):
        try:
            data = json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30))
            cf.write_text(json.dumps(data), "utf8")
            return data
        except urllib.error.HTTPError as e:
            if e.code == 404: return None
            time.sleep(2 * (attempt + 1))
        except Exception:
            time.sleep(2 * (attempt + 1))
    return None

def best_version(pid):
    vs = get(f"/project/{pid}/version", {"game_versions": [MC], "loaders": [LOADER]})
    if not vs: return None
    rank = {"release": 0, "beta": 1, "alpha": 2}
    vs.sort(key=lambda v: (rank.get(v["version_type"], 3), -time.mktime(time.strptime(v["date_published"][:19], "%Y-%m-%dT%H:%M:%S"))))
    return vs[0]

def side_of(p):
    c, s = p["client_side"], p["server_side"]
    if s == "unsupported": return "client"
    if c == "unsupported": return "server"
    return "both"

def toml_str(s): return json.dumps(s, ensure_ascii=False)

def write_pw(slug, p, v, side):
    f = next((x for x in v["files"] if x.get("primary")), v["files"][0])
    txt = (f'name = {toml_str(p["title"])}\nfilename = {toml_str(f["filename"])}\nside = "{side}"\n\n'
           f'[download]\nurl = {toml_str(f["url"])}\nhash-format = "sha512"\nhash = "{f["hashes"]["sha512"]}"\n\n'
           f'[update]\n[update.modrinth]\nmod-id = "{p["id"]}"\nversion = "{v["id"]}"\n')
    (PACK / "mods" / f"{slug}.pw.toml").write_text(txt, "utf8", newline="\n")

def parse_list():
    out = []
    for line in (ROOT / "tools" / "modlist.txt").read_text("utf8").splitlines():
        line = line.split("#")[0].strip()
        if not line: continue
        parts = [x.strip() for x in line.split("|")]
        parts += [""] * (3 - len(parts))
        out.append(tuple(parts[:3]))
    return out

def main():
    keep = set()
    for f in (PACK / "mods").glob("*.pw.toml"):
        if "[update.modrinth]" in f.read_text("utf8"): f.unlink()
        else: keep.add(f.name[:-8])  # curseforge / manual entries are preserved
    wanted = parse_list()
    resolved, unresolved, seen_ids = {}, [], {}
    queue = [(s, w, r, None) for s, w, r in wanted]
    while queue:
        slug, wave, role, via = queue.pop(0)
        p = get(f"/project/{slug}")
        if not p:
            unresolved.append((slug, wave, "нет проекта на Modrinth", via)); continue
        slug = p["slug"]
        if slug in resolved or p["id"] in seen_ids or slug in keep: continue
        if slug in BANNED or any(b in slug for b in BANNED_SUBSTR):
            unresolved.append((slug, wave, "ЗАПРЕЩЁН", via)); continue
        if p["project_type"] != "mod":
            unresolved.append((slug, wave, f"тип {p['project_type']}", via)); continue
        v = best_version(p["id"])
        if not v:
            unresolved.append((slug, wave, f"нет версии {MC}+{LOADER}", via)); continue
        side = side_of(p)
        seen_ids[p["id"]] = slug
        resolved[slug] = dict(title=p["title"], version=v["version_number"], type=v["version_type"],
                              side=side, wave=wave, role=role or (f"зависимость {via}" if via else ""),
                              updated=v["date_published"][:10], dep=bool(via), id=p["id"], v=v, p=p)
        for d in v.get("dependencies", []):
            if d["dependency_type"] == "required" and d.get("project_id") and d["project_id"] not in seen_ids:
                queue.append((d["project_id"], wave, "", slug))
    # drop anything that depends on banned/unresolvable required dep
    changed = True
    while changed:
        changed = False
        bad = {u[0] for u in unresolved}
        for slug, r in list(resolved.items()):
            for d in r["v"].get("dependencies", []):
                if d["dependency_type"] != "required": continue
                dp = d.get("project_id")
                if dp and dp not in seen_ids and (get(f"/project/{dp}") or {}).get("slug") not in keep:
                    resolved.pop(slug); unresolved.append((slug, r["wave"], "зависимость не разрешилась", None)); changed = True; break
    for slug, r in resolved.items():
        write_pw(slug, r["p"], r["v"], r["side"])
    # index.toml (overwritten by `packwiz refresh` afterwards)
    lines = ['hash-format = "sha256"\n']
    for f in sorted((PACK / "mods").glob("*.pw.toml")):
        h = hashlib.sha256(f.read_bytes()).hexdigest()
        lines.append(f'[[files]]\nfile = "mods/{f.name}"\nhash = "{h}"\nmetafile = true\n')
    idx = "\n".join(lines)
    (PACK / "index.toml").write_text(idx, "utf8", newline="\n")
    (PACK / "pack.toml").write_text(
        f'name = "Arkhaven"\nauthor = "Arkhaven"\nversion = "0.1.0"\npack-format = "packwiz:1.1.0"\n\n'
        f'[index]\nfile = "index.toml"\nhash-format = "sha256"\nhash = "{hashlib.sha256(idx.encode()).hexdigest()}"\n\n'
        f'[versions]\nminecraft = "{MC}"\nneoforge = "{NEO}"\n', "utf8", newline="\n")
    rep = ["# modlist_resolved (авто, tools/resolve_pack.py)\n", f"Всего: **{len(resolved)}** (явных: {sum(not r['dep'] for r in resolved.values())}, зависимостей: {sum(r['dep'] for r in resolved.values())})\n",
           "| slug | название | версия | тип | сторона | волна | роль | обновлён |", "|---|---|---|---|---|---|---|---|"]
    for s, r in sorted(resolved.items()):
        rep.append(f"| {s} | {r['title']} | {r['version']} | {r['type']} | {r['side']} | {r['wave']} | {r['role']} | {r['updated']} |")
    (ROOT / "docs/reports/modlist_resolved.md").write_text("\n".join(rep) + "\n", "utf8")
    un = ["# unresolved\n", "| slug | волна | причина | кем требуется |", "|---|---|---|---|"]
    for s, w, why, via in unresolved: un.append(f"| {s} | {w} | {why} | {via or ''} |")
    (ROOT / "docs/reports/unresolved.md").write_text("\n".join(un) + "\n", "utf8")
    print(f"resolved {len(resolved)}, unresolved {len(unresolved)}")
    for u in unresolved: print("  x", u)

if __name__ == "__main__":
    main()
