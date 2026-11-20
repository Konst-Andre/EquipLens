#!/usr/bin/env python3
# живе доки: стенд не портовано в білд (BUILD-1 Ф3 закрито) — далі → archive/
"""Інвентар стенда (BUILD-1 Ф0): кожна одиниця стенда → застосунок · harness · токени · мішане.

Лічить (стенд лише читає):
  CSS  — кожне правило (і всередині @media) за класами й id; самоперевірка: число «{» ≡ розібраним блокам;
  HTML — кожен статичний елемент з class/id (застосунок рендерить JS у #sbox, тож решта — стенд);
  JS   — кожна іменована функція / стрілка; категорія — з явної карти FN (причина — коментар групи),
         бо сканер тексту не бачить ні ролі функції, ні складених імен класів (практика PurgeCSS /
         filtercss: JS-вставлений DOM і конкатенацію тримають явним списком — тут FN і SAFE).
Категорії: A застосунок (їде в PWA) · H harness стенда (лишається) · T обчислення значень із S
(на порті → генерація токенів у збірці) · M мішане (на порті розрізати).
✗ (exit 1): непоміщене · застаріле в FN · складений клас без SAFE · розбір CSS не зійшовся.
ⓘ підсилення: класи el-* з CSS без згадки в JS/HTML — мертві кандидати (звірити очима, не ✗).

Запуск з кореня репо:  python3 tools/stand_inventory.py [стенд] [--list] [--inject]
  без стенда — живий (найбільший номер) · --inject — підкидає правило й функцію без категорії → «ЗЛОВИВ».

Режим --values (BUILD-1 Ф1, S37 20.11.2026) — третій стан чисел (StageBench §3 п.13): засів LOCK_SEED стенда
→ lens/EquipLens_head_valuesLOCK.md. З 20.11.2026 файл — ДЖЕРЕЛО чисел (рішення Konst), правиться вироком;
генератор лише засіває (файла нема), перезаписувати відмовляється. Форму файла судить `tools/build.py values --check`.
  --values           — засів: пише файл, лише коли його нема (засів · «на межі повзунка» · без лока з причиною)
  --values --check   — бік стенда: живий стенд ≡ заморожений (ім'я й md5 з шапки файла) → інакше ✗;
                       ключ засіву, якого нема у файлі, → ✗; новий вирок (файл ≠ засів) — ⓘ, не ✗;
                       класифікація «без лока» (UNLOCKED_*) — ✗ на новий / застарілий ключ;
                       з --inject — підкидає засіву зайвий ключ → «ЗЛОВИВ».
"""
import re, sys, glob, os

