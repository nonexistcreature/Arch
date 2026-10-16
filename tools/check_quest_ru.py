#!/usr/bin/env python3
"""Find generated quests whose Russian side is not Russian: the title is English (or the bare quest id), or the
body is empty or mostly Latin. Usage: check_quest_ru.py [--ids] (prints ids per file, exit 1 if any)."""
import glob
import os
import re
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def latin_heavy(t):
    return len(re.findall("[A-Za-z]", t)) > len(re.findall("[А-Яа-яЁё]", t))


def main():
    total = 0
    for f in sorted(glob.glob(os.path.join(ROOT, "quests_src", "more", "*_gen.yaml"))):
        d = yaml.safe_load(open(f, encoding="utf8"))
        bad_t = [q["id"] for q in d["quests"] if not re.search("[А-Яа-яЁё]{3}", q["ru"]["title"]) or q["ru"]["title"] == q["id"]]
        bad_b = [q["id"] for q in d["quests"] if q["ru"]["text"] == q["ru"]["title"] or latin_heavy(q["ru"]["text"])]
        if bad_t or bad_b:
            print(os.path.basename(f), "TITLE", bad_t, "BODY", bad_b)
            total += len(set(bad_t + bad_b))
    print("total", total)
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
