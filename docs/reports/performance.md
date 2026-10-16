# Производительность клиента (авто, tools/bench_client.py)

ПК теста: Ryzen 5 7500F, RX 6700 XT, 2560×1377, сервер выключен (одиночный мир).

| дата | вариант | медиана FPS | мин | макс | среднее | разрешение | выключено |
|---|---|---|---|---|---|---|---|
| 2026-10-14 17:39 | baseline | FAILED | | | | 2560x1377 | ['   [17:34:58.206] [main/WARN] [mixin/]: Error loading class: com/alien/common/util/AlienPredicates (java.lang.ClassNotFoundException: com.alien.common.util.AlienPredicates)'] |
| 2026-10-14 17:46 | mem10_zgc | FAILED | | | | 2560x1377 |  |
| 2026-10-14 17:46 | noshader | FAILED | | | | 2560x1377 |  |
| 2026-10-14 17:51 | mem10_zgc | FAILED | | | | 2560x1377 | ['   [17:47:14.907] [main/WARN] [mixin/]: Error loading class: com/alien/common/util/AlienPredicates (java.lang.ClassNotFoundException: com.alien.common.util.AlienPredicates)'] |
| 2026-10-14 17:53 | noshader | FAILED | | | | 2560x1377 | ['   [17:51:42.551] [main/WARN] [mixin/]: Error loading class: com/alien/common/util/AlienPredicates (java.lang.ClassNotFoundException: com.alien.common.util.AlienPredicates)'] |
| 2026-10-14 18:18 | mem10_zgc | 37 | 15 | 64 | 33 | 2560x1377 | - |
| 2026-10-14 18:19 | noshader | FAILED | | | | 2560x1377 | ['   [18:19:04.511] [main/WARN] [mixin/]: Error loading class: com/alien/common/util/AlienPredicates (java.lang.ClassNotFoundException: com.alien.common.util.AlienPredicates)'] |
| 2026-10-14 18:25 | current | 82 | 23 | 84 | 61 | 2560x1377 | - |
| 2026-10-14 18:28 | noshader | 88 | 15 | 131 | 86 | 2560x1377 | - |
| 2026-10-14 18:40 | current | 23 | 0 | 38 | 25 | 2560x1377 | - |
| 2026-10-14 18:42 | lite_client | 17 | 8 | 24 | 16 | 2560x1377 | DistantHorizons-3.3.3-1.21.1-fabric-neoforge.jar, visuality-forge-3.0.0.jar, particlerain-4.0.2+1.21.1-neoforge.jar, SubtleEffects-neoforge-1.21.1-1.15.1.jar, AmbientSounds_NEOFORGE_v6.3.10_mc1.21.1.jar, PresenceFootsteps-1.21.1-1.12.0-beta.1-1.21NeoForge.jar |
| 2026-10-14 18:42 | current | FAILED | | | | 2560x1377 | ['   [18:42:53] [Render thread/WARN] [minecraft/ClientLanguage]: Skipped language file: emi_loot:lang/ru_ru.json (com.google.gson.JsonSyntaxException: com.google.gson.stream.MalformedJsonException: Expected name at line 569 column 2 path $.emi_loot.enchantment_value.lookup)'] |
| 2026-10-14 18:43 | current | FAILED | | | | 2560x1377 | ['CLIENT EXITED 1 after 3s'] |
| 2026-10-14 18:43 | noshader | FAILED | | | | 2560x1377 | ['CLIENT EXITED 1 after 3s'] |
| 2026-10-14 18:48 | current | 68 | 15 | 106 | 56 | 2560x1377 | - |
| 2026-10-14 18:51 | noshader | FAILED | | | | 2560x1377 | ['   [18:48:52.360] [main/WARN] [mixin/]: Error loading class: com/mrcrayfish/controllable/client/binding/context/BindingContext (java.lang.ClassNotFoundException: com.mrcrayfish.controllable.client.binding.context.BindingContext)'] |
| 2026-10-14 19:55 | current | 52 | 16 | 92 | 52 | 2560x1377 | - |
| 2026-10-14 19:58 | shader_medium | 88 | 60 | 123 | 90 | 2560x1377 | - |
| 2026-10-14 20:01 | no_dh | 147 | 82 | 160 | 136 | 2560x1377 | DistantHorizons-3.3.3-1.21.1-fabric-neoforge.jar |
| 2026-10-14 20:04 | rd8 | 45 | 42 | 108 | 60 | 2560x1377 | - |
| 2026-10-14 20:06 | noshader | 140 | 84 | 190 | 127 | 2560x1377 | - |
| 2026-10-14 20:10 | no_dh_medium | 56 | 51 | 94 | 61 | 2560x1377 | DistantHorizons-3.3.3-1.21.1-fabric-neoforge.jar |
| 2026-10-14 20:12 | no_dh_medium | 52 | 15 | 55 | 40 | 2560x1377 | DistantHorizons-3.3.3-1.21.1-fabric-neoforge.jar |

