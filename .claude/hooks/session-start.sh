#!/bin/bash
# EquipLens · старт хмарної сесії Claude Code: інструменти для гейтів.
# живе доки: гейти з CLAUDE.md потребують цих інструментів. Змінив гейт чи версію — правиш цей файл ТИМ САМИМ комітом.
# Зразок — lens-governance:tools/claude-code/templates/session_start_template.sh. Реєстрація — .claude/settings.json (SessionStart, без matcher).
# Сесія з кількома репо: Claude Code бере налаштування з /home/user, тож цей хук кличе диспетчер ядра lens-hooks.sh (CLAUDE_CODE.md «Гачки»).
set -euo pipefail
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then exit 0; fi

# смоук стенда (tools/smoke_v*.js) — jsdom; поза репо, щоб не тягнути node_modules у публікацію Pages (сайт — корінь main)
[ -d "$HOME/.deps/node_modules/jsdom" ] || npm install -q --no-save --prefix "$HOME/.deps" jsdom >/dev/null 2>&1 || true
[ -n "${CLAUDE_ENV_FILE:-}" ] && echo "export NODE_PATH=\"$HOME/.deps/node_modules\"" >> "$CLAUDE_ENV_FILE"
# Python-Playwright — пара до браузера образу (не зашите число, PW-1; зразок — lens-governance:tools/claude-code/templates/session_start_template.sh):
#   потрібен детектору «стенд ≡ білд» (lens/BUILD-1_brief.md §5-а Ф3) і селф-тестам приладів ядра (clip · port_same · pw_quiet)
PWV=$(python3 -c "import json;print(json.load(open('/opt/node-tools/node_modules/playwright/package.json'))['version'])" 2>/dev/null || true)
[ -n "$PWV" ] && { python3 -c "import importlib.metadata as m,sys; sys.exit(m.version('playwright')!='$PWV')" 2>/dev/null || pip install -q "playwright==$PWV" >/dev/null 2>&1 || true; }
# шрифт білда (BUILD-1 Ф2-2а): tools/fonts.py build і --check — fonttools + brotli (woff2)
python3 -c "import fontTools, brotli" 2>/dev/null || pip install -q fonttools brotli >/dev/null 2>&1 || pip install -q --break-system-packages fonttools brotli >/dev/null 2>&1 || true
# знак (BUILD-1 Ф2-2б): tools/brand.py icons — Pillow (PNG з печаткою); wordmark — uharfbuzz (розстановка ≡ Chromium). --check — лише playwright-python
python3 -c "import PIL, uharfbuzz" 2>/dev/null || pip install -q pillow uharfbuzz >/dev/null 2>&1 || pip install -q --break-system-packages pillow uharfbuzz >/dev/null 2>&1 || true
echo "session-start: playwright-python ${PWV:-—} · jsdom ($HOME/.deps) · NODE_PATH · fonttools · pillow · uharfbuzz"
