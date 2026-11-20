#!/usr/bin/env bash
# EquipLens — перевірка середовища на старті сесії: база · мережа · змінні · гейти · живий прод.
# живе доки: існує репо (перший крок кожної сесії; див. CLAUDE.md). Запуск: bash tools/env_check.sh · зуби: ENV_INJECT=1 bash tools/env_check.sh
# ⚠ Змінив гейт, шлях публікації чи воркера — правиш цей файл ТИМ САМИМ комітом.
# Зразок — lens-governance:tools/claude-code/templates/env_check_template.sh. Значення змінних НЕ друкуються ніколи.
set -u
cd "$(dirname "$0")/.."

# ── налаштувати під репо ──
EXTRA_VARS=""                  # секретів EquipLens не має; імена змінних середовища через пробіл (значення не друкуються), напр. "GROQ_KEY BOT_TOKEN"
K=../lens-governance; [ -d "$K" ] || K=/tmp/lens-governance
GATE_CMD="python3 $K/kernel/Lens_validate.py --product ."  # головний гейт; останній рядок виводу — підсумок, напр. "node tools/validate.js"
SUMDIR="sessions"           # тека самері (продукт Lens — sessions)
AUDITF="lens/EquipLens_AUDIT.md"          # журнал аудиту правил (продукт Lens — lens/<Продукт>_AUDIT.md)
code() { curl -sS -m 10 -o /dev/null -w '%{http_code}' "$1" 2>/dev/null || true; }

# база
git fetch -q origin main 2>/dev/null || true
echo "база: HEAD $(git rev-parse --short HEAD) · origin/main $(git rev-parse --short origin/main 2>/dev/null) (origin/main попереду на $(n=$(git rev-list --count HEAD..origin/main 2>/dev/null); printf %s "${n:-?}"; [ "${n:-0}" != 0 ] && printf " — треба pull"))"

# мережа · змінні · гейти · аудит
g=$(code https://api.github.com/)
vars=""; for v in GH_TOKEN $EXTRA_VARS; do [ -n "${!v:-}" ] && vars+="$v=так " || vars+="$v=ні "; done
gate=$(bash -c "$GATE_CMD" 2>&1 | tail -1)
case "$gate" in *"✗ 0"*) ;; *) fail=1;; esac   # ✗ гейта продукту = exit 1 (S36: без цього рядка новий файл поза INDEX проходив)
last=$(grep -m1 -oE "^\| 20[0-9]{2}-[0-9]{2}-[0-9]{2}" "$AUDITF" 2>/dev/null | tr -d '| ')
if [ -n "$last" ]; then days=$(( ( $(date +%s) - $(date -d "$last" +%s) ) / 86400 )); [ "$days" -gt 30 ] && aud="аудит правил: $days дн. — ПОРА" || aud="аудит правил: $days дн. тому"; else aud="аудит правил: журналу нема"; fi
INSTR="CLAUDE.md .claude/settings.json"              # файли інструкцій репо (skills, профіль у репо — дописати)
# AUD-2 · AUD-4 (19.10.2026): борг пакетного аудиту — коміти в інструкціях ПІСЛЯ останнього коміту журналу аудиту (той самий день теж видно).
# Не борг: позначка «аудит: клас 0» / «за аудитом» у будь-якому рядку повідомлення (будь-який регістр) · межа неглибокого клону — $GIT_DIR/shallow,
# по одному коміту в рядку; без батька її дифф «додає» всі файли (git-scm.com/docs/shallow, 18.10.2026; AE S90 — хибні 22 файли).
# «ПОРА» — ≥ 5 файлів у борзі або найстаріший коміт боргу ≥ 7 дн. (числа — пропозиція AUD-4 08.10, «так» Konst 19.10; переглянути після 2–3 пакетів).
shallow="$(git rev-parse --git-path shallow)"; jc=$(git log -1 --format=%H -- "$AUDITF" 2>/dev/null); debt=0; dfiles=""; oldest=""
[ -n "$jc" ] && for h in $(git rev-list "$jc"..HEAD -- $INSTR 2>/dev/null); do
  grep -qx "$h" "$shallow" 2>/dev/null && continue
  git show -s --format=%B "$h" | grep -qiE 'аудит: клас 0|за аудитом' && continue
  debt=$((debt+1)); dfiles="$dfiles $(git show --name-only --format= "$h" -- $INSTR | tr '\n' ' ')"; oldest=$(git show -s --format=%ct "$h")
