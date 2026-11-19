> живе доки: назавжди (вхід у репо продукту) · розкладка — Р-7, `lens-governance:sessions/Lens_gov/Lens_MIGRATION_GW_ledger.md`

# EquipLens

Продукт сімейства Lens (PWA). Що це, стан і як працюємо — `CLAUDE.md`; карта — `REPO_LAYOUT.md`.
Правила роботи — у ядрі родини: [`Konst-Andre/lens-governance`](https://github.com/Konst-Andre/lens-governance) (`kernel/`). Цей репо самодостатній: код, канон, самері, стенди — тут.

## Де що

| тека | роль |
|---|---|
| `docs/` | **лише опублікований сайт** (Р-7) — теки ще нема: сайт у корені, див. нижче |
| `lens/` | канон продукту: `*_CHERGA` (відкрите) · `*_MASTER_LOCK` · `*_valuesLOCK` (з'явиться на Ф1 `lens/BUILD-1_brief.md`) · реєстри |
| `sessions/` | живі самері (стеля 2) |
| `archive/` | витіснене: старі самері · стенди · матриці |
| `tools/` | живі стенди · смоуки · скрипти й продуктові гейти |
| `sources/` | вихідні дані (xlsx, zip, фото-оригінали) |

> **Перехідний стан (G-X, 24.09.2026).** Сайт поки лежить у **корені** (`index.html` · `data/` · `media/`) — GitHub Pages публікує `/`.
> Переїзд у `docs/` — лише після того, як Konst перемкне джерело публікації (GitHub Pages → `/docs` · Cloudflare → `docs`).
> **Хід 2-б завершено (G-Z, 27.09.2026):** канон, самері, стенди й архів EquipLens живуть **лише тут** — ядро `lens-governance` їх більше не тримає, Project — теж.
> Що живе — оголошує `lens/EquipLens_INDEX.md`; гейт продукту: `python3 <lens-governance>/kernel/Lens_validate.py --product .`

## Як почати сесію

Claude Code: `CLAUDE.md` (як працюємо) → `REPO_LAYOUT.md` (карта) → `bash tools/env_check.sh` (диспетчер ядра кличе його сам).
Прилади ядра — з клону `lens-governance` поруч або `/tmp/lens-governance`, не `curl` з `main` (`lens-governance:tools/claude-code/ADOPT.md` 4-а).
