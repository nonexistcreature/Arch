# Arkhaven — домашний сервер

Всё живёт в `/opt/arkhaven` под системным пользователем `arkhaven`. Другие сервисы машины не затрагиваются.

| Что | Команда |
|---|---|
| Установка (один раз, Ubuntu 24.04) | `bash server/scripts/install.sh` |
| Старт / стоп | `sudo systemctl start arkhaven` / `sudo systemctl stop arkhaven` |
| Логи | `docker logs -f arkhaven-mc` |
| Консоль сервера | `docker exec -it arkhaven-mc rcon-cli` |
| Ручной бэкап сейчас | `docker exec arkhaven-backup backup now` |
| Список бэкапов | `docker exec arkhaven-backup restic -r /backups snapshots` |
| Проверить бэкап (развернуть рядом) | `sudo /opt/arkhaven/scripts/restore.sh latest --into /tmp/arkhaven-check` |
| Откатить мир | `sudo /opt/arkhaven/scripts/restore.sh <id>` (старый мир не удаляется, а переименовывается) |
| Обновить сборку | на машине разработчика `tools/release.sh`, затем `sudo systemctl restart arkhaven` |
| Свой канал обновлений | `cd /opt/arkhaven/compose && docker compose --profile selfhost-pack up -d` |

Настройки — в `/opt/arkhaven/compose/.env` (шаблон `server/.env.example`):
`PACK_URL`, `OPS`, `WHITELIST`, `RCON_PASSWORD`, `SERVER_MEMORY`.

Порты: `25565/tcp` (игра), `24454/udp` (голосовой чат), RCON `25575` — только localhost.
Ночной перезапуск — systemd-таймер `arkhaven-restart.timer` в 06:00 с предупреждениями в чат.
Бэкапы — ежечасно (restic), хранятся 24 часа / 7 дней / 4 недели.
