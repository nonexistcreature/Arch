#!/usr/bin/env python3
"""Generate arkhaven-core resources: blockstates, models, 16x16 textures, loot tables, tags, lang (RU/EN).
Re-runnable; overwrites generated files under core-mod/src/main/resources."""
import json, random
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "core-mod/src/main/resources"
A = RES / "assets/arkhaven_core"
D = RES / "data"
MOD = "arkhaven_core"


def wj(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", "utf8")


def noise_tex(base, accent, seed, pattern=None):
    rnd = random.Random(seed)
    img = Image.new("RGBA", (16, 16))
    for y in range(16):
        for x in range(16):
            f = 0.82 + rnd.random() * 0.3
            c = tuple(min(255, int(v * f)) for v in base)
            if pattern and pattern(x, y):
                c = accent
            img.putpixel((x, y), c + (255,))
    return img


def frame(x, y):
    return x in (0, 15) or y in (0, 15)


def ward_tex(tier, active, side):
    base = (70, 78, 92)
    glow = [(120, 200, 230), (170, 120, 240), (250, 214, 110)][tier - 1]
    if not active:
        glow = tuple(int(v * 0.45) for v in glow)
    def pat(x, y):
        if frame(x, y):
            return True
        if side:
            return (x in (7, 8) and 3 <= y <= 12) or (y in (7, 8) and 3 <= x <= 12)
        return (x - 7.5) ** 2 + (y - 7.5) ** 2 < 10
    img = noise_tex(base, glow, tier * 10 + active + side * 100, pat)
    if not active:
        return img
    for x in range(16):  # bright frame corners
        img.putpixel((x, 0), (255, 255, 255, 255)) if x % 5 == 0 else None
    return img


def main():
    tex = A / "textures/block"
    tex.mkdir(parents=True, exist_ok=True)
    for t in (1, 2, 3):
        name = f"ward_generator_t{t}"
        for active in (0, 1):
            suf = "_on" if active else ""
            ward_tex(t, active, True).save(tex / f"{name}_side{suf}.png")
            ward_tex(t, active, False).save(tex / f"{name}_top{suf}.png")
            wj(A / f"models/block/{name}{suf}.json", {"parent": "minecraft:block/cube_bottom_top", "textures": {
                "top": f"{MOD}:block/{name}_top{suf}", "bottom": f"{MOD}:block/{name}_top{suf}", "side": f"{MOD}:block/{name}_side{suf}"}})
        wj(A / f"blockstates/{name}.json", {"variants": {"active=false": {"model": f"{MOD}:block/{name}"},
                                                        "active=true": {"model": f"{MOD}:block/{name}_on"}}})
        wj(A / f"models/item/{name}.json", {"parent": f"{MOD}:block/{name}_on"})
        wj(D / f"{MOD}/loot_table/blocks/{name}.json", {"type": "minecraft:block", "pools": [{"rolls": 1, "entries": [
            {"type": "minecraft:item", "name": f"{MOD}:{name}"}], "conditions": [{"condition": "minecraft:survives_explosion"}]}]})

    noise_tex((92, 84, 78), (255, 170, 60), 7, lambda x, y: (x - 7.5) ** 2 + (y - 7.5) ** 2 < 6).save(tex / "hearth_stone.png")
    noise_tex((40, 36, 48), (150, 140, 175), 9, lambda x, y: (x * 7 + y * 3) % 11 == 0).save(tex / "meteorite_ore.png")
    for name in ("hearth_stone", "meteorite_ore"):
        wj(A / f"models/block/{name}.json", {"parent": "minecraft:block/cube_all", "textures": {"all": f"{MOD}:block/{name}"}})
        wj(A / f"blockstates/{name}.json", {"variants": {"": {"model": f"{MOD}:block/{name}"}}})
        wj(A / f"models/item/{name}.json", {"parent": f"{MOD}:block/{name}"})
    wj(D / f"{MOD}/loot_table/blocks/hearth_stone.json", {"type": "minecraft:block", "pools": [{"rolls": 1, "entries": [
        {"type": "minecraft:item", "name": f"{MOD}:hearth_stone"}]}]})
    # Meteorite ore drops KubeJS meteoric dust (2-4, fortune), silk touch keeps the ore.
    wj(D / f"{MOD}/loot_table/blocks/meteorite_ore.json", {"type": "minecraft:block", "pools": [{"rolls": 1, "entries": [{
        "type": "minecraft:alternatives", "children": [
            {"type": "minecraft:item", "name": f"{MOD}:meteorite_ore", "conditions": [{"condition": "minecraft:match_tool", "predicate": {
                "predicates": {"minecraft:enchantments": [{"enchantments": "minecraft:silk_touch", "levels": {"min": 1}}]}}}]},
            {"type": "minecraft:item", "name": "arkhaven:meteoric_dust", "functions": [
                {"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": 2, "max": 4}},
                {"function": "minecraft:apply_bonus", "enchantment": "minecraft:fortune", "formula": "minecraft:uniform_bonus_count", "parameters": {"bonusMultiplier": 1}},
                {"function": "minecraft:explosion_decay"}]}]}]}]})

    # Star atlas item texture
    (A / "textures/item").mkdir(parents=True, exist_ok=True)
    atlas = Image.new("RGBA", (16, 16))
    for y in range(2, 14):
        for x in range(2, 14):
            atlas.putpixel((x, y), (40, 50, 90, 255) if 3 <= x <= 12 and 3 <= y <= 12 else (150, 110, 60, 255))
    for (x, y) in ((5, 5), (9, 4), (7, 8), (11, 10), (4, 11), (10, 7)):
        atlas.putpixel((x, y), (255, 230, 140, 255))
    atlas.save(A / "textures/item/star_atlas.png")
    wj(A / "models/item/star_atlas.json", {"parent": "minecraft:item/generated", "textures": {"layer0": f"{MOD}:item/star_atlas"}})

    # Tags
    wj(D / "minecraft/tags/block/mineable/pickaxe.json", {"values": [f"{MOD}:ward_generator_t1", f"{MOD}:ward_generator_t2",
                                                                    f"{MOD}:ward_generator_t3", f"{MOD}:hearth_stone", f"{MOD}:meteorite_ore"]})
    wj(D / "minecraft/tags/block/needs_iron_tool.json", {"values": [f"{MOD}:meteorite_ore", f"{MOD}:ward_generator_t2", f"{MOD}:ward_generator_t3"]})
    for t in (1, 2, 3):
        vals = [{"id": f"arkhaven:ward_crystal_t{k}", "required": False} for k in range(t, 4)]
        wj(D / f"arkhaven/tags/item/ward_fuel/t{t}.json", {"values": vals})
    rift = ["minecraft:zombie", "minecraft:skeleton", "minecraft:spider", "minecraft:husk", "minecraft:stray", "minecraft:vindicator",
            "born_in_chaos_v1:dread_hound", "born_in_chaos_v1:spirit_guide", "born_in_chaos_v1:barrel_zombie",
            "born_in_chaos_v1:skeleton_thrasher", "born_in_chaos_v1:decrepit_skeleton"]
    wj(D / "arkhaven/tags/entity_type/rift_spawns.json", {"values": [r if r.startswith("minecraft:") else {"id": r, "required": False} for r in rift]})

    # Lang
    L = {
        "block.arkhaven_core.ward_generator_t1": ("Генератор оберега I", "Ward Generator I"),
        "block.arkhaven_core.ward_generator_t2": ("Генератор оберега II", "Ward Generator II"),
        "block.arkhaven_core.ward_generator_t3": ("Генератор оберега III", "Ward Generator III"),
        "block.arkhaven_core.hearth_stone": ("Камень очага", "Hearth Stone"),
        "block.arkhaven_core.meteorite_ore": ("Метеоритная руда", "Meteorite Ore"),
        "item.arkhaven_core.star_atlas": ("Звёздный атлас", "Star Atlas"),
        "entity.arkhaven_core.meteor": ("Метеорит", "Meteor"),
        "entity.arkhaven_core.rift": ("Разлом", "Rift"),
        "itemGroup.arkhaven_core": ("Arkhaven", "Arkhaven"),
        "tooltip.arkhaven_core.ward": ("Защищает радиус %s блоков от взрывов и метеоритов. Топливо — кристаллы оберега.",
                                       "Protects a %s-block radius from explosions and meteors. Fuel: ward crystals."),
        "message.arkhaven_core.ward.wrong_tier": ("Нужен кристалл оберега уровня %s или выше.", "Needs a ward crystal of tier %s or higher."),
        "message.arkhaven_core.ward.fuelled": ("Оберег заправлен: %s кристалл(ов).", "Ward fuelled: %s crystal(s)."),
        "message.arkhaven_core.ward.full": ("Оберег заправлен до отказа.", "The ward is full."),
        "message.arkhaven_core.ward.status": ("Оберег %s ур., радиус %s, топлива на %s мин. — %s", "Ward tier %s, radius %s, %s min of fuel — %s"),
        "message.arkhaven_core.ward.on": ("работает", "active"),
        "message.arkhaven_core.ward.off": ("выключен", "inactive"),
        "message.arkhaven_core.hearth.placed": ("Камень очага поставлен: в радиусе %s блоков враги не появляются.", "Hearth stone placed: no hostile spawns within %s blocks."),
        "message.arkhaven_core.zone.0": ("✦ Безопасная зона — здесь спокойно", "✦ Safe zone — all is calm here"),
        "message.arkhaven_core.zone.1": ("◇ Спокойные земли", "◇ Calm lands"),
        "message.arkhaven_core.zone.2": ("⚠ Дикие земли — будь начеку", "⚠ The wilds — stay alert"),
        "message.arkhaven_core.zone.3": ("☠ Опасные края", "☠ Dangerous lands"),
        "message.arkhaven_core.forecast.title": ("— Звёздный атлас (сила катастроф: %s) —", "— Star Atlas (disaster intensity: %s) —"),
        "message.arkhaven_core.forecast.shower_yes": ("Сегодня ночью ожидается звездопад ✨", "A meteor shower is expected tonight ✨"),
        "message.arkhaven_core.forecast.shower_no": ("Звездопада сегодня не будет.", "No meteor shower tonight."),
        "message.arkhaven_core.forecast.rift_yes": ("Небо неспокойно: ночью могут открыться разломы.", "The sky is restless: rifts may open tonight."),
        "message.arkhaven_core.forecast.rift_no": ("Разломов этой ночью не ждём.", "No rifts expected tonight."),
        "message.arkhaven_core.forecast.strike": ("Крупный метеорит: небо «набирает силу» — %s%%.", "Meteor strike: the sky is gathering strength — %s%%."),
        "message.arkhaven_core.forecast.strike_untrained": ("Крупные метеориты не падают, пока вы не прошли квест «Метеориты» (%s%%).", "No meteor strikes until you finish the \"Meteors\" quest (%s%%)."),
        "message.arkhaven_core.forecast.cooldown": ("Катастрофы не чаще раза в 3 дня. До следующей возможной: %s ч.", "Disasters at most once every 3 days. Next one possible in: %s h."),
        "message.arkhaven_core.forecast.active": ("Режиссёр событий активен.", "The event director is active."),
        "message.arkhaven_core.forecast.paused.intensity0": ("События выключены (сила 0).", "Events are off (intensity 0)."),
        "message.arkhaven_core.forecast.paused.vacation": ("Режим отпуска: мир отдыхает.", "Vacation mode: the world is resting."),
        "message.arkhaven_core.forecast.paused.noplayers": ("Никого нет — ничего не происходит.", "Nobody online — nothing happens."),
        "message.arkhaven_core.forecast.paused.grace": ("Льготный период: первые дни мир спокоен.", "Grace period: the first days are quiet."),
        "message.arkhaven_core.event.shower.title": ("Звездопад!", "Meteor Shower!"),
        "message.arkhaven_core.event.shower.subtitle": ("Посмотри на небо — и ищи упавшие камни", "Look up — and look for fallen stones"),
        "message.arkhaven_core.event.shower.tutorial": ("Первый звездопад: только красота и подарки", "First shower: just beauty and gifts"),
        "message.arkhaven_core.event.shower.chat": ("[Arkhaven] Начался звездопад. Мелкие метеориты падают в диких землях — в них метеоритная пыль. Если метеорит упадёт в воду, там может оказаться звёздный карп.",
                                                    "[Arkhaven] A meteor shower has begun. Small meteors fall in the wilds and leave meteoric dust. If one falls into water, a star carp might be there."),
        "message.arkhaven_core.event.rift.title": ("Ночь разломов", "Rift Night"),
        "message.arkhaven_core.event.rift.subtitle": ("Где-то рядом открылся разлом", "A rift has opened nearby"),
        "message.arkhaven_core.event.rift.tutorial": ("Учебный разлом: маленький и короткий", "Training rift: small and short"),
        "message.arkhaven_core.event.rift.chat": ("[Arkhaven] В 60–130 блоках от вас открылись разломы. Мобы не уходят от них далеко и исчезнут на рассвете. Закрой разлом — получишь осколки. Обереги II уровня не дают разломам открыться.",
                                                  "[Arkhaven] Rifts have opened 60–130 blocks from you. Their mobs stay close and vanish at dawn. Survive one for rift shards. Tier II wards keep rifts from opening."),
        "message.arkhaven_core.event.strike.title": ("Метеорит!", "Meteor Incoming!"),
        "message.arkhaven_core.event.strike.subtitle": ("Крупный метеорит падает — смотри на небо", "A big meteor is falling — watch the sky"),
        "message.arkhaven_core.event.strike.tutorial": ("Учебный метеорит упадёт далеко от построек", "Training meteor: it will land far from builds"),
        "message.arkhaven_core.event.strike.chat": ("[Arkhaven] Приближается метеорит! Светящийся столб в небе показывает, куда он упадёт. Генератор оберега сожжёт его в воздухе.",
                                                    "[Arkhaven] A meteor approaches! The glowing column in the sky shows where it will land. A Ward Generator burns it up in the air."),
        "message.arkhaven_core.event.strike.where": ("Место падения: X %s, Z %s. Время: %s мин %s с.", "Impact site: X %s, Z %s. Time: %s min %s s."),
        "message.arkhaven_core.event.strike.bar": ("Метеорит приближается", "Meteor approaching"),
        "message.arkhaven_core.event.tutorial_note": ("Это первое событие такого типа — учебное и безопасное. Подробности в главе «Стихии и защита».",
                                                      "This is the first event of its kind — a safe tutorial. Details in the \"Elements & Defence\" chapter."),
        "message.arkhaven_core.cmd.intensity": ("Сила катастроф: %s", "Disaster intensity: %s"),
        "message.arkhaven_core.cmd.vacation_on": ("Режим отпуска включён: события остановлены.", "Vacation mode on: events paused."),
        "message.arkhaven_core.cmd.vacation_off": ("Режим отпуска выключен.", "Vacation mode off."),
        "message.arkhaven_core.cmd.event": ("Событие запущено: %s", "Event started: %s"),
        "message.arkhaven_core.cmd.event_failed": ("Не удалось запустить событие %s (нужен игрок и подходящее место).", "Could not start event %s (needs a player and a suitable spot)."),
        "message.arkhaven_core.cmd.noplayers": ("Нет игроков онлайн — события не запускаются.", "No players online — events don't run."),
        "message.arkhaven_core.cmd.kit": ("Выдан демо-набор (%s предметов).", "Demo kit given (%s items)."),
    }
    for i, loc in enumerate(("ru_ru", "en_us")):
        wj(A / f"lang/{loc}.json", {k: v[i] for k, v in L.items()})
    from nbt_structure import write_empty_structure
    write_empty_structure(D / f"{MOD}/structure/empty.nbt", 9)
    print("core resources generated")


if __name__ == "__main__":
    main()
