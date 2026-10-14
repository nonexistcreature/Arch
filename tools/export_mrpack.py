#!/usr/bin/env python3
"""Export the packwiz pack as a Modrinth modpack: launcher/dist/Arkhaven-<version>.mrpack
Importable by Prism Launcher, Modrinth App, ATLauncher, GDLauncher and other launchers that read .mrpack.

- Modrinth mods: download link + hashes (sha1/size looked up via the Modrinth API by the sha512 we already have).
- CurseForge mods: link to the CurseForge CDN (all ours allow third-party downloads — packwiz-installer fetches them
  the same way). The jar is downloaded once into tools/.cache/cf to compute sha512/size and is checked against the
  sha1 in our metafile. Jars are NOT put into the archive.
- Everything else in the index (configs, quests, KubeJS, options, servers.dat, arkhaven-core) goes to overrides/.
Usage: export_mrpack.py [--version X]
"""
import hashlib
import json
import sys
import tomllib
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACK = ROOT / "pack"
CACHE = ROOT / "tools/.cache/cf"
UA = {"User-Agent": "arkhaven-build/1.0 (+https://github.com/nonexistcreature/Arch)"}


def http(url, data=None):
    req = urllib.request.Request(url, data=data, headers={**UA, **({"Content-Type": "application/json"} if data else {})})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def env_for(side):
    return {"client": "required" if side in ("both", "client") else "unsupported",
            "server": "required" if side in ("both", "server") else "unsupported"}


def cf_url(file_id, filename):
    return f"https://mediafilez.forgecdn.net/files/{file_id // 1000}/{file_id % 1000}/{urllib.parse.quote(filename)}"


def main():
    pack = tomllib.loads((PACK / "pack.toml").read_text("utf8"))
    version = sys.argv[sys.argv.index("--version") + 1] if "--version" in sys.argv else pack["version"]
    index = tomllib.loads((PACK / pack["index"]["file"]).read_text("utf8"))
    metas, overrides = [], []
    for f in index["files"]:
        (metas if f.get("metafile") else overrides).append(f["file"])

    mods = []
    for rel in metas:
        m = tomllib.loads((PACK / rel).read_text("utf8"))
        folder = str(Path(rel).parent).replace("\\", "/")
        mods.append((folder, m))

    # Modrinth: sha512 -> {sha1, size}
    mr = [m for _, m in mods if "url" in m["download"]]
    lookup = json.loads(http("https://api.modrinth.com/v2/version_files", json.dumps(
        {"hashes": [m["download"]["hash"] for m in mr], "algorithm": "sha512"}).encode()))
    files = []
    for folder, m in mods:
        d = m["download"]
        entry = {"path": f"{folder}/{m['filename']}", "env": env_for(m.get("side", "both"))}
        if "url" in d:
            ver = lookup.get(d["hash"])
            if not ver:
                sys.exit(f"Modrinth doesn't know {m['filename']} (sha512 {d['hash'][:12]}...)")
            fobj = next(x for x in ver["files"] if x["hashes"]["sha512"] == d["hash"])
            entry.update(hashes={"sha1": fobj["hashes"]["sha1"], "sha512": d["hash"]},
                         downloads=[d["url"]], fileSize=fobj["size"])
        else:
            cf = m["update"]["curseforge"]
            url = cf_url(cf["file-id"], m["filename"])
            jar = CACHE / f"{cf['file-id']}-{m['filename']}"
            if not jar.exists():
                CACHE.mkdir(parents=True, exist_ok=True)
                print("download", m["filename"])
                jar.write_bytes(http(url))
            b = jar.read_bytes()
            if hashlib.new(d["hash-format"], b).hexdigest() != d["hash"]:
                jar.unlink()
                sys.exit(f"hash mismatch for {m['filename']} from {url}")
            entry.update(hashes={"sha1": hashlib.sha1(b).hexdigest(), "sha512": hashlib.sha512(b).hexdigest()},
                         downloads=[url], fileSize=len(b))
        files.append(entry)

    mrindex = {
        "formatVersion": 1, "game": "minecraft", "versionId": version, "name": pack["name"],
        "summary": "Arkhaven — дружеская сборка: Create, магия, RPG, квесты. Сервер ищется сам.",
        "files": sorted(files, key=lambda e: e["path"]),
        "dependencies": {"minecraft": pack["versions"]["minecraft"], "neoforge": pack["versions"]["neoforge"]},
    }
    out = ROOT / f"launcher/dist/Arkhaven-{version}.mrpack"
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("modrinth.index.json", json.dumps(mrindex, ensure_ascii=False, indent=1))
        for rel in overrides:
            z.write(PACK / rel, "overrides/" + rel)
    n_cf = sum(1 for _, m in mods if "url" not in m["download"])
    print(f"built {out} — {len(files)} mods by link ({n_cf} CurseForge), {len(overrides)} files in overrides, "
          f"{out.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
