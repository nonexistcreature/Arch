# 02 — Список модов по системам

Обозначения:
- ✅ — версия под 1.21.1 NeoForge подтверждена при подготовке ТЗ (октябрь 2026);
- 🔎 — почти наверняка есть, **проверь** через API перед добавлением;
- ⚠ — неофициальный порт: допустим, но отметь в отчёте и следи за крашами;
- (опц.) — добавлять, только если бюджет FPS/модов позволяет после основных волн.

Библиотеки (Architectury, Balm, GeckoLib, Citadel, Curios/Accessories, Kotlin for Forge, Moonlight,
Puzzles Lib, Cloth Config, YACL, Fzzy, CoroUtil, Veil и т.п.) подтягиваются как зависимости
автоматически — их не перечисляем. Не ставь библиотеку, которую никто не требует.

Итоговый, разрешённый список с версиями агент ведёт в `docs/reports/modlist_resolved.md`
(таблица: мод, версия, источник, сторона, роль, статус, примечания).

---

## A. Правило «один мод на категорию»

| Категория | Выбор | НЕ ставить вместе с ним |
|---|---|---|
| Рецепты | EMI (+ JEI как бэкенд плагинов) | REI |
| Карта | Xaero's Minimap + World Map | JourneyMap, FTB Chunks-карта, Antique Atlas |
| Приваты | Open Parties and Claims (OPAC) | FTB Chunks |
| Вейнмайнер | FTB Ultimine | Vein Mining, OreExcavation |
| Рюкзаки | Sophisticated Backpacks | Traveler's Backpack |
| Хранилище блоками | Sophisticated Storage | Functional Storage, Tom's Storage |
| Цифровое хранилище | Applied Energistics 2 | Refined Storage |
| Надгробие | GraveStone Mod | Corail Tombstone, Corpse |
| Физика транспорта | Create Aeronautics (Sable) | Valkyrien Skies + Eureka |
| Деревенские NPC | MCA Reborn | Villagers Reborn, Guard Villagers |
| Загрязнение | Airborne | Pollution of the Realms, AdPother |
| Рыбалка (ядро) | Tide 2 | Stardew Fishing (как отдельная система) |
| Боёвка ближнего боя | Better Combat (+ Combat Roll) | Epic Fight |
| Огнестрел | TaCZ ⚠ | Point Blank, Scorched Guns |
| Тултипы | Legendary Tooltips | — |
| Порт Alex's Mobs | ровно один из портов ⚠ | второй порт (никогда оба) |
| Расы | NeoOrigins | Origins Legacy: NeoForged (только как запасной) |
| Классы/умения | Pufferfish's Skills (+ Attributes) | другие системы уровней (Project MMO, RPG-классы с атрибутами-дублями) |
| Контроль спауна | In Control! | другие спаун-менеджеры |
| Крюки-кошки | Create Grappling Hooks + один ранний классический (Grappling Hook: Neo) | третий мод крюков |
| Температура/жажда | нет (опция Cold Sweat — выкл.) | Tough As Nails |
| Зачарование/лут-аффиксы | ванильное зачарование + Create Enchantment Industry | **Apotheosis и всё его семейство — ЗАПРЕЩЕНО** (см. ниже) |

### ⛔ Запрещённые моды (решение владельца, не обсуждается)
- **Apotheosis** и всё его семейство: Apothic Enchanting, Apothic Spawners, Apothic Attributes,
  любые аддоны Apotheosis. Причина: ломает баланс игры.
- Если какой-то мод требует один из них как зависимость — этот мод **не ставим**, ищем замену
  и пишем в `docs/reports/decisions.md`. `tools/check_pack.py` падает, если находит запрещённый мод.
- Также не ставим: Immersive Portals, Epic Fight, Valkyrien Skies, Villagers Reborn (см. 01).

---

## B. Производительность и стабильность (обе стороны, если не указано)

✅ Sodium (NeoForge) · ✅ Iris · 🔎 Sodium Extra · ✅ Reese's Sodium Options · ✅ Lithium ·
🔎 ModernFix · 🔎 FerriteCore · 🔎 ImmediatelyFast (клиент) · 🔎 Entity Culling (клиент) ·
🔎 More Culling (клиент) · ✅ AllTheLeaks · 🔎 Clumps · 🔎 Let Me Despawn · 🔎 AI Improvements ·
🔎 Async Locator · 🔎 Structure Layout Optimizer · 🔎 BadOptimizations (клиент) ·
🔎 Dynamic FPS (клиент) · 🔎 Model Gap Fix (клиент) · 🔎 FastWorkbench/FastSuite ·
🔎 C2ME (если есть NeoForge-сборка; иначе пропустить) · ✅ Distant Horizons (клиент + сервер) ·
🔎 spark · 🔎 Chunky (сервер, прегенерация) · ✅ Crash Assistant (клиент, понятные краши) ·
🔎 Smooth Boot / аналог для быстрого старта.

