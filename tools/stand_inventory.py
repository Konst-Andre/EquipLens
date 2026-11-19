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


def live_stand():
    here = os.path.dirname(os.path.abspath(__file__))
    return max(glob.glob(os.path.join(here, 'EquipLens_headbench_v*.html')),
               key=lambda p: [int(x) for x in re.findall(r'\d+', os.path.basename(p))])


def main(argv):
    inject, lst = '--inject' in argv, '--list' in argv
    args = [a for a in argv if not a.startswith('--')]
    path = args[0] if args else live_stand()
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