## С 2026-10-16: бенч в движении (полёт по кругу 10 блоков/с) + стабильность кадров

p99 — 99-й перцентиль времени кадра (мс, медиана по окнам 5 с); worst — худший кадр; s33/s50 — кадры дольше 33/50 мс за прогон (фризы).

| дата | вариант | медиана FPS | мин | среднее | p99 мс | worst мс | s33 | s50 | выключено |
|---|---|---|---|---|---|---|---|---|---|
| 2026-10-16 14:10 | noshader | FAILED | | | | | | | ['   [14:10:09.812] [main/WARN] [mixin/]: Error loading class: com/crystaelix/simurail/content/bogey/PhysicsBogeyBlockEntity (java.lang.ClassNotFoundException: com.crystaelix.simurail.content.bogey.PhysicsBogeyBlockEntity)'] |
| 2026-10-16 14:13 | noshader | 533 | 297 | 520 | 9.0 | 68 | 8 | 1 | - |
| 2026-10-16 14:16 | noshader | 454 | 136 | 431 | 12.0 | 619 | 14 | 6 | - |
| 2026-10-16 14:19 | noshader | 814 | 391 | 743 | 8.0 | 167 | 5 | 4 | - |
| 2026-10-16 14:22 | noshader | 726 | 315 | 664 | 10.0 | 171 | 9 | 2 | - |
| 2026-10-16 14:26 | pack_noshader (real) | FAILED | | | | | | | ['   [14:23:56.334] [main/WARN] [mixin/]: Error loading class: com/crystaelix/simurail/content/bogey/PhysicsBogeyBlockEntity (java.lang.ClassNotFoundException: com.crystaelix.simurail.content.bogey.PhysicsBogeyBlockEntity)'] |
| 2026-10-16 14:29 | pack_noshader (real) | 537 | 262 | 531 | 10.0 | 36 | 1 | 0 | - |
| 2026-10-16 14:32 | pack (real) | 132 | 15 | 78 | 78.0 | 368 | 372 | 356 | - |
| 2026-10-16 14:35 | sh_medium (real) | 151 | 139 | 155 | 16.0 | 569 | 22 | 1 | - |
| 2026-10-16 14:38 | sh_low (real) | 185 | 167 | 189 | 14.0 | 424 | 4 | 1 | - |
| 2026-10-16 14:41 | sh_tuned (real) | 164 | 154 | 168 | 16.0 | 472 | 7 | 1 | - |
| 2026-10-16 14:43 | pack (real) | 136 | 100 | 131 | 19.0 | 53 | 47 | 1 | - |
| 2026-10-16 14:46 | ns_no_cosmetic (real) | 565 | 420 | 570 | 9.0 | 36 | 1 | 0 | sound-physics-remastered-neoforge-1.21.1-1.5.1.jar, particlerain-4.0.2+1.21.1-neoforge.jar, visuality-forge-3.0.0.jar, SubtleEffects-neoforge-1.21.1-1.15.1.jar, Falling Leaves-1.0.jar, AmbientSounds_NEOFORGE_v6.3.10_mc1.21.1.jar, PresenceFootsteps-1.21.1-1.12.0-beta.1-1.21NeoForge.jar |
| 2026-10-16 14:49 | ns_no_soundphys (real) | 556 | 198 | 494 | 12.0 | 41 | 5 | 0 | sound-physics-remastered-neoforge-1.21.1-1.5.1.jar |
| 2026-10-16 14:52 | ns_no_emf (real) | 539 | 286 | 498 | 11.0 | 47 | 2 | 0 | entity_model_features-3.3.11-1.21-neoforge.jar, notenoughanimations-neoforge-1.12.6-mc1.21.1.jar |
| 2026-10-16 14:54 | pack_noshader (real) | 278 | 213 | 289 | 13.0 | 39 | 3 | 0 | - |
| 2026-10-16 14:57 | pack (real) | 135 | 122 | 139 | 18.0 | 48 | 58 | 0 | - |
| 2026-10-16 14:58 | sh_low (real) | FAILED | | | | | | | ['   [14:57:47.362] [main/WARN] [mixin/]: Error loading class: com/crystaelix/simurail/content/bogey/PhysicsBogeyBlockEntity (java.lang.ClassNotFoundException: com.crystaelix.simurail.content.bogey.PhysicsBogeyBlockEntity)'] |
| 2026-10-16 15:01 | sh_lite (real) | 192 | 163 | 192 | 15.0 | 357 | 3 | 1 | - |
| 2026-10-16 15:04 | sh_noshadow (real) | 197 | 153 | 195 | 15.0 | 531 | 7 | 2 | - |
| 2026-10-16 15:06 | sh_low_rd8 (real) | 198 | 180 | 196 | 15.0 | 48 | 13 | 0 | - |
| 2026-10-16 15:09 | pack_noshader (real) | 557 | 365 | 538 | 10.0 | 44 | 2 | 0 | - |
| 2026-10-16 15:14 | shipped_5g (real) | FAILED | | | | | | | ['   [15:11:51.540] [main/WARN] [mixin/]: Error loading class: com/crystaelix/simurail/content/bogey/PhysicsBogeyBlockEntity (java.lang.ClassNotFoundException: com.crystaelix.simurail.content.bogey.PhysicsBogeyBlockEntity)'] |