done
if [ "$debt" -gt 0 ]; then nf=$(printf '%s\n' $dfiles | sort -u | grep -c .); age=$(( ( $(date +%s) - oldest ) / 86400 ))
  aud="$aud · ⚠ борг аудиту: $debt коміт(ів), $nf файл(ів), найстаріший $age дн."
  { [ "$nf" -ge 5 ] || [ "$age" -ge 7 ]; } && aud="$aud — ПОРА пакет за класом (lens-governance:tools/claude-code/templates/AUDIT_template.md)"; fi
echo "env: github=${g:-000} · ${vars% } · гейт: $gate · $aud"
[ -f "$K/tools/claude-code/profile_check.sh" ] && bash "$K/tools/claude-code/profile_check.sh"   # профіль: з репо (LENS_PROFILE=1) чи з налаштувань акаунта — lens-governance:tools/claude-code/ACCOUNT_MOVE.md п.1-а / 1-б

# самері — живий журнал (профіль Konst, САМЕРІ): коміти агента (трейлер Claude-Session) після останнього оновлення самері.
# >0 → попередня сесія комітила, не оновивши самері: звірити git log і дописати §0/§1 ДО роботи. Коміти Konst і ботів не рахуються.
sm=$(git log -1 --format=%h -- "$SUMDIR" 2>/dev/null)
if [ -z "$sm" ]; then echo "самері: — (у $SUMDIR ще нема)"
else n=$(git rev-list --count --grep='Claude-Session' "$sm"..HEAD 2>/dev/null); [ "${n:-0}" -gt 0 ] && echo "⚠ самері відстає: після $sm комітів агента без самері — $n (git log $sm..HEAD)" || echo "самері: ≡ (останнє оновлення $sm)"; fi

# браузер гейтів (wsd 1.21 п.4, AE S103) — лишити, якщо в репо є прилади Playwright: справжній запуск Chromium з Python і Node; розбіжність пакета
#   й образу видно тут, а не падінням гейтів за 1 с через пів години (AE S103: образ дав chromium-1243, хук ставив зашите 1.56.0 під 1194)
# pyb=$(timeout 60 python3 -c "from playwright.sync_api import sync_playwright as s
# with s() as p: b=p.chromium.launch(); print(b.version.split('.')[0]); b.close()" 2>/dev/null) && pyb="python ✓ $pyb" || pyb="python ✗ — хук старту не поставив пару образу"
# ndb=$(cd /tmp && timeout 60 node -e "import('/opt/node-tools/node_modules/playwright/index.mjs').then(async({chromium})=>{const b=await chromium.launch();console.log(b.version().split('.')[0]);await b.close()})" 2>/dev/null) && ndb="node ✓ $ndb" || ndb="node ✗"
# case "$pyb $ndb" in *✗*) echo "⚠ браузер: $pyb · $ndb";; *) echo "браузер: $pyb · $ndb";; esac

# прод (лише читання): GitHub Pages з кореня main. Живий index.html ≡ origin/main — за ВМІСТОМ; службове видно (перехідний стан Р-7 — ⚠).
#   Pages віддає Cache-Control: max-age=600 і не дає його змінити (GitHub Support, webapps.stackexchange 119294; звірено 19.11.2026) →
#   запит з ?cb=, а розбіжність ≤ 15 хв після коміту в main — ⚠ «кеш / деплой іде», не ✗. Під ENV_INJECT вікна нема: підкинуте — завжди ✗ (S36: у вікні зуби глухли).
SITE=https://konst-andre.github.io/EquipLens
lm=$(git show origin/main:index.html 2>/dev/null | md5sum | cut -c1-12); pm=$(curl -sS -m 20 "$SITE/?cb=$(date +%s)" 2>/dev/null | md5sum | cut -c1-12)
[ -n "${ENV_INJECT:-}" ] && pm=000000000000
mage=$(( $(date +%s) - $(git log -1 --format=%ct origin/main 2>/dev/null || echo 0) ))
if [ "$lm" = "$pm" ]; then pr="прод: / ≡ origin/main:index.html ($pm)"
elif [ "$mage" -le 900 ] && [ -z "${ENV_INJECT:-}" ]; then pr="⚠ прод: / ($pm) ≠ origin/main ($lm) — коміт у main $((mage/60)) хв тому: кеш Pages / деплой іде, перевір за 10 хв"
else pr="✗ прод: / ($pm) ≠ origin/main:index.html ($lm) — деплой не дійшов або сайт правили не з репо"; fail=1; fi
q=$(curl -sS -m 10 "$SITE/lens/EquipLens_CHERGA.md" 2>/dev/null | head -c 600 | grep -c 'ЧЕРГА')
[ "${q:-0}" -gt 0 ] && pr="$pr · ⚠ службове публікується (/lens/… — вміст видно; Р-7: сайт → docs/, вирішує Konst)"
echo "$pr"

