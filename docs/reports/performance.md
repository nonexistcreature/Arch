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