FN = {  # функція → категорія. Однойменні вкладені — ім'я#N за порядком у файлі
    # harness: локи й засів, панель, повзунки, детектори й паспорт, зум, лупа, мокап статус-бару
    'lockSeedAudit': 'H', 'lockLoad': 'H', 'lockSeed': 'H', 'lockMigrate': 'H', 'lockSave': 'H',
    'lockState': 'H', 'lockToggle': 'H', 'installLocks': 'H', 'markAllLocks': 'H', 'markLock': 'H',
    'conds': 'H', 'deadSet': 'H', 'paintDead': 'H', 'measure': 'H', 'syncAll': 'H', 'slider': 'H',
    'syncPicks': 'H', 'pick': 'H', 'preset': 'H', 'seg': 'H', 'frameW': 'H', 'frameH': 'H',
    'fitZoom': 'H', 'applyZoom': 'H', 'paintLoupe': 'H', 'one#3': 'H', 'setPanel': 'H',
    'holdOn': 'H', 'holdOff': 'H', 'cssPassport': 'H', 'cssCovered': 'H', 'cssGap': 'H',
    'panSwitch': 'H', 'fontProbe': 'H', 'w': 'H', 'aurProbe': 'H', 'paintAurMap': 'H',
    'z': 'H', 'statusbar': 'H',   # w — вкладена у fontProbe; z — у bindSwipe (масштаб зуму)
    # обчислення значень із S → генерація токенів у збірці (ARCH-1: токени — CSS custom properties)
    'applyVars': 'T', 'nvMix': 'T', 'aurLayers': 'T', 'hx': 'T', 'rh': 'T', 'mixHex': 'T',
    'hsl': 'T', 'hexA': 'T',
    # мішане: і застосунок, і стенд (render — ще й лічильники; setTheme — ще й панель; bindSwipe — зум)
    'render': 'M', 'setTheme': 'M', 'bindSwipe': 'M',
    # застосунок: розмітка, знаки, дані й фільтри, поповери, свайп
    'ico': 'A', 'sheetRect': 'A', 'markSvg': 'A', 'wordmark': 'A', 'appbar': 'A', 'btn': 'A',
    'flt': 'A', 'srt': 'A', 'baseRows': 'A', 'CITIES': 'A', 'visRows': 'A', 'fltOn': 'A',
    'cityFilterOn': 'A', 'chipCount': 'A', 'plural': 'A', 'ageCls': 'A', 'sortRows': 'A',
    'srchVisible': 'A', 'ctxhead': 'A', 'chipsRow': 'A', 'ctlRow': 'A', 'screenNone': 'A',
    'rec': 'A', 'listOf': 'A', 'screenEmpty': 'A', 'screenStub': 'A', 'screenBody': 'A',
    'nav': 'A', 'cell': 'A', 'fabHTML': 'A', 'sheetHTML': 'A', 'effTheme': 'A', 'closePop': 'A',
    'openPop': 'A', 'ensureThemePop': 'A', 'locItems': 'A', 'one#1': 'A', 'themeItems': 'A',
    'one#2': 'A', 'closeAllSwipe': 'A',
}
SAFE = {'el-wm'}                      # класи, які JS складає зі шматків (`el-wm${…}`)
CSS_ELEM_A = {'*', '*,*::before,*::after', 'svg', 'button', '::selection'}   # reset — потрібен і PWA
CSS_EXC_H = ('el-status',)            # el-префікс, але мокап статус-бару телефона (statusbar → H)
NAMES = {'A': 'застосунок', 'H': 'harness', 'T': 'токени', 'M': 'мішане'}
STEP = re.compile(r'(from|to|[\d.]+%)(\s*,\s*(from|to|[\d.]+%))*')


def load(path, inject):
    s = open(path, encoding='utf-8').read()
    if inject:
        s = s.replace('</style>', '.zz-inj{color:red}</style>', 1)
        s = s.replace('</script>', '\nfunction zzInj(){ return 1 }\n</script>', 1)
    css = re.sub(r'/\*.*?\*/', '', ''.join(re.findall(r'<style[^>]*>(.*?)</style>', s, re.S)), flags=re.S)
    js = ''.join(re.findall(r'<script[^>]*>(.*?)</script>', s, re.S))
    body = re.sub(r'<(style|script)[^>]*>.*?</\1>', '', s, flags=re.S)
    return css, js, body


def css_units(css):
    out, other = [], 0
    for sel in re.findall(r'([^{}]+)\{', css):
        sel = ' '.join(sel.split())
        if sel.startswith('@') or STEP.fullmatch(sel):
            other += 1
            continue
        cls = re.findall(r'\.([A-Za-z][\w-]*)', sel)
        ids = [i for i in re.findall(r'#([A-Za-z][\w-]*)', sel) if i != 'sbox']
        h = bool(ids) or any(c.startswith('bx-') or c.startswith(CSS_EXC_H) for c in cls)
        a = '#sbox' in sel or any(c == 'screenbox' or (c.startswith('el-') and not c.startswith(CSS_EXC_H)) for c in cls)
        if a and h:
            cat = 'M'
        elif h or a:
            cat = 'H' if h else 'A'
        elif sel in CSS_ELEM_A:
            cat = 'A'
        elif not cls:
            cat = 'H'        # голі елементи (body, html, details, summary…) — сторінка стенда
        else:
            cat = None       # клас без відомого префікса
        out.append((sel, cat))
    return out, other


def html_units(body):
    out = []
    for tag in re.findall(r'<[a-zA-Z][^>]*\b(?:class|id)="[^"]*"[^>]*>', body):
        m = re.search(r'class="([^"]*)"', tag)
        cls = m.group(1).split() if m else []
        m = re.search(r'\bid="([^"]*)"', tag)
        i = m.group(1) if m else ''
        if i == 'sbox' or 'screenbox' in cls:
            cat = 'A'        # корінь застосунку: сюди рендерить render()
        elif any(c.startswith('el-') for c in cls):
            cat = 'M'        # el-клас поза #sbox — розібрати
        else:
            cat = 'H'        # статична розмітка поза #sbox — панель і рамка стенда
        out.append((' '.join(tag.split())[:70], cat))
    return out


