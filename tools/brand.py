#!/usr/bin/env python3
# живе доки: живе застосунок EquipLens зі своїм знаком-написом (BUILD-1 Ф2-2б і далі)
"""Знак-напис «EquipLens» контуром Chillax (вирок «А» Konst, S38). Іконки PWA з гліфа Н5 — прилад ядра
lens-governance:tools/claude-code/pwa_icon.py з конфігом tools/icon.json (ICON-1, Konst 20.11.2026: «100% … треба її в ядро»):
  python3 ../lens-governance/tools/claude-code/pwa_icon.py icons tools/icon.json [--sheet <тека>]   · --check tools/icon.json [--inject]

  python3 tools/brand.py wordmark [--zip <архів набору>] [--keep <тека>] — src/brand/wordmark.svg. Набір качається з Fontshare у
                                            тимчасову теку (у git і на сервер — ні: ITF FFL v2.0; логотип, зроблений шрифтом, — наш твір).
                                            Грані — як у стенді: СТАТИЧНІ 500/600/700 (стенд вантажить їх CSS Fontshare), вагу valuesLOCK
                                            обирає правило CSS Fonts 4 «font matching» (> 500 → важчі за зростанням, тож 800 → 700).
                                            Розстановка — HarfBuzz (рушій Chromium): кернінг, letter-spacing після КОЖНОГО знака, без
                                            необов'язкових лігатур (CSS Text: letter-spacing ≠ 0). Звірка тим самим ходом: SVG ⟂ текст Chillax у
                                            Chromium — позиція кожного знака (≤ 0.05 px) і пікселі ×4 (≤ 1 %); не зійшлось → SVG не записується;
                                            wordmark --inject — трекінг +0.1 px → мусить бути «ЗЛОВИВ»
  python3 tools/brand.py --check [--inject] — шапка wordmark.svg ≡ valuesLOCK (wSize · wTrack · ваги → грані; без мережі);
                                            --inject — трекінг +1 → «ЗЛОВИВ»
Генерація — Chromium (Playwright), Pillow, uharfbuzz, fontTools; --check — stdlib.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRAND = os.path.join(ROOT, 'src', 'brand')
WORDMARK = os.path.join(BRAND, 'wordmark.svg')
FONTSHARE = 'https://api.fontshare.com/v2/fonts/download/chillax'
FACES = {500: 'Chillax-Medium.ttf', 600: 'Chillax-Semibold.ttf', 700: 'Chillax-Bold.ttf'}   # ≡ CSS стенда: chillax@500,600,700
OFF = {'liga': False, 'clig': False, 'dlig': False, 'hlig': False}                          # letter-spacing ≠ 0 → без лігатур
WMHEAD = re.compile(r'знак: wSize=([\d.]+) · wTrack=(-?[\d.]+) · wEq=(\d+)→(\d+) · wLe=(\d+)→(\d+) · набір (\S+)')


def num(x):
    return ('%.3f' % x).rstrip('0').rstrip('.')


def values():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import build
    return build.load_values()


def match(w, avail):
    """CSS Fonts 4 «font matching», вага: 400–500 → спершу вгору до 500, далі вниз, далі вгору; < 400 → вниз, далі вгору;
    > 500 → вгору, далі вниз (WPT css-fonts/matching/font-weight-search-direction, 20.11.2026)."""
    a = sorted(avail)
    if w in a:
        return w
    up, dn = [x for x in a if x > w], [x for x in a if x < w][::-1]
    if 400 <= w <= 500:
        order = [x for x in up if x <= 500] + dn + [x for x in up if x > 500]
    elif w < 400:
        order = dn + up
    else:
        order = up + dn
    return order[0]


def shape_run(ttf, text, size, track, x0, base):
    """HarfBuzz → контури SVG (px): x кожного знака = сума (advance·s + track) — letter-spacing і після останнього."""
    import uharfbuzz as hb
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen
    face = hb.Face(hb.Blob(ttf))
    font = hb.Font(face)
    s = size / face.upem
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf, OFF)
    d, x, xs = [], x0, []
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        xs.append(x)
        pen = SVGPathPen(None, ntos=lambda v: ('%.2f' % v).rstrip('0').rstrip('.'))
        font.draw_glyph_with_pen(info.codepoint, TransformPen(pen, (s, 0, 0, -s, x + pos.x_offset * s, base - pos.y_offset * s)))
        d.append(pen.getCommands())
        x += pos.x_advance * s + track
    ext = font.get_font_extents('ltr')
    shape_run.xs = xs                                                # позиції знаків — для звірки з Chromium
    return ' '.join(c for c in d if c), x, ext.ascender * s, -ext.descender * s


def wordmark_svg(fonts, v, ver, skew=0.0):
    size, track = float(v['wSize']), float(v['wTrack']) / 10 + skew   # стенд: letter-spacing = wTrack/10 px; skew — лише --inject
    fa, fb = match(int(v['wEq']), FACES), match(int(v['wLe']), FACES)
    for want, got in ((v['wEq'], fa), (v['wLe'], fb)):
        if int(want) >= 600 and got < 600:
            raise SystemExit(f'вага {want} → грань {got}: Chromium домалював би синтетичний жирний — контур так не вміє')
    _, _, asc, desc = shape_run(fonts[fa], 'E', size, 0, 0, 0)
    da, xa, _, _ = shape_run(fonts[fa], 'Equip', size, track, 0, asc)
    xs = shape_run.xs
    db, xb, _, _ = shape_run(fonts[fb], 'Lens', size, track, xa, asc)
    xs = xs + shape_run.xs
    W, H = xb, asc + desc
    return ('<!-- живе доки: живе знак EquipLens · згенеровано tools/brand.py wordmark — руками не правити. Chillax (Indian Type Foundry, ITF FFL v2.0):\n'
            f'     знак: wSize={num(size)} · wTrack={num(float(v["wTrack"]))} · wEq={int(v["wEq"])}→{fa} · wLe={int(v["wLe"])}→{fb} · набір {ver}\n'
            f'     рядок: «Equip» 0…{num(xa)} · «Lens» {num(xa)}…{num(xb)} · базова лінія y={num(asc)} (px при wSize; letter-spacing і після останнього знака, як у Chromium);\n'
            '     кольори — класами .a / .b (токени теми, порт шапки Ф3); у стенді «Equip» — градієнт по коробці рядка «Equip» -->\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {num(W)} {num(H)}" width="{num(W)}" height="{num(H)}" role="img" aria-label="EquipLens">'
            f'<path class="a" fill="currentColor" d="{da}"/><path class="b" fill="currentColor" d="{db}"/></svg>\n'), (fa, fb, xa, xb, xs)


def chillax(argv):
    """Набір Chillax — у пам'ять (тимчасовий файл стирається з текою): {вага: байти TTF}, версія."""
    import io, tempfile, urllib.request, zipfile
    if '--zip' in argv:
        raw = open(argv[argv.index('--zip') + 1], 'rb').read()
    else:
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, 'chillax.zip')
            urllib.request.urlretrieve(FONTSHARE, p)
            raw = open(p, 'rb').read()
    z = zipfile.ZipFile(io.BytesIO(raw))
    names = z.namelist()
    pick = lambda f: next(n for n in names if n.endswith('/TTF/' + f) or n.endswith('/fonts/' + f))
    fonts = {w: z.read(pick(f)) for w, f in FACES.items()}
    if not any(n.upper().endswith('FFL.TXT') for n in names):
        raise SystemExit('у наборі нема FFL.txt — ліцензію не звірено, знак не робимо')
    from fontTools.ttLib import TTFont
    ver = TTFont(io.BytesIO(fonts[700]))['name'].getDebugName(5).split(';')[0].replace(' ', '_')
    return fonts, ver


