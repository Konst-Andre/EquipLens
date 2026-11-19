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
echo "session-start: jsdom ($HOME/.deps) · NODE_PATH"