def js_units(js):
    seen, out = {}, []
    for m in re.finditer(r'(?m)^[ \t]*(?:async\s+)?function\s+(\w+)|^[ \t]*(?:const|let|var)\s+(\w+)\s*=\s*(?:\([^)]*\)|\w+)\s*=>', js):
        n = m.group(1) or m.group(2)
        seen[n] = seen.get(n, 0) + 1
        key = f'{n}#{seen[n]}' if (n + '#1') in FN else n
        out.append((key, FN.get(key)))
    return out


# S без LOCK_SEED → чому без лока. Заміряно логікою самого стенда (deadSet) у Chromium: 12 станів — світла й
# темна × таби ov / ph / eq × дані є / нема, засів запечено, 0 помилок JS (S37 20.11.2026). Новий ключ S без
# лока, не названий тут, → ✗ (як FN). Лише стан ‘дані є’ пропустив би hSize — урок: стан застосунку цілий.
UNLOCKED_LIVE = {'haAL': 'аура смуг світлої — жива у світлій на всіх табах, вироку нема (заводське стенда; темна `haAD` — у засіві)',
                 'wmFont': 'шрифт знака — живий в обох темах; Chillax — у задумі (DES-1 п.9, шрифт у репо з ліцензією)',
                 'hSize': 'герой порожнього екрана (дані = нема, таби Потреби · Обладнання) — живий в обох темах, вироку нема'}
UNLOCKED_H = {'thesis': 'пресет стенда (кнопка «теза» перезаписує групу важелів) — не значення продукту'}
UNLOCKED_DEAD = {  # мертві в усіх 4 станах за засівом — гілка не обрана
    'mat = plain (не well)': ['wb', 'wY', 'wB', 'wA', 'wMixL', 'dY', 'dB', 'dA', 'hA', 'wMixD'],
    'край аркуша pkEdge = none': ['edgeX', 'edgeY', 'edgeAL', 'edgeAD', 'edgeStop'],
    'рядок = картка (не аркуш / щілина)': ['shtAL', 'shtAD', 'slitW'],
    'знак = n5 (не n1–n3)': ['n1Holes', 'n1R', 'n2Lines', 'n2Stub', 'n3H', 'n3W'],
    'кнопки голови — скло-пігулка без фону (hgrp = glass, hbare = 1)': ['bfill'],
    'активний сегмент = tint (не well)': ['ctlOnDep'],
    'великого заголовка нема (comp = v4) — колапсу нема': ['scroll'],
}
VALUES_OUT = 'lens/EquipLens_head_valuesLOCK.md'


def js_obj(js, name):
    m = re.search(r'const ' + name + r' = \{(.*?)\n\};', js, re.S)
    if not m:
        return None
    b = re.sub(r'//[^\n]*', '', re.sub(r'/\*.*?\*/', '', m.group(1), flags=re.S))
    return dict(re.findall(r"(\w+)\s*:\s*('[^']*'|-?[\d.]+)", b))