def cmd_wordmark(argv):
    import base64, io
    fonts, ver = chillax(argv)
    v = values()
    inject = '--inject' in argv
    svg, (fa, fb, xa, xb, xs) = wordmark_svg(fonts, v, ver, 0.1 if inject else 0.0)   # --inject: трекінг +0.1 px → мусить впасти
    # звірка: той самий рядок текстом у Chromium з тими самими гранями ⟂ SVG, ×4 — габарит чорнила і пікселі
    from playwright.sync_api import sync_playwright
    from PIL import Image, ImageChops
    ff = ''.join(f"@font-face{{font-family:'Chillax';src:url(data:font/ttf;base64,{base64.b64encode(fonts[w]).decode()});font-weight:{w}}}" for w in FACES)
    txt = (f"<style>{ff}body{{margin:0;background:#fff}}.w{{font-family:'Chillax';font-size:{v['wSize']}px;letter-spacing:{float(v['wTrack'])/10}px;"
           f"white-space:nowrap;position:absolute;left:20px;top:20px;line-height:1;color:#000}}.a{{font-weight:{int(v['wEq'])}}}.b{{font-weight:{int(v['wLe'])}}}</style>"
           '<span class="w"><span class="a">Equip</span><span class="b">Lens</span></span>')
    pic = "<style>body{margin:0;background:#fff}svg{position:absolute;left:20px;top:20px;color:#000}</style>" + re.sub(r'^<!--.*?-->\n', '', svg, flags=re.S)
    shots = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        for h in (txt, pic):
            pg = b.new_page(viewport={'width': 260, 'height': 80}, device_scale_factor=4)
            pg.route('**/*', lambda r: r.abort())
            pg.set_content(h)
            pg.evaluate('async () => { await document.fonts.load("700 20px Chillax"); await document.fonts.load("600 20px Chillax"); await document.fonts.ready; }')
            if h is txt:                                             # позиції знаків, як їх поставив Chromium (Range — по одному знаку)
                cx = pg.evaluate('''() => { const o = [], x0 = document.querySelector('.w').getBoundingClientRect().left;
                  for (const sp of document.querySelectorAll('.w span')) { const t = sp.firstChild;
                    for (let i = 0; i < t.length; i++) { const R = document.createRange(); R.setStart(t, i); R.setEnd(t, i + 1);
                      o.push(R.getBoundingClientRect().left - x0); } } return o; }''')
            shots.append(Image.open(io.BytesIO(pg.screenshot())).convert('L'))
            pg.close()
        b.close()
    ink = [ImageChops.invert(i).point(lambda x: 255 if x > 40 else 0) for i in shots]
    bb = [i.getbbox() for i in ink]
    if None in bb:
        raise SystemExit('звірка: один із рендерів порожній — шрифт не доїхав у Chromium?')
    wh = [(x1 - x0, y1 - y0) for x0, y0, x1, y1 in bb]
    crop = [ImageChops.invert(s).crop(b) for s, b in zip(shots, bb)]
    w, h = min(wh[0][0], wh[1][0]), min(wh[0][1], wh[1][1])
    diff = ImageChops.difference(crop[0].crop((0, 0, w, h)), crop[1].crop((0, 0, w, h)))
    bad = sum(diff.histogram()[64:]) / (w * h)          # частка пікселів з різницею > 25 % (згладжування — нижче порога)
    dx = max(abs(a - b) for a, b in zip(xs, cx)) if len(xs) == len(cx) else 99
    print(f'знак · Chillax {ver} · wEq {v["wEq"]}→{fa} · wLe {v["wLe"]}→{fb} · ширина {num(xb)} px · «Lens» з {num(xa)} px' + (' · --inject' if inject else ''))
    print(f'  звірка з текстом у Chromium: знаків {len(xs)}/{len(cx)} · найбільший зсув позиції {dx:.3f} px · чорнило (×4) текст '
          f'{wh[0][0]/4:.2f}×{wh[0][1]/4:.2f} · SVG {wh[1][0]/4:.2f}×{wh[1][1]/4:.2f} px · пікселів з різницею > 25 %: {bad*100:.2f} %')
    if '--keep' in argv:
        d = argv[argv.index('--keep') + 1]
        os.makedirs(d, exist_ok=True)
        for n, im in (('wm_text.png', shots[0]), ('wm_svg.png', shots[1]), ('wm_diff.png', ImageChops.invert(diff))):
            im.save(os.path.join(d, n))
    # поріг: позиції — геометрія (LayoutUnit Chromium = 1/64 px); габарит чорнила НЕ судимо — растр тексту й фігури
    # згладжується по-різному (замір S38: ±0.5 px при позиціях ≡ до 0.017 px)
    if dx > 0.05 or bad > 0.01:
        print('  ✗ знак ≠ тексту в браузері (поріг: позиція знака ≤ 0.05 px, пікселі ≤ 1 %) — SVG не записано')
        if inject:
            print('ЗЛОВИВ')
        return 1
    if inject:
        print('НЕ ЗЛОВИВ — звірка знака без зубів')
        return 0
    os.makedirs(BRAND, exist_ok=True)
    open(WORDMARK, 'w', encoding='utf-8').write(svg)
    print(f'  записано src/brand/wordmark.svg · {len(svg.encode())} Б (файл шрифту — ні в git, ні на диску: лише пам\'ять процесу)')
    return 0