## C. Мир: генерация, биомы, структуры, измерения

- Рельеф и биомы: 🔎 **Tectonic** + 🔎 **Terralith** (ванильные блоки — лучше всего выглядят с
  шейдерами). Нижний мир: 🔎 Incendium или Amplified Nether ✅. Энд: 🔎 Nullscape.
- Сезоны: 🔎 **Serene Seasons** (сезонные посевы + теплицы из стекла их обходят).
- Деревни: 🔎 ChoiceTheorem's Overhauled Village (CTOV), 🔎 Towns and Towers.
- Данжи и структуры: 🔎 YUNG's (Better Dungeons, Mineshafts, Strongholds, Desert/Jungle Temples,
  Witch Huts, Ocean Monuments, Nether Fortresses, Bridges, Extras), 🔎 When Dungeons Arise
  (+ Seven Seas), 🔎 Dungeons and Taverns, 🔎 Repurposed Structures, 🔎 Explorify,
  ✅ **Lootr** (лут в сундуках у каждого игрока свой — важно для кооператива),
  🔎 Marston's Fallen Stars (места падения метеоритов в генерации).
- Измерения: 🔎 **Twilight Forest**, 🔎 **The Aether**, 🔎 Deeper and Darker, 🔎 Undergarden,
  🔎 The Bumblezone (пчёлы), 🔎 Blue Skies (опц.).
- Космос (опц., фаза 8): 🔎 Northstar (Create-космос; есть мост совместимости с Sable/Iris/DH).

## D. Еда, кулинария, садоводство

- Ядро: 🔎 **Farmer's Delight** + аддоны: ✅ My Nether's Delight, 🔎 Ocean's Delight,
  🔎 End's Delight, 🔎 Cultural Delights, 🔎 Expanded Delight, 🔎 Farmer's Respite (чай),
  🔎 Brewin' and Chewin', 🔎 Create Slice & Dice (автоматизация FD через Create).
  Брать только аддоны с живой версией 1.21.1; цель 5–8 штук, не больше.
- Уютная серия 🔎 **Let's Do**: Vinery (вино), Bakery (выпечка), Brewery (пивоварня с мини-играми),
  Meadow (сыр, альпийские животные), Candlelight (сервировка, ужины), HerbalBrews (чаи),
  Farm & Charm (фермерство, корма), Beachparty (опц.).
- ✅ **Cooking for Blockheads** (кухня-мультиблок, готовит из содержимого холодильников).
- 🔎 **Spice of Life: Carrot Edition** — новые блюда = доп. сердца. Главный мотиватор кулинарии.
- Растения: 🔎 Botany Pots, 🔎 Mystical Agriculture (+ Mystical Agradditions — опц.),
  🔎 Fruit Trees / Fruitful Fun (что живое на 1.21.1), 🔎 Supplementaries (плантеры, декор),
  🔎 Bonsai Trees (опц.).
- ✅ **Almost Unified** — объединяет дубликаты (помидоры, рис, металлы и т.п.) в один предмет.

## E. Животные, питомцы, разведение, рыбалка

- Существа: ⚠ **Alex's Mobs** (ровно один порт; предпочесть «Alex's Mobs (Unofficial Port)» от
  Raguto как самый популярный, при проблемах — Alex's Mobs Neo), 🔎 Naturalist,
  🔎 Friends & Foes, 🔎 Critters and Companions.
- Разведение/генетика: 🔎 **Productive Bees** (пчелиная генетика → ресурсы),
  🔎 **Dragon Mounts: Legacy** (разведение драконов разных пород, езда),
  🔎 мод генетики ванильных животных (Genetic Animals или аналог — что живо на 1.21.1),
  Let's Do Meadow (альпийский скот).
- Питомцы QoL: 🔎 мод на команды/сидение питомцев и защиту от урона своих (например,
  «Tameable/Pet tweaks» — найти актуальный), 🔎 Comforts (спальники).
- Рыбалка: ✅ **Tide 2** (100+ рыб, журнал, мини-игра, удочки с наживкой), 🔎 Aquaculture 2 +
  ✅ Fishing Rod Compat (переводит удочки Aquaculture на систему Tide), ✅ Fintastic Supreme (опц.).
- Опционально по выбору владельца: 🔎 Cobblemon (по умолчанию ВЫКЛ).

## F. Техника и автоматизация