def values_md(path, js, body, inject):
    """Згенерований текст valuesLOCK і помилки класифікації."""
    seed, S = js_obj(js, 'LOCK_SEED'), js_obj(js, 'S')
    if not seed or not S:
        return None, ['LOCK_SEED або S не розібрано']
    if inject:  # підкинутий дефект засіву: інше значення + зайвий ключ
        k0 = next(k for k, v in seed.items() if not v.startswith("'"))
        seed[k0] = str(float(seed[k0]) + 1)
        seed['zzInj'] = '1'
    rng = {}
    for m in re.finditer(r'<input type="range" id="(\w+)"([^>]*)>', body):
        a = dict(re.findall(r'(min|max|step)="([^"]*)"', m.group(2)))
        rng[m.group(1)] = (a.get('min'), a.get('max'), a.get('step'))
    errs = [f'засів без S: {k}' for k in sorted(set(seed) - set(S)) if k != 'zzInj']
    known = set(UNLOCKED_LIVE) | set(UNLOCKED_H) | {k for ks in UNLOCKED_DEAD.values() for k in ks}
    unl = set(S) - set(seed)
    errs += [f'без лока й без причини в UNLOCKED_*: {k}' for k in sorted(unl - known)]
    errs += [f'застаріле в UNLOCKED_*: {k} (має лок або нема в S)' for k in sorted(known - unl)]
    q = lambda v: v.strip("'")
    md5 = __import__('hashlib').md5(open(path, 'rb').read()).hexdigest()
    edge, rows = [], []
    for k in sorted(seed, key=str.lower):
        v, r = seed[k], rng.get(k)
        kind = 'вибір' if v.startswith("'") else 'число'
        on = ''
        if r and kind == 'число' and float(v) in (float(r[0]), float(r[1])):
            on = '⚠ межа'
            edge.append((k, q(v), r))
        rr = f'{r[0]}…{r[1]} · {r[2]}' if r else '—'
        rows.append(f'| `{k}` | {q(v)} | {q(S.get(k, "—"))} | {kind} | {rr} | {on} |')
    L = [f'# EquipLens · valuesLOCK — числа голови (третій стан, канон значень)', '',
         '> живе доки: живе застосунок EquipLens — це джерело чисел збірки (`tools/build.py`)',
         f'> **ДЖЕРЕЛО ЧИСЕЛ ПРОДУКТУ** (рішення Konst 20.11.2026). Засіяно зі стенда `{os.path.basename(path)}` (md5 `{md5}`, засів `LOCK_SEED`) — стенд заморожений. **Правка — лише вироком пристрою:** змінити значення в рядку §3 (і §1, якщо вирок зійшов з межі чи став на неї), у коміті — який вирок і де суджено. Генератор файл не перезаписує.',
         '> Форма — `python3 tools/build.py values --check` (✗ на рядок не за формою, дубль, не-число, розбіжність §0 і §1); бік стенда — `python3 tools/stand_inventory.py --values --check`; обидва — у `tools/env_check.sh`. Дім і правило: `lens/BUILD-1_brief.md` §4-б · три стани — StageBench §3 п.13.', '',
         '## §0 · Підсумок', '',
         f'- засів: **{len(seed)}** ключів · стан стенда `S`: {len(S)} · без лока: {len(unl)} (живих без вироку {len(UNLOCKED_LIVE)} · harness {len(UNLOCKED_H)} · мертвих гілок {len(unl) - len(UNLOCKED_LIVE) - len(UNLOCKED_H)})',
         f'- на межі повзунка: **{len(edge)}** — засів не перевірений на межі (З-61); вирок — device-раунд білда (`lens/DES-1_brief.md` п.7)', '',
         '## §1 · На межі повзунка', '', '| ключ | вирок | повзунок |', '|---|---|---|']
    L += [f'| `{k}` | {v} | {r[0]}…{r[1]} |' for k, v, r in edge]
    L += ['', '## §2 · Без лока — чому', '', '| ключ | заводське | чому |', '|---|---|---|']
    L += [f'| `{k}` | {q(S[k])} | **живий без вироку** — {t} |' for k, t in UNLOCKED_LIVE.items()]
    L += [f'| `{k}` | {q(S[k])} | harness — {t} |' for k, t in UNLOCKED_H.items()]
    L += [f'| {" · ".join(f"`{k}`" for k in ks)} | — | мертві за засівом: {g} |' for g, ks in UNLOCKED_DEAD.items()]
    L += ['', f'## §3 · Засів — {len(seed)}', '', '| ключ | вирок | заводське S | тип | повзунок min…max · крок | |', '|---|---|---|---|---|---|']
    return '\n'.join(L + rows) + '\n', errs


