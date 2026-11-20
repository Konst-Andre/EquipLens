> живе доки: назавжди (індекс продукту — дім оголошень EquipLens, Р-9) · читається: першим у продуктовій сесії EquipLens, після `lens-governance:kernel/Lens_INDEX.md`
> дім оголошено: `lens-governance:kernel/Lens_INDEX.md` §5 «Реєстр продуктів» · заведено G-Z 27.09.2026 (хід 7-в журналу переїзду)
> гейт: `python3 <ядро>/kernel/Lens_validate.py --product <корінь цього репо>` — G24 · G1 · G3 · G10 · G14 (Р-4′: гейт перевіряє лише свій репо)

# EquipLens · INDEX — що живе в цьому репо

**Як читати.** Шляхи — від кореня репо. Гейт продукту звіряє файли `lens/` · `sessions/` · `tools/` з цим індексом
**в обидва боки**: неоголошений файл → ✗, оголошений без файлу → ✗. `archive/` — історія, не оголошується поштучно.
Правила роботи — у ядрі (`lens-governance:kernel/`); тут — лише що живе і де.

## Черга

| файл | роль |
|---|---|
| `lens/EquipLens_CHERGA.md` | відкрите по продукту, читається цілком на старті. Стеля — `Lens_INDEX §5` ядра (12 пунктів, 30 днів) |

## Брифи (пункти черги на 2+ сесії)

| файл | що |
|---|---|
| `lens/DES-1_brief.md` | бриф `DES-1`: дизайн і доводка екранів білда (нові екрани + старі пункти стенда з вироками Konst) |
| `lens/BUILD-1_brief.md` | бриф `BUILD-1`: порт стенда в PWA |
| `lens/EquipLens_head_valuesLOCK.md` | **джерело чисел продукту** (рішення Konst 20.11.2026; засіяно зі стенда `v17_30`, правиться лише вироком пристрою): засів 244 · на межі повзунка · без лока з причиною (`BUILD-1` Ф1) |
| `lens/HOST-1_brief.md` | бриф `HOST-1`: Pages → Cloudflare Workers |
| `lens/BACK-1_brief.md` | бриф `BACK-1`: бекенд і сховище (записи й фото кожного представника, офлайн, вхід) |

## Живі самері (стеля 2)

| файл | що |
|---|---|
| `sessions/EquipLens_session_summary_S38_FONTS.md` | останнє самері продукту (§0 «ВІДКРИТЕ» — зверху): Ф2-2 шрифти й маніфест, ліцензія Chillax прочитана |
| `sessions/EquipLens_session_summary_S37_TOOLS_HOST.md` | попереднє: прилади як в AE, воркер, стенд очима, Ф1–Ф2-1 |

Витіснені — `archive/summaries/` (S1…S36; S35 — останнє по стенду, засів `LOCK_SEED` §1).

## Канон

| файл | що |
|---|---|
| `lens/EquipLens_MASTER_LOCK.md` | єдиний канон значень і вироків продукту; межа з QR Lens — §2 |
| `lens/EquipLens_Z_REGISTR.md` | реєстр З-серії: номер → адреса повного тексту → стан (роль — адресація, не переказ) |
| `lens/EquipLens_K21_PANEL_SPEC_v1.md` | специфікація панелі K21 |
| `lens/EquipLens_K21_PANEL_SPEC_v1_ADDENDUM_4b.md` | доповнення 4b до K21 |
| `lens/EquipLens_AUDIT.md` | журнал аудиту інструкцій (`CLAUDE.md` тощо); формула — у ядрі |
| `lens/shots/README.md` | примірка UI-рішень наперед — стан кожної (`SHOTS.md` ядра) |
| `lens/evidence/DES-1_swipe/konst_dark_list.webp` · `lens/evidence/DES-1_swipe/konst_dark_open_corners.webp` · `lens/evidence/DES-1_swipe/konst_light_closing_blink.webp` · `lens/evidence/DES-1_swipe/konst_light_open_corners.webp` · `lens/evidence/DES-1_swipe/machine_close_frames_both_themes.webp` | докази бага свайпу картки (`DES-1` п.25): знімки iPhone Konst 20.11.2026 (`konst_*`, стенд, синтетичні дані) + плівка машини (відкрито → закриття кожні 25 мс; верх світла, низ темна). Живе доки: п.25 закрито — тоді видалити |

## Стенди й інструменти

| файл | роль | живе доки |
|---|---|---|
| `tools/EquipLens_headbench_v*.html` | **головний стенд** · живий = найбільший номер під маскою (`gov 12.20`); числа стенда — у його шапці | не витіснений новим стендом |
| `tools/smoke_v*.js` | матриця головного стенда · живий = найбільший номер; ганяти з `--inject` і без | стенд живий |
| `tools/env_check.sh` | перевірка середовища на старті: база · гейт продукту · прод Pages за вмістом · стенд `--html` і смоук · інвентар стенда · прилади ядра; опис — `REPO_LAYOUT.md` | існує репо |
| `tools/audit_prompts.sh` | аудит інструкцій за класом — копія ядра як є (AUD-2) | є аудит інструкцій |
| `tools/build.py` | збірка білда (`BUILD-1` Ф2): `build` — src → docs/index.html (`--check` — зібране ≡ закоміченому, `--inject`) · `values` — розбір джерела чисел (`--check` — форма файла, `--json`, `--inject`); опис — `REPO_LAYOUT.md` | живе застосунок |
| `tools/stand_inventory.py` | інвентар стенда (`BUILD-1` Ф0): кожне CSS-правило, статичний елемент і функція JS → застосунок · harness · токени · мішане; непоміщене → ✗, `--inject` → «ЗЛОВИВ»; `--values` — засіває valuesLOCK (лише коли файла нема), `--values --check` — бік стенда (`BUILD-1` Ф1); опис — `REPO_LAYOUT.md` | стенд не портовано (`BUILD-1` Ф3) |
| `tools/EquipLens_K0_passport_audit.js` | аудит паспорта стенда К0 (самері S17 §4) | паспорт не переїхав у білд |

## Сайт

Лежить у **корені** (`index.html` · `data/catalog.json` · `data/dicts.json` · `media/`), доки Konst не перемкне Pages на `/docs` (Р-7).
Гейт продукту сайт не судить — білд перевіряє `Lens_validate.py --html`.
