# PROGRESS — память агента между сессиями

> Обновляй после каждого значимого шага. Формат записи: `YYYY-MM-DD — что сделано / что дальше`.

## Текущая фаза
Фазы 2–4 параллельно: контент собран (~250 модов), интеграция и квесты в работе. Деплой ждёт данных владельца.

## Статус фаз
- [x] 0 Подготовка (2026-10-14) — JDK 21, packwiz, NeoForge 21.1.259, Inno Setup 7.1, Prism-кеш — всё в `tools/bin/` (не в git)
- [x] 1 Скелет — `tools/resolve_pack.py`, `add_cf.py`, `check_pack.py`, `server_boot_test.py`, `cycle.sh`
- [~] 2 Контент волнами — ~250 модов (+зависимости ≈290 файлов), сервер грузится. Клиентский смоук (HeadlessMC) не сделан
- [~] 3 Интеграция — 12 своих предметов, 31 рецепт-рукопожатие, 8 зелий, баффы еды, Оберег путника, arkhaven-core 0.1.0
- [~] 4 Квесты — 19 глав, 251 квест RU+EN, генератор + валидатор; осталось: Город, Стройка, Великие стройки, Коллекции, С возвращением, Праздники; NPC Гавани, FancyMenu
- [ ] 5 Производительность и красота — пресеты есть (4), тюнинг/нагрузка не делались
- [~] 6 Установщик и сервер — `launcher/build.py` → `Arkhaven-Setup-0.1.0.exe` (проверен тихой установкой/удалением); `server/` (compose, бэкапы, рестарт, откат) написан, не развёрнут (нет доступа)
- [ ] 7 Финальная регрессия и передача

## Как продолжать (шпаргалка)
- Моды: правь `tools/modlist.txt` (Modrinth) / `tools/modlist_cf.txt` (CurseForge) → `tools/cycle.sh` (резолв + refresh + check + загрузка сервера + недостающие зависимости).
- Квесты: `quests_src/*.yaml` → `python tools/build_quests.py` → `python tools/validate_quests.py` (нужен `tests/out/registry.json` — обновляется копией `tests/server_run/kubejs/exported/registry.json` после загрузки).
- Свой мод: `core-mod/` → `tools/build_core.sh` (сборка + GameTests + копия jar в pack/mods + refresh).
- Установщик: `python launcher/build.py` (адреса — `launcher/release.json`).
- Команды на тестовом сервере: `python tools/server_boot_test.py --cmds "arkhaven status;arkhaven forecast"`.

## Последние тесты
- 2026-10-17 — 0.2.0: +26 аддонов Create (вкл. дубли), Relics, TFMG -> Community Edition (проверено: убранных блоков в мире нет), руды x1.5–2 (+ретроген Mekanism/IE), бонус-лут сундуков, Botany Pots для 166 модовых растений; квесты: главы create_paths (98) и create_power (37) + связки (Wizardry, Immersive TaCZ, Relics) — 2276 квестов, 0 ошибок, новые моды 100% ключевых вещей. Сервер-бут OK, клиент до меню и в мир OK.
- 2026-10-16 — оптимизация 0.1.7: бенч в движении на копии реального мира (`tools/bench_client.py --real <вариант>`), шейдер-профиль «lite» 135→192 FPS, подсказка про память (<6 ГБ = фризы), закрыта реклама EC2. Подробно — docs/reports/performance.md.
- 2026-10-14 — уровень 1 (check_pack) зелёный; уровень 2 (загрузка сервера ~70 c, 0 ошибок KubeJS); GameTests arkhaven-core 4/4; валидатор квестов 251/0 ошибок.

