# EquipLens — як працюємо

<!-- живе доки: існує репо. Зразок — lens-governance:tools/claude-code/templates/CLAUDE_template.md (що сюди класти й мірка ваги — його шапка); каркас — tools/claude-code/REPO_FRAME.md там само.
     Заведено S36, 19.11.2026 (переїзд на каркас, шлях Б — самері S36). Правка цього файла — аудит клас 2. -->

**Що це.** Продукт сімейства Lens: польовий нотатник потреби в обладнанні аптек — PWA, один HTML-файл. Окремий продукт від QR Lens (межа — `lens/EquipLens_MASTER_LOCK.md` §2, злиття заборонене). Власник змісту — Konst. Працюємо лише в Claude Code (Project не використовується — Konst 19.11.2026).

**Стан продукту (Konst 19.11.2026): білда ще нема.** Є стенд з важелями `tools/EquipLens_headbench_v*.html` (живий — найбільший номер, зараз `v17_30`) і зафіксовані на ньому значення (засів `LOCK_SEED`, 244 ключі — `archive/summaries/EquipLens_session_summary_S35_OSTRIVETS.md` §1). Застосунок збиратиметься зі стенда **частинами** в PWA — із замороженого стенда `v17_30` (рішення Konst 19.11.2026, `lens/BUILD-1_brief.md` §3; кроки стенда й нові екрани — бриф `lens/DES-1_brief.md`; бриф `lens/BUILD-1_brief.md`); будова дерева — за брифом `lens-governance:kernel/Lens_ARCH-1_brief.md` (крок К5 — польова перевірка тут). `index.html` у корені — старий «Посібник з POS-обладнання», не білд стенда.

- **Старт сесії:** рядки ⚠ / ✗ `env_check` кладе диспетчер ядра (нема — `bash tools/env_check.sh` руками) → `REPO_LAYOUT.md` → найновіше самері в `sessions/` (§0) → `lens/EquipLens_CHERGA.md` цілком → точково `lens/EquipLens_MASTER_LOCK.md` · `lens/EquipLens_Z_REGISTR.md`.
- **Гілка:** робота — на гілці `claude/…`; `main` — лише з «так» Konst: **кожен коміт у `main` = деплой GitHub Pages** (публікується корінь репо, разом зі службовим). Push відхилено — `git pull --rebase`, ніколи force.
- **Пристрій приймання:** телефон (стенд і майбутня PWA).
- **Дизайн-основа:** токенів окремим файлом ще нема — джерело значень зараз стенд: об'єкт `S` (важелі) і засів `LOCK_SEED` у `tools/EquipLens_headbench_v*.html`; канон чисел — `lens/EquipLens_head_valuesLOCK.md` (рішення Konst 19.11.2026, `lens/BUILD-1_brief.md` §3), **згенерований** зі засіву (`BUILD-1` Ф1, 20.11.2026; руками не правити); токени збірки з нього — Ф2 (ПОРТ-ЧИСЕЛ — `lens/BUILD-1_brief.md` §2). Друга поверхня — ще нема (буде адмінка `ADMIN-1` черги — ті самі токени). Іменний простір стенда: `nav*` — коробка острівця, `nv*` — вміст кнопки (S35 §1).

## Де що живе і як потрапляє в прод

Карта тек і приладів — `REPO_LAYOUT.md`; перелік живих файлів `lens/` · `sessions/` · `tools/` — `lens/EquipLens_INDEX.md` (гейт звіряє його в обидва боки: новий файл у цих теках — рядок в INDEX тим самим комітом).

| що | де | як їде в прод |
|---|---|---|
| сайт | корінь: `index.html` · `data/` · `media/` | GitHub Pages з кореня `main` — коміт у `main` |
| стенд, смоук, прилади | `tools/` | не призначені для публікації, але Pages їх віддає (перехідний стан Р-7) |
| канон, самері, архів, оригінали, `*.md` кореня | `lens/` · `sessions/` · `archive/` · `sources/` | те саме |

Переїзд сайту в `docs/` (Р-7) — лише після того, як Konst перемкне джерело Pages; окремим ходом, з пробою «до/після».

## Гейти перед комітом

`bash tools/env_check.sh` — exit 0; `ENV_INJECT=1 bash tools/env_check.sh` — ✗ прод і «ЗЛОВИВ» смоука й інвентаря (зуби). Усередині: гейт продукту `Lens_validate.py --product .`, `--html` живого стенда, смоук `tools/smoke_v*.js` (чистий і `--inject`), інвентар стенда `tools/stand_inventory.py`, прилади ядра. Правив стенд — смоук обома режимами до коміту. Числа ✓ — у виводі приладу; нормативи стенда — у шапці стенда й останньому самері, не тут. Інструменти (jsdom) ставить `.claude/hooks/session-start.sh` — лише в хмарній сесії (`CLAUDE_CODE_REMOTE=true`; локально — `npm install --prefix ~/.deps jsdom` руками); змінив гейт — правиш хук і `env_check` тим самим комітом.

Прилади ядра запускаються з клону ядра: `../lens-governance`, нема — `/tmp/lens-governance` (`tools/env_check.sh`, рядок `K=`). У режимі Auto їх пропускають вузькі правила дозволу `.claude/settings.json` («так» Konst 19.11.2026) — коли робоча тека сесії — цей репо (корінь з кількох репо цей файл не вантажить). Нова команда приладу ядра — нове вузьке правило там же; широкі правила з інтерпретатором (`Bash(python*)`) Auto відкидає (code.claude.com/docs/en/permission-modes, 20.11.2026).

## Секрети

Нема. Дані людей (аптеки, адреси) — не в прев'ю й не в публічних файлах.

## Тут інакше, ніж у профілі

- Самері — `sessions/EquipLens_session_summary_S<N>_<ТЕМА>.md`, живих рівно 2 (`sessions/README.md`); витіснене — `git mv` в `archive/summaries/` і рядок в INDEX.
- Черга — `lens/EquipLens_CHERGA.md` (свій словник станів у шапці). Журнал аудиту правил — `lens/EquipLens_AUDIT.md`.
- Вироки продукту — у `lens/EquipLens_MASTER_LOCK.md` (значення стенда — не сюди, а в `lens/EquipLens_head_valuesLOCK.md`, `lens/BUILD-1_brief.md` Ф1); З-номери — адреси в `lens/EquipLens_Z_REGISTR.md`, повний текст там, куди адреса веде.