def cmd_check(inject):
    """Знак: шапка SVG ≡ valuesLOCK (зміна wSize / wTrack / ваг без перегенерації → ✗; набір не качаємо — env_check без мережі)."""
    errs = []
    v = values()
    if inject:
        v = dict(v, wTrack=float(v['wTrack']) + 1)                   # трекінг знака ≠ valuesLOCK
    if not os.path.exists(WORDMARK):
        errs.append('нема src/brand/wordmark.svg — python3 tools/brand.py wordmark')
    else:
        m = WMHEAD.search(open(WORDMARK, encoding='utf-8').read())
        if not m:
            errs.append('src/brand/wordmark.svg: нема шапки параметрів — перегенеруй: python3 tools/brand.py wordmark')
        else:
            got = (float(m.group(1)), float(m.group(2)), int(m.group(3)), int(m.group(4)), int(m.group(5)), int(m.group(6)))
            want = (float(v['wSize']), float(v['wTrack']), int(v['wEq']), match(int(v['wEq']), FACES), int(v['wLe']), match(int(v['wLe']), FACES))
            if got != want:
                errs.append(f'src/brand/wordmark.svg зроблено з {got} ≠ valuesLOCK {want} (wSize · wTrack · wEq→грань · wLe→грань) — python3 tools/brand.py wordmark')
    print('знак-напис · wordmark.svg ⟂ valuesLOCK' + (' · --inject' if inject else ''))
    for e in errs:
        print('  ✗ ' + e)
    if inject:
        ok = any('wordmark.svg зроблено з' in e for e in errs)
        print('ЗЛОВИВ' if ok else 'НЕ ЗЛОВИВ — трекінг знака ≠ valuesLOCK пройшов')
        return 1 if ok else 0
    print(f'─── знак: помилок {len(errs)} ' + ('✓ ───' if not errs else '✗ ───'))
    return 1 if errs else 0


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:1] == ['wordmark']:
        sys.exit(cmd_wordmark(a[1:]))
    if '--check' in a:
        sys.exit(cmd_check('--inject' in a))
    print(__doc__)
    sys.exit(2)
