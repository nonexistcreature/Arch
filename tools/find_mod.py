#!/usr/bin/env python3
"""Search Modrinth for neoforge 1.21.1 mods: find_mod.py "query" [...]"""
import json, sys, urllib.parse, urllib.request
UA = {"User-Agent": "arkhaven-pack/0.1 (danspite7@gmail.com)"}
for q in sys.argv[1:]:
    facets = json.dumps([["versions:1.21.1"], ["categories:neoforge"], ["project_type:mod"]])
    url = "https://api.modrinth.com/v2/search?" + urllib.parse.urlencode({"query": q, "facets": facets, "limit": 4})
    r = json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA)))
    print(f"## {q}")
    for h in r["hits"]:
        print(f"   {h['slug']:40} {h['title'][:40]:40} dl={h['downloads']}")
