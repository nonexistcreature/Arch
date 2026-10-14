# HANDOFF — для владельца

> Документ дополняется по ходу работы. Финальная версия — в конце проекта (фаза 7).

## Нужно от владельца

1. **GitHub Pages (одна галочка):** https://github.com/nonexistcreature/Arch → Settings → Pages → Source: **GitHub Actions**.
   После этого сборка публикуется сама по адресу `https://nonexistcreature.github.io/Arch/pack.toml`,
   а при теге `v*` в Releases появляются `Arkhaven-Setup.exe`, `Arkhaven-Prism-Instance.zip`, `Arkhaven-Own-Launcher.zip`, `Arkhaven-Server-Kit.zip`.
2. **Сервер на этом ПК:** двойной клик по `server\windows\Arkhaven-Server-Setup.cmd` → «Да» на запрос прав.
   Больше ничего: админом станешь ты (ник берётся из аккаунта в лаунчере), поднимется сеть друзей ZeroTier,
   сервер будет запускаться сам при входе в Windows. Потом скажи мне — я опубликую ID сети (`pack/network.json`), и установщики друзей подключат ZeroTier сами.
   Linux-ноутбук вместо ПК — `server/КАК_РАЗВЕРНУТЬ.md`, вариант 2.

Игрокам: `launcher/ИГРОКАМ.md` (установщик, Prism-импорт или свой лаунчер через `install-to-launcher.cmd`). Вход — аккаунт Microsoft.

## Что уже установлено на этой машине (для разработки)

Всё лежит **внутри папки проекта** `tools/bin/` (в git не попадает):
JDK 21 (Temurin), packwiz, NeoForge-установщик, packwiz-installer-bootstrap,
Inno Setup 7.1 (установлен «для текущего пользователя» в `tools/bin/inno`, удаляется через
«Приложения» → Inno Setup), кеш Prism Launcher и JRE. Python-пакет `pyyaml`.
Тестовый клиент — `tests/client_run/` (HeadlessMC, без окна).
⚠ Один раз HeadlessMC по умолчанию поставил NeoForge в твою папку `%APPDATA%\.minecraft`. Я это откатил:
профиль «NeoForge» убран из официального лаунчера (копия старого файла — `tests/launcher_profiles.backup.json`),
версии перенесены в папку проекта. В `%APPDATA%\.minecraft\libraries` могли остаться скачанные библиотеки —
это просто кеш, он ничего не меняет (можно не трогать).
Тестовый сервер — `tests/server_run/` (только 127.0.0.1, offline-режим, запускается и останавливается тестом).

## Как зайти
(заполняется в конце: ссылка на установщик, адрес сервера, SmartScreen)

## Что посмотреть глазами
(заполняется в конце — см. шаблон в docs/09_ROADMAP.md)
