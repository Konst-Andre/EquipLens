> живе доки: до наступного самері EquipLens (тоді → `archive/summaries/`)
> **Дім:** `sessions/` (живе самері, стеля 2 — `sessions/README.md`). Черга — `lens/EquipLens_CHERGA.md`.
> Сесія: самостійна сесія Konst (резервний акаунт), продовження S36. Гілка харнеса `claude/trusting-brahmagupta-7ru963` (S36 називала `claude/equiplens-cc-adopt` — обидві на `f41c6e3`, ≡ `origin/main`). Репо сесії: EquipLens · lens-governance (запис — `main` ядра) · на читання AE-Simulator · QR-Lens · AirLens (дозвіл Konst 20.11.2026).

# EquipLens · S37 — прилади як в AE, воркер, стенд очима

**Що ти побачиш:** рішення Konst 20.11 записані (аудит — лише за командою · «Посібник» → архів · новий `TOOLS-1` · воркер — план); стенд `v17_30` подивлений на телефонному розмірі; рядки ядра п.7-г — план, чекає «так».

---

## §0 · ВІДКРИТЕ

1. **Борг ядра (S36 §0 п.7-г) — план показано, чекає «так» Konst і вибору А/Б:** шаблон `lens-governance:tools/claude-code/templates/CLAUDE_template.md`:26 · «Черга» `lens-governance:tools/claude-code/ADOPTIONS.md` (+ рядки журналу 22–23 стоять не в тій таблиці · тест EquipLens ⬜ → ✅ · рядок AirLens). Звірка: code.claude.com/docs/en/hooks (20.11.2026) — «`$CLAUDE_CODE_REMOTE` is `"true"` in remote web environments and not set in the local CLI». Греп продуктів: хук старту з тим самим вартовим — `AE-Simulator:.claude/hooks/session-start.sh`:8 · `QR-Lens:.claude/hooks/session-start.sh`:7 · `AirLens:.claude/hooks/session-start.sh`:7 (там ще `--force`); фраза «руками» без `--force` — лише `AirLens:CLAUDE.md`:20.
   **Питання Konst 20.11 «агент ставить руками?» — ні:** у хмарній сесії (Konst працює лише в ній) усе ставить хук сам; доказ — журнал гачків цієї сесії `/tmp/lens-repo-hooks.log`: «session-start: playwright-python 1.63.0 · jsdom · NODE_PATH» на старті, руками нічого не ставилось. «Руками» — лише для сесії на власному ПК (терміналі), де хук свідомо мовчить. Дозволи в setup script (`permissions.allow`) — інше: вони пускають команди приладів ядра в режимі Auto без питань, нічого не встановлюють.
2. **Аудит правил — лише за командою Konst** (20.11.2026: «запустимо його за моєю командою, не зараз»). Борг ядра «8 комітів» — чекає команди.
3. **(г) переглянуто Konst:** старий «Посібник» (`index.html` кореня) → **архів**, не підшлях (`lens/BUILD-1_brief.md` §3). Прибрати з кореня = зміна проду Pages → окремим ходом із «так»; порядок з п.4.
4. **`HOST-1` — Konst 20.11: «створити воркер під цей проєкт» (токен, конектор, дозвіл).** Факти 20.11: токен ✓ (`user/tokens/verify` 200), у акаунті 6 воркерів (`ae-edit` · `ae-simulator` · `airlens` · `lens-gh` · `qr-admin` · `qr-lens`), `equiplens` нема. План і вилка «що воркер віддає, доки білда нема» — у звіті ходу 2; виконання (створення воркера, Workers Builds) — прод-крок, окремим «так».
5. **Стенд очима:** `tools/EquipLens_headbench_v17_30.html` відкрито в Chromium з розміром iPhone — 0 помилок JS, видно телефон зі списком 20 аптек, острівець, «+», важелі під ним. Стенд **уже публічний**: Pages віддає `https://konst-andre.github.io/EquipLens/tools/EquipLens_headbench_v17_30.html` (200, 378 129 Б ≡ репо). **Чекає Konst:** назви аптек і вулиці в стенді (Подорожник, 9-1-1, АНЦ… · вул. Шевченка, 12) — справжні чи вигадані? `CLAUDE.md` «Секрети»: дані аптек — не в публічних файлах; до відповіді копію в sandbox не кладу.
6. **`TOOLS-1` (новий, черга §1):** прилади й машина як в AE «і навіть більше» — перелік «беремо / не беремо» з реєстру ядра «Прилади продуктів».
7. **Konst пояснить, що за проєкт** — наступним повідомленням; дім — визначу, коли прийде (кандидат — `lens/EquipLens_MASTER_LOCK.md`).
8. **З S36, без змін:** лишок §0 п.6 (`З-57` зіпсований рядок) · 💡 чекають вироку: п.7 (іспит у кінці сесії) · п.7-б (печатка «0 справжніх») · п.7-в (постійний дозвіл на fast-forward `main`). Далі за чергою: `BUILD-1` Ф1 valuesLOCK → `Г-11`.

## §1 · ХІД

| # | що | коміт |
|---|---|---|
| 1 | Старт: `env_check` (⚠ версія — відомо) · прийом · план ядра п.7-г з мікроскопом і другим поглядом; звірка документації (web-fetch) і греп AirLens; AE / QR — класифікатор Auto відхилив `add_repo` | — |
| 2 | Konst 20.11: аудит — за командою · дозвіл на AE / QR (клоновано) · «Посібник» → архів · воркер · стенд очима і прев'ю · `TOOLS-1` · пояснення проєкту — далі. Самері народилось; S35 → `archive/summaries/` | цей коміт |

## §6 · Стартове повідомлення наступної сесії

```text
EquipLens — самостійна сесія Konst. Продовження S37.
Середовище «Lens» (lens-governance:tools/claude-code/ENVIRONMENT.md). Репо: Konst-Andre/EquipLens + Konst-Andre/lens-governance (ядро — запис у main за його CLAUDE.md); на читання — AE-Simulator, QR-Lens (дозвіл Konst 20.11).
main EquipLens = прод GitHub Pages: коміт у main — лише з «так» Konst; робота — на гілці харнеса.
Старт: bash tools/env_check.sh → CLAUDE.md → REPO_LAYOUT.md → sessions/EquipLens_session_summary_S37_TOOLS_HOST.md §0 → lens/EquipLens_CHERGA.md цілком.
Відкрите — S37 §0: рядки ядра п.1 (чекає «так» А/Б) · HOST-1 воркер (план, «так») · «Посібник» → архів · стенд — дані справжні? · TOOLS-1 · BUILD-1 Ф1.
```
