# Решения

## 2026-10-14 Chunky исключён (пока)
Distant Horizons 3.3.3 вызывает ChunkyProvider при загрузке чанка спавна на выделенном сервере → краш «Chunky is not loaded».
Альтернатива: прегенерация встроенным DH-генератором LOD / `/forceload`; вернуть Chunky, когда DH исправит порядок инициализации.

## 2026-10-14 Windows-хост для тестов, пакетный путь без HTTP
packwiz-installer на этой машине не подключается к localhost по HTTP (backlog), используем file:// URL — `tools/server_boot_test.py`.

## JEI [beta]
JEI для 1.21.1 публикуется как beta; нужна 19.53+ для FTB XMod Compat → берём beta (флаг `[beta]` в modlist.txt).

## Let's Do: Bakery/Brewery/Candlelight
Нет сборок 1.21.1 NeoForge на Modrinth → вне сборки; заменяем тем, что есть (Vinery, Meadow, HerbalBrews, Farm&Charm).

## EW2D исключён: mixin на dedicated-сервере падает (ClassNotFound extendedrenderer.particle.entity.EntityRotFX). Вернуть после проверки на новой версии.

## SSRD исключён: Distant Horizons 3.3.3 объявляет несовместимость с ssrd ≤1.8.6. Вернуть, когда выйдет SSRD >1.8.6.

## Botania отсутствует на 1.21.1 NeoForge
Ни Modrinth, ни CurseForge не дают сборку Botania под 1.21.1 NeoForge. Глава 13 «Botania» заменяется расширенной главой Ars Nouveau/Occultism; Gourmaryllis-рукопожатие → Ars «Mycelial Sourcelink» (еда → Source). Альтернатива: Nature's Aura (если найдётся) — в стретч.

## Клавиши
Квесты — L (ванильные «Достижения» отвязаны, они доступны из меню паузы), дерево умений — P, шейдеры — K/O (Iris), карта — M, вейнмайнер — `. Полная проверка конфликтов — в клиентском тесте (фаза 5).

## Кулинарные аддоны: убраны Cultural Delights и Expanded Delight
Дублируют сыр/соль/пиво/корицу Let's Do Meadow, Brewin' and Chewin' и Vinery (правило «один мод на категорию», лимит аддонов FD 5–8). Осталось: My Nether's, Ocean's, End's Delight, Farmer's Respite, Brewin' and Chewin', Slice & Dice + Let's Do (Vinery, Meadow, HerbalBrews, Farm & Charm).

## Убраны Create Diesel Generators и Create: New Age
Третий путь нефти/дизеля (уже есть Immersive Petroleum и TFMG) и второй путь «электричество+атом в Create» (есть Crafts & Additions и Mekanism). Правило «один мод на категорию».

## arkhaven-core в pack/mods (jar в git)
Свой мод не опубликован на Modrinth/CF; кладём собранный jar (~100 КБ) прямо в pack/mods, packwiz раздаёт его как обычный файл. Правило «не класть jar в git» относится к чужим модам.