# стенд і смоук: живий = найбільший номер під маскою (lens/EquipLens_INDEX.md); смоук потребує jsdom (хук старту)
st=$(ls tools/EquipLens_headbench_v*.html 2>/dev/null | sort -V | tail -1); sm=$(ls tools/smoke_v*.js 2>/dev/null | sort -V | tail -1)
h=$(python3 "$K/kernel/Lens_validate.py" --html "$st" 2>&1 | tail -1)
s=$(cd tools && NODE_PATH="$HOME/.deps/node_modules${NODE_PATH:+:$NODE_PATH}" timeout 300 node "$(basename "$sm")" ${ENV_INJECT:+--inject} 2>&1 | tail -1)
echo "стенд $(basename "$st"): --html${h#*ПІДСУМОК:} · смоук $(basename "$sm")${ENV_INJECT:+ --inject}: $s"
if [ -n "${ENV_INJECT:-}" ]; then case "$s" in *ЗЛОВИВ*) ;; *) echo "✗ смоук --inject не зловив підкинутий дефект — гейт без зубів"; fail=1;; esac
else case "$h" in *"✗ 0"*) ;; *) fail=1;; esac; case "$s" in *"✗0"*) ;; *) fail=1;; esac; fi
# інвентар стенда (BUILD-1 Ф0): кожна одиниця — застосунок / harness / токени / мішане; непоміщене → ✗
iv=$(python3 tools/stand_inventory.py ${ENV_INJECT:+--inject} 2>&1 | tail -1); echo "інвентар стенда${ENV_INJECT:+ --inject}: $iv"
if [ -n "${ENV_INJECT:-}" ]; then case "$iv" in ЗЛОВИВ) ;; *) echo "✗ інвентар --inject не зловив підкинуте — гейт без зубів"; fail=1;; esac
else case "$iv" in *"✓ ───"*) ;; *) fail=1;; esac; fi
# джерело чисел (BUILD-1, рішення Konst 20.11.2026): lens/EquipLens_head_valuesLOCK.md — форма (build.py) і бік стенда (стенд заморожений,
# кожен ключ засіву має рядок; нові вироки — ⓘ). Обидва з зубами --inject
# + збірка (BUILD-1 Ф2-1): docs/index.html ≡ зібраному з src/ і valuesLOCK
# + шрифт (Ф2-2а): src/fonts/manrope.woff2 — вісь, версія, бюджет, кожен символ тексту src/ (fonttools — хук старту)
# + знак (Ф2-2б): гліф іконок ≡ стенду (Chromium), PNG розмір · непрозорість · печатка, маніфест, meta оболонки, safe-area
for vc in "build.py values --check" "stand_inventory.py --values --check" "build.py build --check" "fonts.py --check" "brand.py --check"; do
  vl=$(python3 tools/$vc ${ENV_INJECT:+--inject} 2>&1 | tail -1); echo "${vc#* } · ${vc%% *}${ENV_INJECT:+ --inject}: $vl"
  if [ -n "${ENV_INJECT:-}" ]; then case "$vl" in ЗЛОВИВ) ;; *) echo "✗ valuesLOCK · ${vc%% *} --inject не зловив підкинуте — гейт без зубів"; fail=1;; esac
  else case "$vl" in *"✓ ───"*) ;; *) fail=1;; esac; fi
done

