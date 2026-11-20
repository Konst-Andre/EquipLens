# EquipLens — навігація по репо

> живе доки: існує репо. Кожна зміна структури (нова тека, новий прилад, переїзд) оновлює цей файл у тому ж коміті.
> Зразок — `lens-governance:tools/claude-code/templates/REPO_LAYOUT_template.md`. Місце — корінь, не `docs/`: за Р-7 `docs/` — лише сайт (рішення Konst 19.11.2026, S36).
> Перелік живих файлів `lens/` · `sessions/` · `tools/` для гейта — `lens/EquipLens_INDEX.md`. Тут — теки, прилади й читачі; поштучного переліку не дублюю.

## Порядок читання на старті сесії

0. `bash tools/env_check.sh` (диспетчер ядра кладе його ⚠ / ✗ у перше повідомлення сам)
1. `CLAUDE.md`
2. найновіше самері в `sessions/` — §0 «ВІДКРИТЕ»
3. `lens/EquipLens_CHERGA.md` — цілком; бриф пункту (`lens/<id>_brief.md`) — коли береш пункт
4. точково: `lens/EquipLens_MASTER_LOCK.md` (вироки) → `lens/EquipLens_Z_REGISTR.md` (адреси З-номерів) → специфікації `lens/EquipLens_K21_*`

## Дерево

```
EquipLens/
├─ CLAUDE.md          як працюємо (щосесії)
├─ REPO_LAYOUT.md     ця карта
├─ index.html         живий сайт — «Посібник з POS-обладнання» (GitHub Pages публікує корінь main)
├─ data/  media/      дані й фото; у коді index.html не згадані (греп 19.11.2026)
├─ lens/              канон: черга · MASTER_LOCK · реєстри · специфікації · INDEX (перелік для гейта) · AUDIT
│  ├─ shots/          примірка UI-рішень наперед (README — стан)
│  └─ evidence/       докази вад до примірки (знімки Konst, плівка машини) — оголошено в INDEX, видаляються з закриттям пункту
├─ sessions/          живі самері (стеля 2)
├─ src/               джерела білда (BUILD-1 Ф2): shell.html (оболонка з мітками) · css/ (5 шарів @layer) · js/ · fonts/ (Manrope-підмножина + OFL, згенеровано tools/fonts.py) · brand/ (SVG гліфа й знака, HTML-кадри іконок) і icons/ (PNG) — згенеровано приладом ядра pwa_icon.py з tools/icon.json (знак-напис — tools/brand.py) · manifest.webmanifest
├─ docs/              ЗІБРАНИЙ білд — docs/index.html (tools/build.py build; руками не правити). Тека сайту за Р-7: на гілці й у main (правило — `CLAUDE.md` «Гілка»; Pages віддає за /docs/); адресою людей — з HOST-1 Б
├─ tools/             стенд з важелями, смоук, прилади, збірка
├─ sources/           оригінали (xlsx, zip, фото; fonts/ — Manrope[wght].ttf + OFL, джерело підмножини)
├─ archive/           історія: самері · стенди · матриці — не правиться
└─ .claude/           налаштування Claude Code і хук старту
```

## Прилади

