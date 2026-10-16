
## 2026-10-16 — Particle Core async × Ars Nouveau × C2ME → клиент виснет, кик по таймауту
Particle Core тикает частицы в ForkJoinPool; ParticleGlow (Ars) берёт level.random; C2ME (threading fixes) на каждое
обращение не из Render thread пишет ConcurrentModificationException со стеком. Возле источников свечения Ars — десятки
тысяч трейсов (лог 115 МБ), клиент замирает > 30 с, сервер кикает «Timed out». Лечение: Particle Core
`asynchronousTicking = false` + `disableOptimizations: ["ASYNC"]` (pack/config).
Серверное лечение без обновления клиентов: `67_ars_light_fix.js` меняет `ars_nouveau:light_block` вокруг игроков
на ванильный `minecraft:light` (уровень 15, без частиц). Точка, где кикало: (-492, 148, -1044) — 36 фонарей Ars.
