#!/usr/bin/env python3
"""One-command release (docs/09_ROADMAP.md DoD #6):
  python tools/release.py 0.2.0 "Короткий список изменений" ["Short changelog in English"]

Steps: build quests + validate -> core mod (+GameTests) -> packwiz refresh -> level 1 check -> server boot test
-> bump pack.toml version -> "What's new" quest -> rebuild installer -> publish -> git tag.
Publishing target comes from launcher/release.json "publish":
  {"type": "git", "remote": "pages"}               push pack/ to a GitHub Pages branch
  {"type": "ssh", "host": "user@server", "path": "/opt/arkhaven/pack"}   rsync pack/ to the home server (Caddy serves it)
  missing -> skipped with a warning (still builds everything).
Players get the update on next launch (packwiz pre-launch); the server picks it up on restart.
"""
import json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable


def run(*cmd, cwd=ROOT, check=True):
    print("$", " ".join(map(str, cmd)))
    return subprocess.run([str(c) for c in cmd], cwd=cwd, check=check)


def bump(version):
    p = ROOT / "pack/pack.toml"
    p.write_text(re.sub(r'^version = ".*"$', f'version = "{version}"', p.read_text("utf8"), flags=re.M), "utf8", newline="\n")
    r = ROOT / "launcher/release.json"
    d = json.loads(r.read_text("utf8")); d["version"] = version
    r.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", "utf8")


def whats_new(version, ru, en):
    f = ROOT / "quests_src/23_welcome_back.yaml"
    qid = "wb_new_" + version.replace(".", "_")
    text = f.read_text("utf8")
    if qid in text:
        return
    text += f"""
  - id: {qid}
    deps: [wb_start]
    icon: minecraft:writable_book
    tasks: [{{type: checkmark}}]
    ru:
      title: "Что нового: {version}"
      text: |
        {ru}
    en:
      title: "What's New: {version}"
      text: |
        {en}
"""
    f.write_text(text, "utf8")


def publish(cfg):
    pub = cfg.get("publish")
    if not pub:
        print("WARN: launcher/release.json has no 'publish' target - skipping upload")
        return
    if pub["type"] == "ssh":
        run("rsync", "-az", "--delete", "pack/", f"{pub['host']}:{pub['path']}/")
    elif pub["type"] == "git":
        run("git", "subtree", "push", "--prefix", "pack", pub["remote"], pub.get("branch", "gh-pages"))


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    version, ru = sys.argv[1], sys.argv[2]
    en = sys.argv[3] if len(sys.argv) > 3 else ru
    whats_new(version, ru, en)
    run(PY, "tools/build_quests.py")
    run(PY, "tools/validate_quests.py")
    run("bash", "tools/build_core.sh")
    bump(version)
    run("tools/bin/packwiz.exe", "refresh", cwd=ROOT / "pack")
    run(PY, "tools/check_pack.py")
    run(PY, "tools/server_boot_test.py", "--timeout", "600")
    run(PY, "launcher/build.py")
    publish(json.loads((ROOT / "launcher/release.json").read_text("utf8")))
    run("git", "add", "-A")
    run("git", "commit", "-m", f"Release {version}", check=False)
    run("git", "tag", f"v{version}", check=False)
    print(f"Release {version} done. Restart the server: sudo systemctl restart arkhaven")


if __name__ == "__main__":
    main()