def values(path, js, body, check, inject):
    txt, errs = values_md(path, js, body, inject)
    print(f'valuesLOCK · бік стенда · {os.path.basename(path)}' + (' · --check' if check else '') + (' · --inject' if inject else ''))
    exists = os.path.exists(VALUES_OUT)
    if txt is not None and not check and not inject:
        if exists:
            errs.append(f'{VALUES_OUT} — джерело чисел (рішення Konst 20.11.2026): генератор не перезаписує; засів — лише коли файла нема')
        elif errs:
            print('  ✗ файл не записано — спершу класифікація')
        else:
            open(VALUES_OUT, 'w', encoding='utf-8').write(txt)
            print(f'  засіяно {VALUES_OUT}')
    elif txt is not None:
        if not exists:
            errs.append(f'нема {VALUES_OUT} — засій: --values')
        else:
            cur = open(VALUES_OUT, encoding='utf-8').read()
            m = re.search(r'Засіяно зі стенда `([^`]+)` \(md5 `(\w+)`', cur)
            md5 = __import__('hashlib').md5(open(path, 'rb').read()).hexdigest()
            if not m:
                errs.append('у шапці файла нема «Засіяно зі стенда `…` (md5 `…`)» — не звірити, чи стенд заморожений')
            elif (m.group(1), m.group(2)) != (os.path.basename(path), md5):
                errs.append(f'стенд не заморожений: живий {os.path.basename(path)} md5 {md5[:12]} ≠ засіяний {m.group(1)} {m.group(2)[:12]} (BUILD-1 (в))')
            sys.dont_write_bytecode = True
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from build import parse
            fv, _, _ = parse(cur)
            seed = js_obj(js, 'LOCK_SEED')
            if inject:
                seed['zzInj'] = '1'
            q = lambda v: v.strip("'")
            errs += [f'ключ засіву без рядка у файлі: {k}' for k in sorted(set(seed) - set(fv))]
            moved = sorted(k for k in set(seed) & set(fv) if str(fv[k]) != q(seed[k]) and
                           not (q(seed[k]).replace('.', '', 1).lstrip('-').isdigit() and float(fv[k]) == float(q(seed[k]))))
            extra = sorted(set(fv) - set(seed))
            print(f'  ⓘ нові вироки після засіву (файл ≠ засів стенда): {len(moved)}' + (': ' + ' '.join(moved) if moved else '')
                  + (f' · нових ключів {len(extra)}: ' + ' '.join(extra) if extra else ''))
    for e in errs[:20]:
        print('  ✗ ' + e)
    if inject:
        print('ЗЛОВИВ' if errs else 'НЕ ЗЛОВИВ — детектор без зубів')
        return 1 if errs else 0
    print(f'─── valuesLOCK · бік стенда: помилок {len(errs)} ' + ('✓ ───' if not errs else '✗ ───'))
    return 1 if errs else 0


def live_stand():
    here = os.path.dirname(os.path.abspath(__file__))
    return max(glob.glob(os.path.join(here, 'EquipLens_headbench_v*.html')),
               key=lambda p: [int(x) for x in re.findall(r'\d+', os.path.basename(p))])


def main(argv):
    inject, lst = '--inject' in argv, '--list' in argv
    args = [a for a in argv if not a.startswith('--')]
    path = args[0] if args else live_stand()
    if '--values' in argv:
        _, js, body = load(path, False)
        return values(path, js, body, '--check' in argv, inject)
    css, js, body = load(path, inject)
    cssu, other = css_units(css)
    units = {'CSS': cssu, 'HTML': html_units(body), 'JS': js_units(js)}
    errs = []
    if css.count('{') != len(cssu) + other:
        errs.append(f'розбір CSS не зійшовся: «{{» {css.count("{")} ≠ блоків {len(cssu) + other}')
    errs += [f'застаріле в FN: {k} (у стенді нема)' for k in sorted(set(FN) - {k for k, _ in units['JS']})]
    composed = set(re.findall(r'(el-[\w-]*?)\$\{', js)) | set(re.findall(r"['\"](el-[\w-]*)['\"]\s*\+", js))
    errs += [f'складений клас без SAFE: {c}…' for c in sorted(composed - SAFE)]
    print(f'інвентар стенда · {os.path.basename(path)}' + (' · --inject' if inject else ''))
    print('| що | ' + ' | '.join(NAMES[c] for c in 'AHTM') + ' | непоміщене | усього |')
    print('|---|---|---|---|---|---|---|')
    for k, us in units.items():
        n = {c: sum(1 for _, x in us if x == c) for c in 'AHTM'}
        u = [x for x, c in us if c is None]
        errs += [f'непоміщене {k}: {x}' for x in u]
        print(f'| {k} | ' + ' | '.join(str(n[c]) for c in 'AHTM') + f' | {len(u)} | {len(us)} |')
        if lst:
            for x, c in us:
                print(f'    {k} {c or "?"} {x}')
    for e in errs:
        print('  ✗ ' + e)
    used = set(re.findall(r'el-[\w-]+', js + body))
    dead = sorted({c for sel, _ in cssu for c in re.findall(r'\.(el-[\w-]+)', sel)
                   if c not in used and not any(c.startswith(p) for p in SAFE)})
    print(f'ⓘ el-класів у CSS без згадки в JS/HTML (мертві кандидати — звірити очима): {len(dead)}'
          + (': ' + ' '.join(dead) if dead and lst else ''))
    if inject:
        print('ЗЛОВИВ' if errs else 'НЕ ЗЛОВИВ — детектор без зубів')
        return 1 if errs else 0
    print(f'─── непоміщених і помилок: {len(errs)} ' + ('✓ ───' if not errs else '✗ ───'))
    return 1 if errs else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