| прилад | що міряє / робить | коли брати | запуск |
|---|---|---|---|
| `.claude/hooks/session-start.sh` | ставить інструменти гейтів: `jsdom` у `~/.deps` + `NODE_PATH` (смоук) · Python-Playwright у парі з браузером образу (детектор «стенд ≡ білд», селф-тести ядра) | сам, на старті сесії (реєстрація — `.claude/settings.json`; сесія з кількома репо — кличе диспетчер ядра) | `CLAUDE_CODE_REMOTE=true .claude/hooks/session-start.sh` |
| `tools/env_check.sh` | база · гейт продукту (`Lens_validate --product`) · прод: `/` ≡ `origin/main:index.html` за вмістом, службове видно — ⚠ · стенд `--html` · смоук · інвентар стенда · `doc_health` · `shots_check` · версія; exit 1 — розібратись до роботи | перший крок кожної сесії (диспетчер ядра кличе сам) | `bash tools/env_check.sh` · зуби: `ENV_INJECT=1 bash tools/env_check.sh` → ✗ прод (підкинута розбіжність; вікна кешу під ним нема) · смоук і інвентар «ЗЛОВИВ» |
| `tools/audit_prompts.sh` | аудит інструкцій моделями (`/doctor prompt-audit`), клас 1 — opus, клас 2 — ще й sonnet; журнал — `lens/EquipLens_AUDIT.md` | змінив `CLAUDE.md` / правило — пакетом перед самері, після заміру лімітів | `bash tools/audit_prompts.sh 2 CLAUDE.md` |
| `tools/smoke_v*.js` | механіка головного стенда (не значення важелів); живий — найбільший номер | після кожної правки стенда | `cd tools && node smoke_v17_30.js` · `--inject` |
| `tools/build.py` | збірка білда `BUILD-1` Ф2 (свій скрипт Python без npm — ARCH-1). **`build`** (Ф2-1): `src/shell.html` → `docs/index.html` — мітки `<!--@src шлях-->` вставляють файл з коментарем-міткою джерела, `<!--@values-->` — JSON-блок значень (екрановано `< > &` і U+2028/9); `build --check` — зібране ≡ закоміченому (руками зібране не правити). **`values`** — джерело чисел: суворий розбір `lens/EquipLens_head_valuesLOCK.md` §3 (рядок за формою · ключ унікальний · число — число · «⚠ межа» ≡ вирок на межі · §0 і §1 ≡ рядкам); `load_values()` — для збірки | `env_check` сам; руками — правив valuesLOCK | `python3 tools/build.py values` · `--check` · `--json` · `--check --inject` → «ЗЛОВИВ» |
| `tools/fonts.py` | шрифт тексту (Ф2-2а): `build` — підмножина Manrope → `src/fonts/manrope.woff2`; `--check` — вісь, версія, бюджет, символи тексту `src/` | правка `sources/fonts/` чи нові символи в UI → `build`, тоді `tools/build.py build` |
| `tools/build_smoke.js` | білд у браузері (Ф2-2а · Ф2-2б · Ф2-3): Chromium без мережі, обидві теми — 0 помилок JS, Manrope малює; оболонка PWA — маніфест і іконки з локального сервера; токени ≡ стенду — обчислений фон `html` білда ≡ `#sbox` стенда, `color-scheme` зі своєю темою, кожна CSS-змінна кореня ≡ стенду + покриття «N з M» (`--list`) | `env_check` (чистий і `--inject`) |
| `tools/brand.py` | знак-напис (Ф2-2б): `wordmark` — «EquipLens» контуром Chillax → `src/brand/wordmark.svg`; `--check` — шапка знака ≡ valuesLOCK | змінились `wSize` · `wTrack` · `wEq` · `wLe` → `wordmark` (`--check` ✗ підкаже); тоді `tools/build.py build` |
| `tools/icon.json` | конфіг іконки для приладу ядра `pwa_icon.py` (`ICON-1`): гліф Н5 зі стенда → `src/brand/` кадри → `src/icons/` PNG; `--check` — кадри ≡ стенду, PNG, маніфест, meta, safe-area | змінився гліф чи кольори стенда, або прилад ядра → `python3 ../lens-governance/tools/claude-code/pwa_icon.py icons tools/icon.json`, тоді `tools/build.py build` |
| `tools/stand_inventory.py` | інвентар стенда `BUILD-1` Ф0: кожне CSS-правило (і в `@media`), статичний елемент з class/id і функція JS → застосунок · harness · токени (обчислення з `S` → генерація в збірці) · мішане (різати на порті). Функції — явною картою `FN`, складені класи — `SAFE`; самоперевірка розбору CSS; ⓘ мертві кандидати `el-*`. **Ф1:** `--values` — засіває `lens/EquipLens_head_valuesLOCK.md` (лише коли файла нема — файл тепер джерело; причини «без лока» — карта `UNLOCKED_*`), `--values --check` — бік стенда: стенд заморожений (ім'я й md5 з шапки), кожен ключ засіву має рядок, нові вироки — ⓘ | `env_check` сам (обидва режими); руками — правив стенд або карту | `python3 tools/stand_inventory.py` · `--list` (кожна одиниця) · `--inject` → «ЗЛОВИВ» · `--values [--check] [--inject]` |
| `tools/EquipLens_K0_passport_audit.js` | аудит паспорта стенда К0 (самері S17 §4) | правка паспорта стенда | `cd tools && node EquipLens_K0_passport_audit.js` (без аргументу — живий стенд; S36: було зашите ім'я `v17`) |

## Хто що читає

| шлях | читач | як |
|---|---|---|
| `index.html` | браузер | GitHub Pages з кореня `main` — кожен коміт у `main` = деплой |
| `lens/` · `sessions/` · `tools/` · `*.md` кореня | люди, агент; **але й Pages** — службове поки публікується (проба 19.11: `/lens/EquipLens_CHERGA.md` → 200) | переїзд сайту в `docs/` (Р-7) прибере — вирішує Konst |
| `tools/EquipLens_headbench_v*.html` | Konst (стенд з важелями, приймання на телефоні) | файл відкривається напряму; у білд портується частинами (`BUILD-1` черги) |
| `src/` → `docs/index.html` (+ `manifest.webmanifest`, `icons/` — файли за мітками `{{v:…}}`) | збірка → браузер | `tools/build.py build`; `docs/` у `main` — `CLAUDE.md` «Гілка»; адресою людей — з HOST-1 Б (воркер `[assets]`), доти Pages віддав би білд ще й з `/docs/` |
| `data/` · `media/` | читача в коді не знайдено | не видаляти без вироку Konst (ADOPT «Чого не робити») |

## Переїзди (старий шлях → новий)

| було | стало | коли |
|---|---|---|
| `lens-governance:products/EquipLens/` | `lens/` · `archive/` | G-Y, 24.09.2026 |
| сайт у корені | `docs/` (Р-7) | ⬜ — після перемикання Pages Konst |
| стенд `tools/EquipLens_headbench_v*.html` (один файл) | дерево джерел (`src/`) + збірка в один HTML (`tools/build.py`), значення — із засіву стенда | 🔄 — `BUILD-1` (`lens/BUILD-1_brief.md`), за `lens-governance:kernel/Lens_ARCH-1_brief.md` (К5 тут; канон дерева в ядрі ще не написаний — К2–К3) |
