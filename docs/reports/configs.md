# Конфиги

## config/incontrol/spawn.json
1. Zone 0: no natural hostile spawns within 256 blocks of world spawn (the Haven)
2. Zone 1: modded wildlife and bosses stay away from the calm lands (1500 blocks around spawn)
3. Zone 1: vanilla hostiles half as often within 1500 blocks of spawn
4. No phantoms anywhere

Ключи `onjoin`, `description` In Control 10.3 не принимает.

## Анти-гринд (03 §6)
| Мод | Параметр | Было → стало | Зачем |
|---|---|---|---|
| FTB Ultimine | exhaustion_per_block | 20 → 5 | вейнмайнер почти не ест голод; лимит 64 блока оставлен |
| AE2 | channels | DEFAULT → INFINITE | уютная сборка, без головоломки каналов |
| Dragon Mounts | hatch_time / growth_time | 600 → 300 с | дракон вылупляется и растёт вдвое быстрее |
| Waystones | XP за телепорт | до 27 → до 10 ур., 0.005/блок | дешёвые путешествия |
| Ванилла | playersSleepingPercentage | 34 | 2–3 спящих из 8 пропускают ночь |
| Ванилла | doInsomnia | false | нет фантомов |
| arkhaven-core | creepersKeepBlocks | true | криперы не ломают постройки |
