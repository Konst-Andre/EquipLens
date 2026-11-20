# EquipLens — як працюємо

<!-- живе доки: існує репо. Зразок — lens-governance:tools/claude-code/templates/CLAUDE_template.md (що сюди класти й мірка ваги — його шапка); каркас — tools/claude-code/REPO_FRAME.md там само.
     Заведено S36, 19.11.2026 (переїзд на каркас, шлях Б — самері S36). Правка цього файла — аудит клас 2. -->

**Що це.** Продукт сімейства Lens: польовий нотатник потреби в обладнанні аптек — PWA, один HTML-файл. Окремий продукт від QR Lens (межа — `lens/EquipLens_MASTER_LOCK.md` §2, злиття заборонене). Власник змісту — Konst. Працюємо лише в Claude Code (Project не використовується — Konst 19.11.2026).

**Стан продукту — не тут** (міняється щоходу): самері §0 (`sessions/`, найновіше) і бриф `lens/BUILD-1_brief.md` §0. Тут — лише те, що стоїть: джерело вигляду — **заморожений стенд** `tools/EquipLens_headbench_v17_30.html` (рішення Konst 19.11.2026, `lens/BUILD-1_brief.md` §3) з важелями `S` і засівом `LOCK_SEED` (`archive/summaries/EquipLens_session_summary_S35_OSTRIVETS.md` §1). Застосунок збирається з нього **частинами** в PWA: джерела `src/` → `docs/index.html` (`tools/build.py build`, руками не правити); кроки порту — `lens/BUILD-1_brief.md`, кроки стенда й нові екрани — `lens/DES-1_brief.md`; будова дерева — `lens-governance:kernel/Lens_ARCH-1_brief.md` (крок К5 — польова перевірка тут). `index.html` у корені — старий «Посібник з POS-обладнання» (сайт людей до `HOST-1` Б), не білд.

- **Старт сесії:** рядки ⚠ / ✗ `env_check` кладе диспетчер ядра (нема — `bash tools/env_check.sh` руками) → `REPO_LAYOUT.md` → найновіше самері в `sessions/` (§0) → `lens/EquipLens_CHERGA.md` цілком → точково `lens/EquipLens_MASTER_LOCK.md` · `lens/EquipLens_Z_REGISTR.md`.
- **Гілка:** робота — на гілці `claude/…`; `main` — лише з «так» Konst: **кожен коміт у `main` = деплой GitHub Pages** (публікується корінь репо, разом зі службовим). Стоїть «так» Konst 20.11.2026 (S38): fast-forward `main` до гілки після зелених гейтів, **коли сайт кореня (`index.html` · `data/` · `media/`) не змінюється** — перед push `git diff --stat origin/main HEAD -- index.html data media` порожній; змінює корінь — окреме «так». Push відхилено — `git pull --rebase`, ніколи force.
- **Пристрій приймання:** телефон (стенд і майбутня PWA).
- **Дизайн-основа:** канон чисел — `lens/EquipLens_head_valuesLOCK.md` (рішення Konst 19.11.2026, `lens/BUILD-1_brief.md` §3), **джерело чисел** (правка — лише вироком пристрою, правило — шапка файла; форму судить `tools/build.py values --check`); токени збірки — з нього (ПОРТ-ЧИСЕЛ — `lens/BUILD-1_brief.md` §2; стан — там же). Друга поверхня (адмінка, `ADMIN-1` черги) бере ті самі токени. Іменний простір стенда: `nav*` — коробка острівця, `nv*` — вміст кнопки (S35 §1).

## Де що живе і як потрапляє в прод

Карта тек і приладів — `REPO_LAYOUT.md`; перелік живих файлів `lens/` · `sessions/` · `tools/` — `lens/EquipLens_INDEX.md` (гейт звіряє його в обидва боки: новий файл у цих теках — рядок в INDEX тим самим комітом).

| що | де | як їде в прод |
|---|---|---|
| сайт | корінь: `index.html` · `data/` · `media/` | GitHub Pages з кореня `main` — коміт у `main` |
| білд | джерела `src/` → зібраний `docs/` (`index.html` + маніфест й іконки поруч; `tools/build.py build`, руками не правити) | у `main` fast-forward-ом (Pages віддає за `/docs/`); адресою людей стане з `HOST-1` Б (воркер `equiplens` віддає `docs/`, прод — «так») |
| стенд, смоук, прилади | `tools/` | не призначені для публікації, але Pages їх віддає (перехідний стан Р-7) |
| канон, самері, архів, оригінали, `*.md` кореня | `lens/` · `sessions/` · `archive/` · `sources/` | те саме |

Переїзд адреси людей на білд (Р-7) — крок Б `HOST-1` (`lens/HOST-1_brief.md`: воркер віддає `docs/`, «Посібник» → архів, Pages вимкнути) — прод, окреме «так» Konst, з пробою «до/після».

## Гейти перед комітом

`bash tools/env_check.sh` — exit 0; `ENV_INJECT=1 bash tools/env_check.sh` — ✗ прод і «ЗЛОВИВ» у кожного приладу з `--inject` (зуби). Усередині — гейти продукту (`Lens_validate.py --product .`, стенд і смоук `tools/smoke_v*.js`, джерело чисел, збірка `docs/`, шрифт, знак, іконки PWA) і прилади ядра; повний перелік — сам `tools/env_check.sh` (рядок виводу на прилад). Правив стенд — смоук обома режимами до коміту. Числа ✓ — у виводі приладу; нормативи стенда — у шапці стенда й останньому самері, не тут. Інструменти гейтів (jsdom, playwright-python, fonttools, pillow, uharfbuzz — перелік у хуку) ставить `.claude/hooks/session-start.sh` — лише в хмарній сесії (`CLAUDE_CODE_REMOTE=true`); локально — руками ті самі встановлення, що в хуку; змінив гейт — правиш хук і `env_check` тим самим комітом.

Прилади ядра запускаються з клону ядра: `../lens-governance`, нема — `/tmp/lens-governance` (`tools/env_check.sh`, рядок `K=`). У режимі Auto їх пропускають вузькі правила дозволу `.claude/settings.json` («так» Konst 19.11.2026) — коли робоча тека сесії — цей репо (сесія з кореня кількох репо `.claude/settings.json` цього репо не вантажить). Нова команда приладу ядра — нове вузьке правило там же; широкі правила з інтерпретатором (`Bash(python*)`) Auto відкидає (code.claude.com/docs/en/permission-modes, 20.11.2026).

## Секрети

Нема. Дані людей (аптеки, адреси) — не в прев'ю й не в публічних файлах.

## Тут інакше, ніж у профілі

- Самері — `sessions/EquipLens_session_summary_S<N>_<ТЕМА>.md`, живих рівно 2 (`sessions/README.md`); витіснене — `git mv` в `archive/summaries/` і рядок в INDEX.
- Черга — `lens/EquipLens_CHERGA.md` (свій словник станів у шапці). Журнал аудиту правил — `lens/EquipLens_AUDIT.md`.
- Вироки продукту — у `lens/EquipLens_MASTER_LOCK.md` (значення стенда — не сюди, а в `lens/EquipLens_head_valuesLOCK.md`, `lens/BUILD-1_brief.md` Ф1); З-номери — адреси в `lens/EquipLens_Z_REGISTR.md`, повний текст там, куди адреса веде.