## Открытые проблемы
- Редкая гонка при загрузке сервера (1 из ~5): "unbound value create:chocolate_bucket" при инициализации реестров — подозрение на аддоны Create с шоколадом (create_confectionery / central_kitchen). Повторный старт проходит.
- Визуальная проверка названий квестов не автоматизирована (скриншот из игры не сработал; снимать рабочий стол нельзя — владелец за ПК).
- FPS: последний замер в одиночке ~100 медиана с шейдерами, цель 180 — финальная оптимизация в конце (владелец так решил), замеры ≤3 минут.
- Клиент не проверен запуском (нет HeadlessMC/аккаунта) — нужен клиентский смоук. Риск: клиентские моды/миксины (Iris+Sodium+Aeronautics, Fresh Animations).
- `ftbteams party create/force-add` в `50_quest_hooks.js` — синтаксис не проверен (нужен живой игрок).
- `ItemEvents.modifyTooltips` (client_scripts) не проверен на клиенте.
- Звёздный карп: падает в воду с метеоритом (не через рыбалку Tide).
- Botania нет на 1.21.1 → заменено (decisions.md).
- Кольцевой коллайдер (MMR) не сделан: экзотическая материя пока крафтится «временным» рецептом.
- Сеты брони (бонусы комплектов) из главы «Оружие» не реализованы.

