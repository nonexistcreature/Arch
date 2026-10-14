#!/usr/bin/env python3
"""Shared loader for quests_src: chapter files (*.yaml) + extensions (more/*.yaml with `extends: <chapter id>`)."""
from pathlib import Path
import yaml

SRC = Path(__file__).resolve().parent.parent / "quests_src"


def load_chapters():
    chapters = []
    for f in sorted(SRC.glob("*.yaml")):
        d = yaml.safe_load(f.read_text("utf8"))
        d["_file"] = f.name
        chapters.append(d)
    by_id = {c["chapter"]["id"]: c for c in chapters}
    for f in sorted((SRC / "more").glob("*.yaml")):
        d = yaml.safe_load(f.read_text("utf8"))
        target = by_id[d["extends"]]
        for q in d["quests"]:
            q["_file"] = "more/" + f.name
        target["quests"].extend(d["quests"])
    chapters.sort(key=lambda c: c["chapter"]["order"])
    return chapters
