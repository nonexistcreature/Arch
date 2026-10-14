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