# білд у браузері (Ф2-2а · Ф2-2б): Chromium без мережі, обидві теми — 0 помилок JS і Manrope справді малює (канарка ширини);
# оболонка PWA з локального сервера — маніфест розбирається, кожна іконка вантажиться й має заявлений розмір
bs=$(timeout 180 node tools/build_smoke.js ${ENV_INJECT:+--inject} 2>&1 | tail -1); echo "білд у браузері${ENV_INJECT:+ --inject}: $bs"
if [ -n "${ENV_INJECT:-}" ]; then case "$bs" in ЗЛОВИВ) ;; *) echo "✗ build_smoke --inject не зловив зіпсований шрифт чи биті іконки — гейт без зубів"; fail=1;; esac
else case "$bs" in *"✓ ───"*) ;; *) fail=1;; esac; fi

# Спільні інструменти ядра — з КЛОНУ ядра поруч ($K, як профіль вище): виклик, не копія. Клон кладе setup script v3 середовища; нема клону — рядки «ядра поруч нема»: налаштувати середовище, не обходити curl-ом
# (lens-governance:tools/claude-code/CLAUDE_CODE.md «Гачки»: ядро серед репо сесії або /tmp/lens-governance), тож «curl | python» з main — зайвий шлях
# виконання віддаленого коду (скрипт з гілки — ризик ланцюга постачання; випадок —
# lens-governance:tools/claude-code/ADOPTIONS.md, рядок AE 18.10.2026).
CC="$K/tools/claude-code"
# документи — ціна читання в Claude Code (ядро DOC-1: щосесійні ≤ 200 рядків · старт ≤ 25 КБ · розділ ≤ 16 КБ · > 80 КБ з маршрутом); лише ⚠, exit 0
if [ -f "$CC/doc_health.py" ]; then python3 "$CC/doc_health.py" .; else echo "документи: — (ядра поруч нема: $K)"; fi

# примірка — тека <документація>/shots/ (lens-governance:tools/claude-code/SHOTS.md): ✗ знімок без рядка · жива без знімків · файли після «прийнято»; ⚠ вік, вага, без накладки.
# Теки нема — рядок «теки shots/ нема» (продукт без UI-рішень наперед — так і є).
if [ -f "$CC/shots_check.py" ]; then python3 "$CC/shots_check.py" . || fail=1; else echo "примірка: — (ядра поруч нема: $K)"; fi
# версія застосунку B · rev (VER-1, lens-governance:tools/claude-code/VERSIONS.md) — лише репо з інтерфейсом; параметри свого продукту:
#   --code <файл коду застосунку> --re '<мітка: група B, група rev>' [--name '<шлях файлу білда з групою B>']
echo "⚠ версія: мітки ще нема — білда нема, є лише стенд (VER-1 — разом з білдом)"
# if [ -f "$CC/version_check.py" ]; then python3 "$CC/version_check.py" . --code <файл> --re '<регулярка>' ${ENV_INJECT:+--inject} || fail=1; else echo "версія: — (ядра поруч нема: $K)"; fi
# зуби: ENV_INJECT=1 bash tools/env_check.sh — прилади з --inject підкидають ваду й мусять дати ✗ (зразок — QR-Lens:tools/env_check.sh; аудит 24.10.2026).
# Мітки в коді ще нема (продукт заводить версію) — рядок «⚠ версія: мітки ще нема», не ✗ (зразок — AE-Simulator:tools/env_check.sh).

# Cloudflare — СПІЛЬНИЙ акаунт усіх проєктів: бюджет (запити · збірки · прогноз) і свіжість правил. Рядки «⚠» — читати й діяти
# за lens-governance:tools/cloudflare/CLOUDFLARE.md. Скрипт лише читає й завжди exit 0. Репо без Cloudflare — прибрати цей рядок, а також c= / cloudflare= у «мережа» і CLOUDFLARE_* у vars вище.
# EquipLens без Cloudflare — рядок cf_budget прибрано.

[ "${g:-000}" = "000" ] && exit 1
[ "${fail:-0}" = 1 ] && exit 1   # ✗ спільного інструмента (примірка, версія) — «exit 1 — розібратись до роботи» (CLAUDE.md репо; зразок — lens-governance:tools/claude-code/templates/CLAUDE_template.md)
exit 0
