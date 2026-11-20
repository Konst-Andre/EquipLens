#!/usr/bin/env python3
# живе доки: застосунок EquipLens вшиває свій шрифт тексту (BUILD-1 Ф2-2а)
"""Шрифт тексту EquipLens — Manrope (OFL 1.1, без Reserved Font Name), вшитий у білд (BUILD-1 Ф2-2а, S38).

Джерело — sources/fonts/Manrope[wght].ttf (google/fonts:ofl/manrope, змінна вісь wght 200–800; стенд вживає
500…800, серед них 650 і 750 — статичні накреслення їх не дадуть). Генератор ріже підмножину (латиниця +
кирилиця з ґ/є/і/ї + пунктуація + № ₴) → src/fonts/manrope.woff2; збірка (tools/build.py, мітка
/*@font fonts/manrope.woff2*/) вшиває його base64-ом — SW кешує один файл (рішення Konst, lens/BACK-1_brief.md §3).
Chillax (ITF FFL v2.0) сюди НЕ йде: підмножина й файл у публічному репо заборонені — знак малюється контуром (вирок «А», S38).

  python3 tools/fonts.py build            — підмножина → src/fonts/manrope.woff2 (потрібні fonttools + brotli)
  python3 tools/fonts.py --check          — woff2: вісь wght 200–800 · версія ≡ джерелу · розмір ≤ бюджету ·
                                            кожен символ обов'язкового набору І кожен символ тексту src/ (без коментарів) — у шрифті
  python3 tools/fonts.py --check --inject — підкидає в текст src/ символ поза шрифтом (U+4E00) → «ЗЛОВИВ»
Пошук символів — за ознакою (усі текстові файли src/), не за переліком імен.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_TTF = os.path.join(ROOT, 'sources', 'fonts', 'Manrope[wght].ttf')
OUT = os.path.join(ROOT, 'src', 'fonts', 'manrope.woff2')
SRC = os.path.join(ROOT, 'src')
UNICODES = ('U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0400-045F,U+0490-0491,'
            'U+04B0-04B1,U+2000-206F,U+20B4,U+2116,U+2122,U+2212,U+2215')
REQUIRED = ('АБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯабвгґдеєжзиіїйклмнопрстуфхцчшщьюя'
            'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
            '.,:;!?()[]%+-=/«»—–…№₴’·×')
# ʼ U+02BC (апостроф-літера) у Manrope 4.505 нема навіть у повному файлі (замір S38) → тексти інтерфейсу пишуть ’ U+2019, як стенд
BUDGET = 40_000   # Б woff2; замір S38 — 32 436 Б, запас ≈ 23 % на нові символи
COMMENTS = re.compile(r'/\*.*?\*/|<!--.*?-->|(?:^|\s)//[^\n]*', re.S | re.M)


def src_text():
    """Текст усіх файлів src/ без коментарів (символи коментарів не малюються — не судимо)."""
    out = []
    for d, _, fs in os.walk(SRC):
        for f in sorted(fs):
            if f.endswith(('.html', '.css', '.js', '.json', '.txt')) and 'fonts' not in os.path.relpath(d, SRC).split(os.sep):
                out.append(COMMENTS.sub(' ', open(os.path.join(d, f), encoding='utf-8').read()))
    return '\n'.join(out)


def cmd_build():
    from fontTools import subset
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    subset.main([SRC_TTF, f'--unicodes={UNICODES}', '--layout-features=*', '--flavor=woff2', f'--output-file={OUT}'])
    print(f'записано {os.path.relpath(OUT, ROOT)} · {os.path.getsize(OUT)} Б')
    return 0


def cmd_check(inject):
    errs = []
    try:
        from fontTools.ttLib import TTFont
    except ImportError:
        print('  ✗ fonttools нема — pip install fonttools brotli (хук старту .claude/hooks/session-start.sh)')
        print('НЕ ЗЛОВИВ — нема fonttools' if inject else '─── шрифт: помилок 1 ✗ ───')
        return 1
    if not os.path.exists(OUT):
        errs.append(f'нема {os.path.relpath(OUT, ROOT)} — збери: python3 tools/fonts.py build')
    else:
        f, s = TTFont(OUT), TTFont(SRC_TTF)
        cmap = set(f.getBestCmap())
        ax = {a.axisTag: (a.minValue, a.maxValue) for a in f['fvar'].axes} if 'fvar' in f else {}
        if ax.get('wght') != (200.0, 800.0):
            errs.append(f'вісь wght {ax.get("wght")} ≠ (200, 800) — ваги стенда 650/750 не дадуть')
        if f['name'].getDebugName(5) != s['name'].getDebugName(5):
            errs.append(f'версія woff2 «{f["name"].getDebugName(5)}» ≠ джерелу «{s["name"].getDebugName(5)}» — перезбери: build')
        size = os.path.getsize(OUT)
        if size > BUDGET:
            errs.append(f'розмір {size} Б > бюджету {BUDGET} Б')
        text = src_text() + ('一' if inject else '')
        need = set(REQUIRED) | {c for c in text if ord(c) >= 0x20 and not c.isspace()}
        miss = sorted(c for c in need if ord(c) not in cmap)
        if miss:
            errs.append('символи поза шрифтом: ' + ' '.join(f'{c} U+{ord(c):04X}' for c in miss[:12]))
        print(f'шрифт · {os.path.relpath(OUT, ROOT)} · {size} Б · гліфів у cmap {len(cmap)} · символів тексту src/ {len(need)}'
              + (' · --inject' if inject else ''))
    for e in errs:
        print('  ✗ ' + e)
    if inject:
        print('ЗЛОВИВ' if errs else 'НЕ ЗЛОВИВ — детектор без зубів')
        return 1 if errs else 0
    print(f'─── шрифт: помилок {len(errs)} ' + ('✓ ───' if not errs else '✗ ───'))
    return 1 if errs else 0


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:1] == ['build']:
        sys.exit(cmd_build())
    if '--check' in a:
        sys.exit(cmd_check('--inject' in a))
    print(__doc__)
    sys.exit(2)