- ✅ **Create 6** + аддоны: ✅ **Create Aeronautics** (Simulated / Aeronautics / Offroad) + ✅ **Sable**,
  аддоны Aeronautics (проверить каждый): Automated Logistics, Claims, Gadgets & Gizmos,
  Dyeable Components, Kinetic Grip, ✅ Waystones: Sable, ✅ Separate Sable Render Distance (дальность
  отрисовки кораблей с Distant Horizons), ✅ Iris Veil Compat (исправляет отрисовку Aeronautics
  под шейдерами). Плюс: 🔎 Create Crafts & Additions (мост в FE), 🔎 Steam 'n' Rails,
  ✅ Create Big Cannons, 🔎 Create Enchantment Industry, 🔎 Create Deco, 🔎 Create Connected,
  🔎 Create Copycats+, 🔎 Create: Interiors (сиденья), 🔎 Create: Deep Seas (корабли/подлодки — проверить).
- 🔎 **Create: The Factory Must Grow (TFMG)** — нефть, сталь, дизель (кормит Airborne загрязнением).
- 🔎 **Mekanism** + Generators (деление, термояд, турбины) + Tools. SPS/антиматерия = «ускоритель».
- 🔎 **Immersive Engineering** + ✅ Immersive Petroleum — огромные красивые мультиблоки.
- 🔎 **Applied Energistics 2** + ExtendedAE + MEGA Cells + Applied Mekanistics + AE2 Wireless Terminals.
- 🔎 **Modular Machinery Reborn** (мегапостройки из JSON — см. 03). Запасной: Custom Machinery.
- (опц.) 🔎 PneumaticCraft: Repressurized (дроны, лифты), 🔎 Industrial Foregoing — только если
  после фазы 5 останется бюджет и найдётся незакрытая петля.

## G. Магия

- 🔎 **Ars Nouveau** + Ars Elemental + 🔎 Ars Creo (мост с Create) + ✅ Ars Ocultas (опц.)
- 🔎 **Iron's Spells 'n Spellbooks** (боевая магия, школы, боссы)
- 🔎 **Botania** (мана, функциональные цветы — Gourmaryllis ест еду!)
- ✅ **Occultism** (ритуалы, духи-слуги для автоматизации)
- 🔎 Theurgy или Nature's Aura (опц., одно из)

## H. Враги, боссы, оружие, броня

- Боссы/враги: 🔎 **L_Ender's Cataclysm**, 🔎 **Mowzie's Mobs**, 🔎 Born in Chaos, 🔎 Aquamirae,
  🔎 Bosses of Mass Destruction (опц.), 🔎 Enhanced Celestials (кровавая/урожайная/голубая луна).
- Огнестрел: ⚠ **TaCZ (Unofficial NeoForge Port)** + ✅ TaCZ Pack Upgrader (для ганпаков),
  ⚠ LesRaisins Tactical Equipements (метательное, нож), ⚠ Create: TaCZ (патроны на Create).
  Требует Veil ≥ 3.1.2 (иначе конфликт).
- Холодное: 🔎 Simply Swords, 🔎 **Better Combat** + Combat Roll.
- Тяжёлое: ✅ Create Big Cannons (орудия на кораблях/цитаделях), Mekanism Meka-Tool, IE Railgun.

## I. NPC, города, социальное

- ✅ **MineColonies** (+ Structurize, BlockUI, Domum Ornamentum, MultiPiston) + стиль-паки
  (✅ Byzantine Styles, Cozy Apartments и т.п. — 2–4 стиля, не больше) + ✅ Warehouse Workshop (опц.).
- ✅ **MCA Reborn** — деревенские жители с характером, браками, детьми; ✅ MCA: Romantic Expansion (опц.,
  подарки и свадьбы между игроками; по умолчанию выкл.).
- 🔎 **Easy NPC** — NPC-гиды с диалогами в стартовой гавани (связка с квестами).
- 🔎 Simple Voice Chat (голос по близости; UDP-порт), 🔎 Emotecraft (эмоции), 🔎 Chat Heads.
- (опц.) 🔎 Lightman's Currency — магазины игроков, если захочется торговли.

## J. Транспорт и перемещение

Create Aeronautics (самолёты, дирижабли, машины, цитадели), поезда Create + Steam 'n' Rails,
🔎 Immersive Aircraft (простые самолёты раннего этапа), ✅ Waystones (+ Waystones: Sable),
Mekanism реактивный ранец, полёт Ars, драконы Dragon Mounts, ездовые Alex's Mobs, лошади.

## K. Строительство, декор, терраформинг

- Схематики Create (Schematicannon) — «постройка готовых моделей»; MineColonies строитель +
  Structurize-сканер; 🔎 Building Gadgets 2; ✅ Construction Sticks; 🔎 Effortless Building (опц.).
