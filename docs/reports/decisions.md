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

## Убраны из списка (нет на 1.21.1 NeoForge / нет на Modrinth под этим именем)
smoothboot-reloaded, createutilities, create-factory-logistics, create-claims, aeronautics-dyeable-components, ars-technica, ars-instrumentum, emi-ae2, ftb-essentials/ranks (CF), mob-captured-in-a-bottle, villager-names, simple-weapons, aether-redux, deep-aether-extension, bosses-of-mass-destruction, goblin-traders, iron-chests, Let's Do Bakery/Brewery/Candlelight. Можно вернуть при появлении портов.

## Reese's Sodium Options убран
Несовместим с Sodium Options API (зависимость Sodium Extra) — клиент не стартовал. Меню настроек даёт Sodium Extra.

## Стороны зависимостей
Modrinth пометил Lithostitched как server-only, но Terralith требует его на клиенте. Резолвер теперь поднимает сторону обязательной зависимости до стороны мода, который её требует.

## Динамический свет отложен
Sodium Dynamic Lights тянет Sodium Options API, который требует Reese's Sodium Options, а тот объявляет несовместимость с Options API — клиент не стартует ни в одной комбинации. Оставлен Reese's Sodium Options, динамический свет — когда появится рабочий порт (LambDynamicLights требует Fabric API).

## Частота катастроф (решение владельца, 2026-10-14)
Метеориты, разломы, штормы/торнадо — **не чаще раза в 3 реальных дня**: arkhaven-core `events.minRealHoursBetweenDisasters=72` (общий кулдаун, реальное время), Weather2 `*_TimeBetweenInTicks=5184000` (72 ч серверных тиков, глобально), сила торнадо снижена (F3 8%, F4 3%, F5 1%). Звездопады остаются как зрелище; падения камней — только когда кулдаун прошёл.

## Спавн всегда на суше (решение владельца)
NeoOrigins: teleports_enabled=false, spawn_in_ocean=false. arkhaven-core LandSpawn: точка спавна мира переносится из воды на ближайшую сушу; первый вход и возрождение без кровати — на эту точку в Верхнем мире, для любой расы/класса.

## ID квестов
FTB Quests теряет переводы у объектов с id ≥ 0x8000000000000000 (знаковый long). Генератор теперь выдаёт только положительные id.
