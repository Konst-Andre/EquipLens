#!/usr/bin/env python3
# живе доки: живе застосунок EquipLens (збірка білда — BUILD-1 Ф2 і далі)
"""Збірка білда EquipLens (BUILD-1 Ф2; будова — lens-governance:kernel/Lens_ARCH-1_brief.md §4 «Збірка»).

Зараз — лише перша частина: ДЖЕРЕЛО ЧИСЕЛ (рішення Konst 20.11.2026, S37).
`lens/EquipLens_head_valuesLOCK.md` — єдине джерело значень продукту: народився генерацією зі засіву
стенда v17_30 (`tools/stand_inventory.py --values`, одноразово — генератор не перезаписує), далі
правиться рядком §3 лише вироком пристрою. Збірка читає §3 цим розбором і вшиває значення JSON-блоком
(ARCH-1: дані — JSON-блоком). Практика: файл у git — єдине джерело, руками пишеться лише він, решта
генерується; один автор на токен (martinfowler.com «Design Token-Based UI Architecture», 20.11.2026).

  python3 tools/build.py values            — розбір: число ключів і типів
  python3 tools/build.py values --json     — значення JSON-ом (для збірки й проб)
  python3 tools/build.py values --check    — суворий розбір: кожен рядок §3 за формою · ключ унікальний ·
                                             число — число · позначка «⚠ межа» ≡ вирок на межі · §0 «засів: N» і «на межі: N» ≡ рядкам · §1 «на межі» ≡ рядкам,
                                             де вирок = min чи max свого повзунка → ✗ (exit 1)
  … --check --inject                       — підкидає дубль ключа й «число» з літерою → «ЗЛОВИВ»
  python3 tools/build.py build             — src/shell.html → docs/index.html: мітки <!--@src шлях--> (шлях від src/)
                                             вставляють файл з коментарем-міткою джерела; <!--@values--> — JSON-блок
                                             значень (екрановано < > & U+2028/9 як \u003c… — практика Django,
                                             adamj.eu «Safely including data for JavaScript», 20.11.2026); звіт розміру
  python3 tools/build.py build --check     — зібране в пам'яті ≡ закоміченому docs/index.html (і відсутній файл,
                                             і мітка без файла) → ✗; з --inject — змінює джерело в пам'яті → «ЗЛОВИВ»
Лише stdlib. Наступні частини — BUILD-1 §4-в: Ф2-2 маніфест і шрифти · Ф2-3 токени.
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VALUES = os.path.join(ROOT, 'lens', 'EquipLens_head_valuesLOCK.md')
ROW = re.compile(r'^\| `(\w+)` \| ([^|]*?) \| ([^|]*?) \| (число|вибір) \| ([^|]*?) \| ([^|]*?) \|$')
RNG = re.compile(r'^(-?[\d.]+)…(-?[\d.]+) · ([\d.]+)$')


def parse(text):
    """§3 → {ключ: значення}; помилки форми — списком (жоден рядок §3 не пропускається мовчки)."""
    errs, vals, kinds, edge_calc = [], {}, {}, []
    sec = re.split(r'^## ', text, flags=re.M)
    s3 = next((x for x in sec if x.startswith('§3')), None)
    if s3 is None:
        return {}, {}, ['нема розділу «## §3» — збірці нема звідки брати числа']
    body = [l for l in s3.splitlines()[1:] if l.startswith('|')][2:]   # без шапки й |---|
    for n, l in enumerate(body, 1):
        m = ROW.match(l)
        if not m:
            errs.append(f'§3 рядок {n} не за формою: {l[:70]}')
            continue
        k, v, _, kind, rng, mark = m.groups()
        if k in vals:
            errs.append(f'§3 ключ двічі: {k}')
        if kind == 'число':
            try:
                x = float(v)
            except ValueError:
                errs.append(f'§3 {k}: «{v}» — не число')
                continue
            r = RNG.match(rng)
            on = bool(r) and x in (float(r.group(1)), float(r.group(2)))
            if on:
                edge_calc.append(k)
            if on != (mark.strip() == '⚠ межа'):
                errs.append(f'§3 {k}: позначка «⚠ межа» ' + ('бракує' if on else 'зайва') + ' — вирок ' + ('на межі' if on else 'не на межі'))
            v = int(x) if x == int(x) and '.' not in v else x
        elif not v:
            errs.append(f'§3 {k}: порожній вибір')
        vals[k], kinds[k] = v, kind
    m0 = re.search(r'засів: \*\*(\d+)\*\*', text)
    if not m0:
        errs.append('§0 без «засів: **N**»')
    elif int(m0.group(1)) != len(vals):
        errs.append(f'§0 каже засів {m0.group(1)}, у §3 рядків {len(vals)} — онови §0')
    m1 = re.search(r'на межі повзунка: \*\*(\d+)\*\*', text)
    if m1 and int(m1.group(1)) != len(edge_calc):
        errs.append(f'§0 каже «на межі» {m1.group(1)}, за §3 — {len(edge_calc)} — онови §0')
    s1 = next((x for x in sec if x.startswith('§1')), '')
    edge_doc = re.findall(r'^\| `(\w+)` \|', s1, re.M)
    for k in sorted(set(edge_calc) - set(edge_doc)):
        errs.append(f'§1 без {k}: вирок на межі повзунка')
    for k in sorted(set(edge_doc) - set(edge_calc)):
        errs.append(f'§1 зайвий {k}: вирок уже не на межі (чи ключа нема в §3)')
    return vals, kinds, errs


def load_values():
    """Для збірки: значення з джерела; помилка форми — зупинка, не тиха підміна."""
    vals, _, errs = parse(open(VALUES, encoding='utf-8').read())
    if errs:
        raise SystemExit('valuesLOCK ✗: ' + '; '.join(errs[:5]))
    return vals


def cmd_values(argv):
    check, inject = '--check' in argv, '--inject' in argv
    rel = os.path.relpath(VALUES, ROOT)
    if not os.path.exists(VALUES):
        print(f'  ✗ нема {rel}')
        print('НЕ ЗЛОВИВ — нема файла' if inject else '─── джерело чисел: помилок 1 ✗ ───')
        return 1
    text = open(VALUES, encoding='utf-8').read()
    if inject:   # дубль першого ключа + рядок-число, де значення — «1x»
        first = next(l for l in text.splitlines() if ROW.match(l))
        text += first + '\n| `zzInj` | 1x | 1 | число | — |  |\n'
    vals, kinds, errs = parse(text)
    if '--json' in argv:
        if errs:
            print('valuesLOCK ✗: ' + '; '.join(errs[:5]), file=sys.stderr)
            return 1
        print(json.dumps(vals, ensure_ascii=False, sort_keys=True))
        return 0
    print(f'джерело чисел · {rel}' + (' · --check' if check else '') + (' · --inject' if inject else ''))
    print(f'  ключів {len(vals)} · число {sum(1 for k in kinds.values() if k == "число")} · вибір {sum(1 for k in kinds.values() if k == "вибір")}')
    for e in errs[:20]:
        print('  ✗ ' + e)
    if inject:
        print('ЗЛОВИВ' if errs else 'НЕ ЗЛОВИВ — детектор без зубів')
        return 1 if errs else 0
    print(f'─── джерело чисел: помилок {len(errs)} ' + ('✓ ───' if not errs else '✗ ───'))
    return 1 if errs else 0


SRC = os.path.join(ROOT, 'src')
OUT = os.path.join(ROOT, 'docs', 'index.html')
MARK = re.compile(r'<!--@src ([\w./-]+)-->')
ESC = {'<': '\\u003c', '>': '\\u003e', '&': '\\u0026', '\u2028': '\\u2028', '\u2029': '\\u2029'}


def build_text(override=None):
    """Збирає один HTML; override {шлях: текст} — підміна джерела в пам'яті (--inject)."""
    override, errs, parts = override or {}, [], []
    read = lambda rel: override[rel] if rel in override else open(os.path.join(SRC, rel), encoding='utf-8').read()

    def one(m):
        rel = m.group(1)
        if rel not in override and not os.path.isfile(os.path.join(SRC, rel)):
            errs.append(f'мітка без файла: src/{rel}')
            return m.group(0)
        body = read(rel).rstrip('\n')
        parts.append((rel, len(body.encode('utf-8'))))
        tag = f'/* @src {rel} */' if rel.endswith(('.css', '.js')) else f'<!-- @src {rel} -->'
        return f'{tag}\n{body}'
    html = MARK.sub(one, read('shell.html'))
    vals = load_values()
    js = json.dumps(vals, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    js = ''.join(ESC.get(c, c) for c in js)
    parts.append(('values (JSON)', len(js.encode('utf-8'))))
    if html.count('<!--@values-->') != 1:
        errs.append(f'мітка <!--@values--> має бути рівно одна (є {html.count("<!--@values-->")})')
    html = html.replace('<!--@values-->', f'<script type="application/json" id="values">{js}</script>')
    return html, parts, errs


def cmd_build(argv):
    check, inject = '--check' in argv, '--inject' in argv
    over = {'js/main.js': open(os.path.join(SRC, 'js', 'main.js'), encoding='utf-8').read() + '\n// zzInj\n'} if inject else None
    html, parts, errs = build_text(over)
    rel = os.path.relpath(OUT, ROOT)
    print(f'збірка · src/ → {rel}' + (' · --check' if check else '') + (' · --inject' if inject else ''))
    if not check and not inject and not errs:
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        open(OUT, 'w', encoding='utf-8').write(html)
        print(f'  записано {rel}')
    elif not errs:
        if not os.path.exists(OUT):
            errs.append(f'нема {rel} — збери: build')
        elif open(OUT, encoding='utf-8').read() != html:
            errs.append(f'{rel} ≠ зібраному з src/ і valuesLOCK — правили зібране руками чи не перезібрали: build')
    print('  розмір: ' + ' · '.join(f'{n} {b}' for n, b in parts) + f' · усього {len(html.encode("utf-8"))} Б')
    for e in errs:
        print('  ✗ ' + e)
    if inject:
        print('ЗЛОВИВ' if errs else 'НЕ ЗЛОВИВ — детектор без зубів')
        return 1 if errs else 0
    print(f'─── збірка: помилок {len(errs)} ' + ('✓ ───' if not errs else '✗ ───'))
    return 1 if errs else 0


if __name__ == '__main__':
    a = sys.argv[1:]
    cmds = {'values': cmd_values, 'build': cmd_build}
    if not a or a[0] not in cmds:
        print(__doc__)
        sys.exit(2)
    sys.exit(cmds[a[0]](a[1:]))