- Декор (выбрать ~8–10, без дублей): 🔎 Macaw's (двери, окна, крыши, мосты, мебель, фонари, пути),
  🔎 Handcrafted, 🔎 Another Furniture, 🔎 Chipped или Rechiseled (одно), 🔎 Framed Blocks,
  🔎 Every Compat (единые варианты для всех пород дерева), 🔎 Fusion (connected textures),
  🔎 Supplementaries + Amendments, 🔎 Decorative Blocks.
- Терраформинг: Building Gadgets (обмен/снос областей), буры Create на Aeronautics-тягачах
  (тоннелепроходческий комбайн), Botania Rod of the Terra Firma / Shifting Crust,
  мегапостройка «Терраформер» (меняет биом в радиусе — см. 03).

## L. Интерфейс и качество жизни

🔎 EMI (+ JEI) · ✅ Jade (+ Jade Addons) · 🔎 AppleSkin · 🔎 Xaero's Minimap + World Map ·
🔎 Open Parties and Claims · ✅ FTB Quests + FTB Teams + FTB Library + ✅ FTB XMod Compat ·
🔎 FTB Ultimine · ✅ Sophisticated Backpacks/Storage · ✅ GraveStone Mod · 🔎 Mouse Tweaks ·
✅ Inventory Essentials · ✅ TrashSlot · 🔎 Legendary Tooltips + Iceberg · 🔎 Overflowing Bars ·
🔎 Traveler's Titles (заставки при входе в биом/данж) · 🔎 Better Advancements · 🔎 Toast Control ·
🔎 Controlling · 🔎 Configured · 🔎 Catalogue · ✅ FancyMenu + 🔎 Drippy Loading Screen (брендинг) ·
✅ Enchantment Descriptions · 🔎 Shoulder Surfing Reloaded (опц.) · 🔎 Cosmetic Armor (мода/внешний вид) ·
🔎 Better Days (плавная смена дня).

## M. Визуал и звук (подробно в 06)

Ресурспаки: Fresh Animations (требует 🔎 Entity Model Features + Entity Texture Features),
Better Leaves, «Stay True» или аналог в ванильном стиле, тёмный/единый GUI — по результатам теста.
Шейдеры: Complementary Reimagined / Unbound + ✅ Euphoria Patches. Частицы/атмосфера:
🔎 Subtle Effects, 🔎 Particle Rain, 🔎 Visuality, 🔎 Falling Leaves, ✅ True Falling Stars (метеоры
в небе — клиентский визуал), 🔎 динамический свет (Sodium Dynamic Lights / LambDynamicLights — что
есть на NeoForge), 🔎 Not Enough Animations. Звук: 🔎 Sound Physics Remastered, 🔎 AmbientSounds,
🔎 Presence Footsteps (если есть NeoForge).

## N. Погода, катастрофы, загрязнение (подробно в 05)

✅ **Weather, Storms & Tornadoes** + CoroUtil · ✅ Expanded Weather2 Dynamics (тревоги, радар,
обзоры ущерба) · ✅ **Airborne** · Serene Seasons · Enhanced Celestials · Mekanism (радиация) ·
**arkhaven-core** (метеориты, разломы, Генератор оберега, режиссёр событий).

## O. Расы, классы, алхимия, крюки, зоны опасности (подробно в 10)

- Расы: 🔎 **NeoOrigins** (+ свой датапак `arkhaven_origins`).
- Классы: 🔎 **Pufferfish's Skills** + Pufferfish's Attributes (+ нужные им аддоны),
  ✅ Iron's Spells 'n Spellbooks Dynamic Skill Trees (деревья школ магии), свой датапак деревьев.
- Алхимия: 🔎 **Toil and Trouble** (котёл-алхимия), плюс встроенное: котёл Iron's, Botania Brewery;
  свои эффекты/зелья — KubeJS.
- Баффы на виду: 🔎 мод описаний эффектов + компактные таймеры эффектов на HUD.
- Крюки: 🔎 **Create Grappling Hooks** (аддон Aeronautics), 🔎 Grappling Hook: Neo (ранний).
- Спаун: 🔎 **In Control!**, 🔎 **Torchmaster** (Мегафакел), фильтр безопасных зон в arkhaven-core.
- Аксессуары: Curios/Accessories (уже есть как зависимость) — «Оберег путника».

## P. Скрипты и данные

🔎 **KubeJS** (+ Rhino), 🔎 KubeJS Create / KubeJS Mekanism / прочие интеграции, если существуют
под 1.21.1 (иначе — рецепты через datapack JSON), ✅ Almost Unified, 🔎 ProbeJS (только для разработки,
не в сборку).
