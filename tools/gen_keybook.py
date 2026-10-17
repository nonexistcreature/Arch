#!/usr/bin/env python3
"""Generates the pages of the "Arkhaven Keys" book (lang keys arkhaven.keybook.pN) from the sections below and
sets ARK_KEYBOOK_PAGES in kubejs/server_scripts/11_keybook.js. Keep in sync with kubejs/client_scripts/07_keybinds.js."""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
S = {
"ru_ru": [
 ("Клавиши Arkhaven", ["Кнопки модов мешали друг другу. Мы развели их по слоям:", "§lбез модификатора§r — то, что жмёшь всё время;", "§lAlt +§r — раса, голос, сумки;", "§lCtrl +§r — режимы брони."]),
 ("Каждый день", ["B — рюкзак", "G, H — аксессуары", "I — аксессуары Эфира", "L — квесты", "M — карта", "U — метки, Alt+U — новая", "P — дерево умений", "O — раса и класс", "Z — перекат", "` — жадная добыча (держать)", "K — шейдеры вкл/выкл"]),
 ("Раса и класс", ["Alt+1…Alt+4 — умения расы", "Alt+5 — умение класса", "Alt+K — ночное зрение", "O — что умеет раса"]),
 ("Голосовой чат", ["Caps Lock — говорить (держать)", "Alt+V — меню чата", "Alt+M — выключить микрофон"]),
 ("Iron's Spells", ["V — сотворить", "R — колесо заклинаний"]),
 ("Ars Nouveau", ["(с посохом или книгой в руке)", "C — выбор заклинания", "X — следующее", "N — книга заклинаний", "Y — способность шлема", "Alt+P — сумка Ars Elemental"]),
 ("Оружие TACZ", ["(с пушкой в руке)", "ЛКМ — выстрел", "ПКМ — прицел", "R — перезарядка", "Y — модификация", "N — режим огня", "X — зум прицела", "C — ползти", "боковая кнопка мыши — штык"]),
 ("Mekanism", ["Ctrl+H — режим шлема", "Ctrl+G — нагрудник", "Ctrl+J — поножи", "Ctrl+B — ботинки", "N — режим инструмента"]),
 ("Ранец и броня", ["J — ранец вкл/выкл", "Alt+J — зависание", "Ctrl+C/Y/V — шлем, грудь, ботинки Cataclysm", "Ctrl+F — оружие Cataclysm", "Ctrl+R — рывок Deep Aether"]),
 ("Сумки и мелочи", ["Alt+B, Alt+N, Alt+E — сумки Occultism", "X — колчан (с луком)", "Ctrl+K — склад Create", "Ctrl+L — сети Create", ". — эмоции", ", — позвать дракона"]),
 ("Building Gadgets", ["(с гаджетом в руке)", "Shift+G — меню", "Shift+H — якорь", "Shift+R — радиус", "Shift+U — отмена"]),
 ("Как поменять", ["Настройки → Управление → Привязки клавиш.", "Сверху поиск и фильтр конфликтов.", "Красная кнопка — на ней два действия. Это нормально, если они работают с разными предметами в руке, в меню или на транспорте."]),
],
"en_us": [
 ("Arkhaven Keys", ["Mod keys clashed, so we split them into layers:", "§lplain§r - things you press all the time;", "§lAlt +§r - origin, voice, bags;", "§lCtrl +§r - armor modes."]),
 ("Every day", ["B - backpack", "G, H - accessories", "I - Aether accessories", "L - quests", "M - map", "U - waypoints, Alt+U - new", "P - skill tree", "O - origin and class", "Z - combat roll", "` - vein mining (hold)", "K - shaders on/off"]),
 ("Origin and class", ["Alt+1...Alt+4 - origin powers", "Alt+5 - class power", "Alt+K - night vision", "O - what your origin can do"]),
 ("Voice chat", ["Caps Lock - talk (hold)", "Alt+V - chat menu", "Alt+M - mute microphone"]),
 ("Iron's Spells", ["V - cast", "R - spell wheel"]),
 ("Ars Nouveau", ["(caster or book in hand)", "C - spell selection", "X - next", "N - spell book", "Y - helmet ability", "Alt+P - Ars Elemental pouch"]),
 ("TACZ guns", ["(gun in hand)", "LMB - shoot", "RMB - aim", "R - reload", "Y - refit", "N - fire mode", "X - scope zoom", "C - crawl", "mouse side button - bayonet"]),
 ("Mekanism", ["Ctrl+H - helmet mode", "Ctrl+G - chestplate", "Ctrl+J - leggings", "Ctrl+B - boots", "N - held tool mode"]),
 ("Jetpack and armor", ["J - jetpack on/off", "Alt+J - hover", "Ctrl+C/Y/V - Cataclysm helmet, chest, boots", "Ctrl+F - Cataclysm weapon", "Ctrl+R - Deep Aether dash"]),
 ("Bags and misc", ["Alt+B, Alt+N, Alt+E - Occultism bags", "X - quiver (with a bow)", "Ctrl+K - Create stock", "Ctrl+L - Create networks", ". - emotes", ", - call your dragon"]),
 ("Building Gadgets", ["(gadget in hand)", "Shift+G - menu", "Shift+H - anchor", "Shift+R - range", "Shift+U - undo"]),
 ("Changing keys", ["Options > Controls > Key Binds.", "Search box and a conflicts filter on top.", "A red key has two actions. That is fine if they work with different items in hand, in a menu or in a vehicle."]),
]}
W, H = 19, 14   # chars per line, lines per page (written book)


def wl(line):
    n, cur = 0, 0
    for w in re.sub("§.", "", line).split(" "):
        if cur and cur + 1 + len(w) > W:
            n, cur = n + 1, len(w)
        else:
            cur += (1 if cur else 0) + len(w)
    return n + 1


def paginate(secs):
    pages, cur, used = [], [], 0
    for title, items in secs:
        need = wl(title) + 1 + sum(wl(i) for i in items[:3])
        if cur and used + need > H:
            pages.append(cur); cur, used = [], 0
        if cur:
            cur.append(""); used += 1
        cur.append("§l" + title + "§r"); used += wl(title)
        for it in items:
            if used + wl(it) > H:
                pages.append(cur); cur, used = ["§l" + title + "§r §7(…)§r"], wl(title) + 1
            cur.append(it); used += wl(it)
    pages.append(cur)
    return pages


out = {lk: paginate(secs) for lk, secs in S.items()}
n = max(len(p) for p in out.values())
for lk, pages in out.items():
    p = ROOT / f"pack/kubejs/assets/arkhaven/lang/{lk}.json"
    d = json.loads(p.read_text("utf8"))
    for k in [k for k in d if re.match(r"arkhaven\.keybook\.p\d+$", k)]:
        del d[k]
    for i in range(n):
        d[f"arkhaven.keybook.p{i + 1}"] = "\n".join(pages[i]) if i < len(pages) else ("§lУдачи!§r" if lk == "ru_ru" else "§lHave fun!§r")
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2), "utf8")
    print(lk, len(pages), "pages, lines:", [sum(wl(l) for l in pg) for pg in pages])
js = ROOT / "pack/kubejs/server_scripts/11_keybook.js"
js.write_text(re.sub(r"let ARK_KEYBOOK_PAGES = \d+", f"let ARK_KEYBOOK_PAGES = {n}", js.read_text("utf8")), "utf8")
