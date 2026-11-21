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
| `sessions/EquipLens_session_summary_S40_BG.md` | останнє самері продукту (§0 «ВІДКРИТЕ» — зверху): примірка фону обох тем, розвідка скла (GlassKit «крапля», lgcl) |
| `sessions/EquipLens_session_summary_S39_TOKENS.md` | попереднє: Ф2-3 токени, детектор «токени ≡ стенду» |

Витіснені — `archive/summaries/` (S1…S38; S35 — останнє по стенду, засів `LOCK_SEED` §1).

## Канон

| файл | що |
|---|---|
| `lens/EquipLens_MASTER_LOCK.md` | єдиний канон значень і вироків продукту; межа з QR Lens — §2 |
| `lens/EquipLens_Z_REGISTR.md` | реєстр З-серії: номер → адреса повного тексту → стан (роль — адресація, не переказ) |
| `lens/EquipLens_K21_PANEL_SPEC_v1.md` | специфікація панелі K21 |
| `lens/EquipLens_K21_PANEL_SPEC_v1_ADDENDUM_4b.md` | доповнення 4b до K21 |
| `lens/EquipLens_AUDIT.md` | журнал аудиту інструкцій (`CLAUDE.md` тощо); формула — у ядрі |
| `lens/shots/README.md` | примірка UI-рішень наперед — стан кожної (`SHOTS.md` ядра) |
| `lens/shots/DES-1_bg/fit_bg.js` | примірка фону обох тем — накладка на стенд: важіль основи світлої (OKLCH) і варіанти з джерелами |
| `lens/shots/DES-1_bg/shoot.js` | знімальник примірки фону: збирає сторінку (стенд + накладка), кадри обох тем і дані для машини; `--engine both` — Chromium ⟂ WebKit на ширині iPhone + Pixel 7 |
| `lens/shots/DES-1_bg/check_bg.py` | машина примірки фону: контраст у найгіршій точці · `SUN-1` сонячна проба · жовтизна · різниця варіантів · блиск на склі · кант · «деформація» вздовж верху (`--inject*`); `--engines` — порівняння рушіїв |
| `lens/shots/DES-1_bg/REVIEW_v7.md` | розбір фону v7 по темах і елементах (делеговано Konst S40): таблиця «елемент · що бачу · що роблю» | живе доки примірка без вироку |
| `lens/shots/DES-1_bg/light.webp` | сітка кадрів світлої v8: «Зараз» + 17 варіантів (А, В, Г зняті — Konst S40) |
| `lens/shots/DES-1_bg/dark.webp` | сітка кадрів темної v8: «Зараз» + 11 варіантів (Д1, Д2 старі — не прийнято Konst S40) |
| `lens/evidence/DES-1_swipe/konst_dark_list.webp` · `lens/evidence/DES-1_swipe/konst_dark_open_corners.webp` · `lens/evidence/DES-1_swipe/konst_light_closing_blink.webp` · `lens/evidence/DES-1_swipe/konst_light_open_corners.webp` · `lens/evidence/DES-1_swipe/machine_close_frames_both_themes.webp` | докази бага свайпу картки (`DES-1` п.25): знімки iPhone Konst 20.11.2026 (`konst_*`, стенд, синтетичні дані) + плівка машини (відкрито → закриття кожні 25 мс; верх світла, низ темна). Живе доки: п.25 закрито — тоді видалити |

## Стенди й інструменти

| файл | роль | живе доки |
|---|---|---|
| `tools/EquipLens_headbench_v*.html` | **головний стенд** · живий = найбільший номер під маскою (`gov 12.20`); числа стенда — у його шапці | не витіснений новим стендом |
| `tools/smoke_v*.js` | матриця головного стенда · живий = найбільший номер; ганяти з `--inject` і без | стенд живий |
| `tools/env_check.sh` | перевірка середовища на старті: база · гейт продукту · прод Pages за вмістом · стенд `--html` і смоук · інвентар стенда · прилади ядра; опис — `REPO_LAYOUT.md` | існує репо |
| `tools/audit_prompts.sh` | аудит інструкцій за класом — копія ядра як є (AUD-2) | є аудит інструкцій |
| `tools/build.py` | збірка білда (`BUILD-1` Ф2): `build` — src → docs/index.html (`--check` — зібране ≡ закоміченому, `--inject`) · `values` — розбір джерела чисел (`--check` — форма файла, `--json`, `--inject`); опис — `REPO_LAYOUT.md` | живе застосунок |
| `tools/fonts.py` | шрифт тексту білда (`BUILD-1` Ф2-2а): `build` — підмножина Manrope з `sources/fonts/` → `src/fonts/manrope.woff2` · `--check` — вісь wght 200–800, версія, бюджет 40 000 Б, кожен символ тексту `src/` у шрифті (`--inject`); в `env_check`, fonttools — хук старту |
| `tools/build_smoke.js` | смоук зібраного білда в Chromium (`BUILD-1` Ф2-2а · Ф2-2б): без мережі, обидві теми — 0 помилок JS · Manrope малює (канарка ширини зі стенда) · оболонка PWA з локального сервера — маніфест розбирається, іконки вантажаться й мають свій розмір · `--inject` псує base64 шрифту і б'є іконки → «ЗЛОВИВ» лише коли спіймано обидва; в `env_check` |
| `tools/brand.py` | знак-напис (`BUILD-1` Ф2-2б): `wordmark` — «EquipLens» контуром Chillax → `src/brand/wordmark.svg` (набір лише в пам'яті; звірка з Chromium у самій генерації, `--inject`) · `--check` — шапка ≡ valuesLOCK (`--inject`); в `env_check`. Іконки — прилад ядра (рядок `tools/icon.json`) |
| `tools/icon.json` | конфіг іконки PWA для приладу ядра `lens-governance:tools/claude-code/pwa_icon.py` (`ICON-1`, кукбук A75): стенд, селектор гліфа Н5, тема, ролі шарів, шляхи `src/brand/` · `src/icons/` · маніфест · оболонка · печатка. `icons tools/icon.json` — кадри «скло на аврорі» і PNG (`--sheet <тека>` — аркуш вироку фону); `--check tools/icon.json` — кадри ≡ стенду, PNG, маніфест, meta, safe-area (`--inject`); в `env_check` |
| `tools/stand_inventory.py` | інвентар стенда (`BUILD-1` Ф0): кожне CSS-правило, статичний елемент і функція JS → застосунок · harness · токени · мішане; непоміщене → ✗, `--inject` → «ЗЛОВИВ»; `--values` — засіває valuesLOCK (лише коли файла нема), `--values --check` — бік стенда (`BUILD-1` Ф1); опис — `REPO_LAYOUT.md` | стенд не портовано (`BUILD-1` Ф3) |
| `tools/EquipLens_K0_passport_audit.js` | аудит паспорта стенда К0 (самері S17 §4) | паспорт не переїхав у білд |

## Сайт

Лежить у **корені** (`index.html` · `data/catalog.json` · `data/dicts.json` · `media/`), доки Konst не перемкне Pages на `/docs` (Р-7).
Гейт продукту сайт не судить — білд перевіряє `Lens_validate.py --html`.
