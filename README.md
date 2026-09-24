> живе доки: назавжди (вхід у репо продукту) · розкладка — Р-7, `lens-governance:sessions/Lens_gov/Lens_MIGRATION_GW_ledger.md`

# EquipLens

Польовий нотатник потреби в обладнанні аптек — PWA, один HTML-файл. Окремий продукт від QR Lens (межа — `lens/EquipLens_MASTER_LOCK.md` §2, злиття заборонене).
Правила роботи — у ядрі родини: [`Konst-Andre/lens-governance`](https://github.com/Konst-Andre/lens-governance) (`kernel/`). Цей репо самодостатній: код, канон, самері, стенди — тут.

## Де що

| тека | роль |
|---|---|
| `docs/` | **лише опублікований сайт**: `index.html` · `manifest` · іконки · `data/` · `media/`. Службове сюди не кладеться — сайт може жити на Cloudflare з приватного репо |
| `lens/` | канон продукту: `*_CHERGA` (відкрите) · `*_MASTER_LOCK` · `*_valuesLOCK` · реєстри |
| `sessions/` | живі самері (стеля 2) |
| `archive/` | витіснене: старі самері · стенди · матриці |
| `tools/` | живі стенди · смоуки · скрипти й продуктові гейти |
| `sources/` | вихідні дані (xlsx, zip, фото-оригінали) |

> **Перехідний стан (G-X, 24.09.2026).** Сайт поки лежить у **корені** (`index.html` · `data/` · `media/`) — GitHub Pages публікує `/`.
> Переїзд у `docs/` — лише після того, як Konst перемкне джерело публікації (GitHub Pages → `/docs` · Cloudflare → `docs`).
> Канон, самері й стенди ще живуть у `lens-governance` і в Project — переносяться ходом 2-б журналу.

## Як почати сесію

```bash
curl -sO https://raw.githubusercontent.com/Konst-Andre/lens-governance/main/kernel/Lens_start.py
GH_TOKEN=… python3 Lens_start.py --product EquipLens --summary-of EquipLens
```
Далі — порядок читання з `lens-governance:kernel/Lens_INDEX.md` §1: черга `lens/EquipLens_CHERGA.md` цілком → живе самері з `sessions/` (§0 «ВІДКРИТЕ») → `Work_Standard.md` точково.
