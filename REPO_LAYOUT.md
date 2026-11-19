# EquipLens — навігація по репо

> живе доки: існує репо. Кожна зміна структури (нова тека, новий прилад, переїзд) оновлює цей файл у тому ж коміті.
> Зразок — `lens-governance:tools/claude-code/templates/REPO_LAYOUT_template.md`. Місце — корінь, не `docs/`: за Р-7 `docs/` — лише сайт (рішення Konst 19.11.2026, S36).
> Перелік живих файлів `lens/` · `sessions/` · `tools/` для гейта — `lens/EquipLens_INDEX.md`. Тут — теки, прилади й читачі; поштучного переліку не дублюю.

## Порядок читання на старті сесії

0. `bash tools/env_check.sh` (диспетчер ядра кладе його ⚠ / ✗ у перше повідомлення сам)
1. `CLAUDE.md`
2. найновіше самері в `sessions/` — §0 «ВІДКРИТЕ»
3. `lens/EquipLens_CHERGA.md` — цілком
4. точково: `lens/EquipLens_MASTER_LOCK.md` (вироки) → `lens/EquipLens_Z_REGISTR.md` (адреси З-номерів) → специфікації `lens/EquipLens_K21_*`

## Дерево

```
EquipLens/
├─ CLAUDE.md          як працюємо (щосесії)
├─ REPO_LAYOUT.md     ця карта
├─ index.html         живий сайт — «Посібник з POS-обладнання» (GitHub Pages публікує корінь main)
├─ data/  media/      дані й фото; у коді index.html не згадані (греп 19.11.2026)
├─ lens/              канон: черга · MASTER_LOCK · реєстри · специфікації · INDEX (перелік для гейта) · AUDIT
│  └─ shots/          примірка UI-рішень наперед (README — стан)
├─ sessions/          живі самері (стеля 2)
├─ tools/             стенд з важелями, смоук, прилади
├─ sources/           оригінали (xlsx, zip, фото)
├─ archive/           історія: самері · стенди · матриці — не правиться
└─ .claude/           налаштування Claude Code і хук старту
```

## Прилади

| прилад | що міряє / робить | коли брати | запуск |
|---|---|---|---|
| `.claude/hooks/session-start.sh` | ставить інструменти гейтів: `jsdom` у `~/.deps` + `NODE_PATH` (для смоука) | сам, на старті сесії (реєстрація — `.claude/settings.json`; сесія з кількома репо — кличе диспетчер ядра) | `CLAUDE_CODE_REMOTE=true .claude/hooks/session-start.sh` |
| `tools/env_check.sh` | база · гейт продукту (`Lens_validate --product`) · прод: `/` ≡ `origin/main:index.html` за вмістом, службове видно — ⚠ · стенд `--html` · смоук · `doc_health` · `shots_check` · версія; exit 1 — розібратись до роботи | перший крок кожної сесії (диспетчер ядра кличе сам) | `bash tools/env_check.sh` · зуби: `ENV_INJECT=1 bash tools/env_check.sh` → ✗ прод (підкинута розбіжність) · смоук «ЗЛОВИВ» |
| `tools/audit_prompts.sh` | аудит інструкцій моделями (`/doctor prompt-audit`), клас 1 — opus, клас 2 — ще й sonnet; журнал — `lens/EquipLens_AUDIT.md` | змінив `CLAUDE.md` / правило — пакетом перед самері, після заміру лімітів | `bash tools/audit_prompts.sh 2 CLAUDE.md` |
| `tools/smoke_v*.js` | механіка головного стенда (не значення важелів); живий — найбільший номер | після кожної правки стенда | `cd tools && node smoke_v17_30.js` · `--inject` |
| `tools/EquipLens_K0_passport_audit.js` | аудит паспорта стенда К0 (самері S17 §4) | правка паспорта стенда | `cd tools && node EquipLens_K0_passport_audit.js` (шапка чекає `EquipLens_headbench_v17.html` поруч — ім'я застаріле, не перевіряв) |

## Хто що читає

| шлях | читач | як |
|---|---|---|
| `index.html` | браузер | GitHub Pages з кореня `main` — кожен коміт у `main` = деплой |
| `lens/` · `sessions/` · `tools/` · `*.md` кореня | люди, агент; **але й Pages** — службове поки публікується (проба 19.11: `/lens/EquipLens_CHERGA.md` → 200) | переїзд сайту в `docs/` (Р-7) прибере — вирішує Konst |
| `tools/EquipLens_headbench_v*.html` | Konst (стенд з важелями, приймання на телефоні) | файл відкривається напряму; у білд ще не портовано (`БІЛД` черги) |
| `data/` · `media/` | читача в коді не знайдено | не видаляти без вироку Konst (ADOPT «Чого не робити») |

## Переїзди (старий шлях → новий)

| було | стало | коли |
|---|---|---|
| `lens-governance:products/EquipLens/` | `lens/` · `archive/` | G-Y, 24.09.2026 |
| сайт у корені | `docs/` (Р-7) | ⬜ — після перемикання Pages Konst |
| стенд `tools/EquipLens_headbench_v*.html` (один файл) | дерево джерел (`src/`) + збірка в один HTML (`tools/build.py`), значення — із засіву стенда | ⬜ — на `БІЛД` черги, за `lens-governance:kernel/Lens_ARCH-1_brief.md` (К5 тут; канон дерева в ядрі ще не написаний — К2–К3) |