### Итог оптимизации 0.1.7 (2026-10-16, копия реального мира, полёт над базой игроков, 2560×1377, RX 6700 XT)

| режим | медиана FPS | кадров > 50 мс |
|---|---|---|
| Complementary HIGH (было по умолчанию) | 132–136 | 0–1 (в первом запуске 356 — компиляция шейдеров) |
| Complementary MEDIUM | 151 | 1 |
| **Complementary «lite» (теперь по умолчанию)** | **192** | 1 |
| Complementary LOW / без теней / дальность 8 | 185 / 197 / 198 | 1–2 |
| без шейдеров | 537–557 (шумно: погода Weather2, симуляция) | 0 |
| без шейдеров, косметика выключена (SoundPhysics, частицы, листья, шаги, Visuality) | 565 | 0 |

- «lite» = тени низкого разрешения на 80 блоков, без объёмных лучей, без SSAO, без отражений блоков и теней от мобов; FXAA вкл.
  На скриншотах выглядит почти как HIGH (`tests/client_run/shots/`). Потолок Complementary на этой карте при 1440p ≈ 200 FPS
  при любых настройках — дальше только без шейдеров.
- Косметические клиентские моды стоят ≈ 5 % — оставлены.
- **Главный источник фризов у игроков — мало памяти.** mrpack не переносит настройки JVM; Prism по умолчанию даёт 4 ГБ,
  Modrinth App — 2 ГБ. Тест: куча 5 ГБ → медиана 4 FPS, паузы GC по 0,5–1 с; 6 ГБ → 231 FPS. Теперь игра сама пишет
  в чат, если памяти < 6 ГБ, и как её поднять (`kubejs/client_scripts/06_memory_hint.js`).
- Реклама «Enhanced Celestials 2 is here!» открывалась поверх игры при каждом входе (и ломала прежние замеры: старые
  «noshader 140» — это FPS меню с размытием). Закрыта скриптом `05_no_popups.js`.