## Журнал
- 2026-10-14 — Фаза 0–1, волны 1–10, сервер грузится (219→254 мода). Решения в `docs/reports/decisions.md`.
- 2026-10-14 — Квесты: генератор/валидатор, главы 0–18 (251). Алхимия (KubeJS эффекты/зелья). Рукопожатия. arkhaven-core 0.1.0 (оберег, метеор, разлом, режиссёр, зоны, Камень очага, команды, GameTests). Установщик собран. Серверные скрипты.
- 2026-10-14 — Владелец протестировал: исправлено «Безымянный» (id квестов), спавн на суше (LandSpawn + NeoOrigins без телепортов), убран Ksyxis (спавн на Y=-64), Every Compat/Quark, MCA пост-шейдер; +10 оптимизаторов; G1 вместо ZGC; память 12 ГБ; квесты 539; бонусы сетов брони; праздники; гиды Гавани (8 NPC); логотип ARKHAVEN; катастрофы не чаще раза в 3 реальных дня.
- 2026-10-14 — Дистрибуция: сервер на Windows в один клик (`server/windows/Arkhaven-Server-Setup.cmd`: JDK, NeoForge, админ из локального аккаунта, свой контроллер ZeroTier 10.77.0.1, автозапуск, бэкапы); Linux `install.sh` + `zerotier-host.sh`; Discover.jar (JRE не запускает .java, был баг), слушает все интерфейсы и проверяет localhost; `Arkhaven-Prism-Instance.zip`, `Arkhaven-Own-Launcher.zip` (`install-to-launcher.ps1` проверен на временной папке: NeoForge + 265 модов + профиль); галочка ZeroTier в установщике; pack_url → GitHub Pages nonexistcreature/Arch. Гайды: `server/КАК_РАЗВЕРНУТЬ.md`, `launcher/ИГРОКАМ.md`. Не проверено вживую: zerotier-host.ps1 (нужны права админа, ставит драйвер), полный прогон install.ps1.
- 2026-10-14 — Сервер развёрнут на ПК владельца (C:\Arkhaven, 245 модов, Done 23 c, админ Lopyx_0, ZeroTier 5de652dcca0e488b / 10.77.0.1). Баг: устаревший хеш servers.dat в index.toml отменял загрузку модов → индекс пересчитан, tools/verify_index.py в CI и build.py. Первый (ванильный) мир отложен в C:\Arkhaven\backups\world_vanilla_*. Релиз v0.1.0.
- 2026-10-15 — Волна 11 (TaCZ→Modrinth, TaCZ NPCs + вооружённые данжи WDA/D&T, Create Droneworks, Extreme Reactors, Small Ships), Almost Unified для стали. LandSpawn исправлен (не уносит со спавна, GameTest 5/5). Квесты 539 → 738: «Путь», «Боссы», «Данжи» (тип structure), «Атом», «Огнестрел», «Транспорт», «Пивоварня», «Create: дополнения», «Иные миры», «Бестиарий», «Дом», +AE2/TFMG/Mekanism Tools. Тестовый сервер перенесён на порт 25570 (25565 — живой сервер владельца). Сервер грузится 7 c, KubeJS 0 ошибок.
- 2026-10-15 — Челлендж: элиты по зонам (65_elites.js) + 6 развилок ролей (66_progression_gates.js), квесты «Вершины требуют друзей», «Элиты диких земель», 749 квестов. На ПК владельца порт 25565 занят посторонним сервером Paper (C:\Java\jdk-21…, paper.jar) — Arkhaven не стартует, пока Paper не закрыт или Arkhaven не переведён на 25566 (ждём решения владельца).
- 2026-10-15 — Квесты по гидам модов: `tools/gen_mod_quests.py` + `quests_spec/<мод>.yaml` (тексты авторов из lang/Ponder/Patchouli/мануала IE, наши строки «Зачем» для RU; `tools/add_why.py`). 738 → 1501 квест, 41 глава. Новые главы: Immersive Engineering, Сумеречный лес, Эфир, Катаклизм; дополнены Ars, AE2, Occultism, Mekanism, Create, Iron's, Mystical Agriculture, Productive Bees, MineColonies, TFMG. Везде — комплекты брони и оружие мода. Валидатор 0 ошибок. Не проверено в игре (тестовый сервер не запускался, пока владелец играет).
- 2026-10-16 — Волна 12 (по просьбе владельца): алкоголь — Kaleidoscope Tavern + World Liquor, Create: Alcohol Industry, Drink Beer Refill; 11 аддонов Create (Garnished, Mechanical Extruder, Tweaked Controllers, Structures Arise, Enchantable Machinery, Integrated Farming, Design n' Decor, Radars, Mobile Packages, Trading Floor, Pattern Schematics); WaterFrames (позже убран: конфликт WATERMeDIA с FancyMenu). Перебалансировано через kubejs/data: Highball (без творческого полёта), Jerk (без взрыва), ром таверны (без Дурного знамения/рейдов); конфиги: пиво не ломает блоки, нет бесконечной лавы из крана. Квесты +90 (алкоголь 52, аддоны Create 38) → 1591. Сервер грузится 99 с. Клиент проверен: главное меню за 76 с (v0.1.6).
- 2026-10-16 — Покрытие квестами по «ключевым вещам» (владелец: только то, что влияет на игру; декор/стройка/дубли не в счёт): quests_spec/key_items.yaml + tools/quest_coverage.py --key. Все 81 мод ≥ 80% (было 17% по всем полезным семействам). +600 квестов → 2102, ветка «Повар-усилитель» с точными баффами, предметы-«рукопожатия» arkhaven. Русский текст проверяет tools/check_quest_ru.py (0 нарушений). Не проверено в игре.
- 2026-10-20 — Живой сервер, фиксы по логам и жалобам: жалобная книга `/жалоба` `/report` (70_reports.js → `kubejs/reports.json` на сервере, оповещение игроков при входе); ключ Create исключён из FTB Ultimine (71_ultimine_wrench.js, жалоба shxtai: блоки пропадали); рецепт смазки Create filling → формат `neoforge:single`; 85 рецептов прокатки Vintage переписаны в формат createaddition 1.7 (`tools/fix_vintage_rolling.py` → kubejs/data/vintage); Almost Unified больше не трогает отливку Create Metallurgy (45 рецептов не грузились); табличка Create Deco. Проверено `/reload` на живом сервере: эти ошибки ушли. Остались безвредные: рецепты для отсутствующих модов (unusualend, kaleidoscope_cookery, modularbees) и ошибки KubeJS в шагах sequenced assembly Garnished/TaCZ/Netherless (ванильный парсер их грузит).
- 2026-10-20 — Create Ultimine 1.3.3 (ключ Create + FTB Ultimine, жалоба shxtai) вместо исключения ключа тегом; конфиг Airborne в паке (fogMaxThreshold 300, blazeBurnerMultiplier 1.5); сторожевой таймер max-tick-time=180000 (сервер висел 11 ч). Тест загрузки OK (10 с). ⚠ `tools/resolve_pack.py` сейчас опасен: он удаляет 33 мода волны 13 (их нет в modlist.txt) и обновляет 27 модов до версий под NeoForge 21.1.262 — сервер не стартует. Изменения откатил; моды добавлять через packwiz напрямую, пока modlist.txt не синхронизирован.
- 2026-10-21 — 0.2.3: волна 14 по обращению игрока (11 модов + DragonLib, решения в decisions.md), тест загрузки OK. Найдено, не сделано: Create Immersive TaCZ требует оружейный пак Create Armorer в /tacz (CurseForge, не помечен под 1.21.1) — без него не работают рецепты гильз; Crawl не проверен с анимациями Better Combat (только в клиенте).
