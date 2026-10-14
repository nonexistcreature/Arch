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
