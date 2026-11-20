#!/usr/bin/env python3
# живе доки: живе застосунок EquipLens зі своїм знаком (BUILD-1 Ф2-2б і далі)
"""Знак EquipLens: іконки PWA з гліфа Н5 і (наступним ходом) знак-контур «EquipLens» — один прилад (BUILD-1 Ф2-2б, S38).

Рецепт — lens-governance:kernel/cookbook/Lens_iOS_cookbook_1_platform.md A75 «іконка = рендер гліфа продукту»: гліф НЕ
перемальовується — береться той самий рядок d, що малює шапка, прямо з замороженого стенда tools/EquipLens_headbench_v17_30.html
(Chromium без мережі, `.el-brand .el-mk svg` — за ознакою, не за іменем; засів стенда ≡ valuesLOCK стереже
stand_inventory.py --values --check). Кольори — обчислені стендом для кожної теми (тацю малює градієнт --g1→--g2, решту --ink);
у SVG іконки вони літералами: у окремому файлі var(--g1) розв'язувати нема від чого.

  python3 tools/brand.py icons            — src/brand/mark.svg (гліф як у стенді) · src/brand/icon-any.svg · icon-mask.svg →
                                            PNG у src/icons/ (Chromium; RGB без альфи — iOS під альфу підкладає чорне, A75 п.1;
                                            у кожен PNG вшито печатку tEXt «equiplens-src» = sha256 його SVG) · аркуш порівняння
                                            фону (світла / темна) — у теку з аргументу --sheet <тека>, у git не йде
  python3 tools/brand.py --check          — SVG знову виходить зі стенда ≡ закоміченим · PNG: розмір, тип 2 (непрозорий),
                                            печатка ≡ SVG · маніфест: id "./", any і maskable окремо (не «any maskable»),
                                            розміри ≡ файлам, фон ≡ --canvas стенда · оболонка: посилання й meta (A1, A55)
  python3 tools/brand.py wordmark [--zip <архів набору>] — знак «EquipLens» контуром Chillax (вирок «А» Konst, S38) →
                                            src/brand/wordmark.svg. Набір качається з Fontshare у тимчасову теку (у git і на
                                            сервер — ні: ITF FFL v2.0; логотип, зроблений шрифтом, — наш твір). Грані — як у стенді:
                                            СТАТИЧНІ 500/600/700 (стенд вантажить їх CSS Fontshare), вагу valuesLOCK обирає правило
                                            CSS Fonts 4 «font matching» (> 500 → важчі за зростанням, тож 800 → 700). Розстановка —
                                            HarfBuzz (рушій Chromium): кернінг, letter-spacing після КОЖНОГО знака, без необов'язкових
                                            лігатур (CSS Text: letter-spacing ≠ 0). Звірка тим самим ходом: SVG ⟂ текст Chillax у
                                            Chromium — позиція кожного знака (≤ 0.05 px) і пікселі ×4 (≤ 1 %); не зійшлось → SVG не
                                            записується; wordmark --inject — трекінг +0.1 px → мусить бути «ЗЛОВИВ»
  python3 tools/brand.py --check --inject — підкидає в пам'яті: штрих гліфа, «any maskable», застарілу печатку, трекінг знака → «ЗЛОВИВ»
Генерація — Chromium (Playwright), Pillow, uharfbuzz, fontTools; --check — stdlib + Chromium (лише для стенда).
"""
import hashlib, json, os, re, struct, sys, zlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STAND = os.path.join(ROOT, 'tools', 'EquipLens_headbench_v17_30.html')
SRC = os.path.join(ROOT, 'src')
BRAND = os.path.join(SRC, 'brand')
MANIFEST = os.path.join(SRC, 'manifest.webmanifest')
SHELL = os.path.join(SRC, 'shell.html')
FRAC = {'any': 0.66, 'mask': 0.50}   # габарит гліфа до сторони — A75 п.3 (maskable: гарантована центральна зона 80 %)
ICONS = [  # файл · розмір · рендер
    ('apple-touch-icon.png', 180, 'any'), ('icon-192.png', 192, 'any'), ('icon-512.png', 512, 'any'),
    ('icon-192-mask.png', 192, 'mask'), ('icon-512-mask.png', 512, 'mask'), ('favicon-32.png', 32, 'any')]
SEAL = 'equiplens-src'
WORDMARK = os.path.join(BRAND, 'wordmark.svg')
FONTSHARE = 'https://api.fontshare.com/v2/fonts/download/chillax'
FACES = {500: 'Chillax-Medium.ttf', 600: 'Chillax-Semibold.ttf', 700: 'Chillax-Bold.ttf'}   # ≡ CSS стенда: chillax@500,600,700
OFF = {'liga': False, 'clig': False, 'dlig': False, 'hlig': False}                          # letter-spacing ≠ 0 → без лігатур
WMHEAD = re.compile(r'знак: wSize=([\d.]+) · wTrack=(-?[\d.]+) · wEq=(\d+)→(\d+) · wLe=(\d+)→(\d+) · набір (\S+)')
TOK = re.compile(r'\{\{v:([\w./-]+)\}\}')

PROBE = r"""(theme) => {
  themeMode = theme; render();
  const sb = document.getElementById('sbox'), svg = sb.querySelector('.el-brand .el-mk svg');
  if (!svg) return null;
  const rgb = v => { const t = document.createElement('i'); t.style.color = v; sb.appendChild(t);
    const c = getComputedStyle(t).color; t.remove(); return c; };
  const cs = getComputedStyle(sb), tray = svg.querySelector('.el-tray'), bb = svg.getBBox();
  const grad = svg.querySelector('linearGradient');
  return { inner: svg.innerHTML, viewBox: svg.getAttribute('viewBox'),
    sw: getComputedStyle(svg).strokeWidth, cap: getComputedStyle(svg).strokeLinecap, join: getComputedStyle(svg).strokeLinejoin,
    ink: getComputedStyle(svg.closest('.el-mk')).color, g1: rgb(cs.getPropertyValue('--g1')), g2: rgb(cs.getPropertyValue('--g2')),
    canvas: rgb(cs.getPropertyValue('--canvas')), trayPaint: tray ? tray.dataset.p : '',
    grad: grad ? ['x1','y1','x2','y2'].map(a => grad.getAttribute(a)) : null,
    bbox: [bb.x, bb.y, bb.width, bb.height] };
}"""


def probe():
    """Стенд у Chromium без мережі → гліф і кольори обох тем."""
    from playwright.sync_api import sync_playwright
    html = open(STAND, encoding='utf-8').read()
    out = {}
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, offline=True)
        ctx.route('**/*', lambda r: r.abort())
        pg = ctx.new_page()
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.set_content(html, wait_until='load')
        for t in ('light', 'dark'):
            out[t] = pg.evaluate(PROBE, t)
        b.close()
    if errs:
        raise SystemExit('стенд у Chromium дав помилки JS: ' + ' | '.join(errs[:3]))
    return out


def hexc(c):
    m = re.match(r'rgba?\((\d+), (\d+), (\d+)', c)
    if not m:
        raise SystemExit(f'колір не розібрано: {c}')
    return '#%02X%02X%02X' % tuple(int(x) for x in m.groups())


def num(x):
    return ('%.3f' % x).rstrip('0').rstrip('.')


def paths(pr):
    """Шляхи гліфа без <defs> (градієнт — свій, літералами)."""
    return re.sub(r'<defs>.*?</defs>', '', pr['inner'], flags=re.S)


def mark_svg(pr):
    """Гліф як у стенді (кольори — змінними теми, для порту шапки Ф3)."""
    sw = pr['sw'].replace('px', '')
    return ('<!-- живе доки: живе знак EquipLens · згенеровано tools/brand.py icons зі стенда v17_30 (гліф Н5); руками не правити -->\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{pr["viewBox"]}" fill="none" stroke="currentColor" '
            f'stroke-width="{sw}" stroke-linecap="{pr["cap"]}" stroke-linejoin="{pr["join"]}">{pr["inner"]}</svg>\n')


def icon_svg(pr, kind, theme):
    """Іконка: суцільний фон --canvas теми · гліф по центру, габарит FRAC[kind] сторони · кольори літералами."""
    sw = float(pr['sw'].replace('px', ''))
    x, y, w, h = pr['bbox']
    x, y, w, h = x - sw / 2, y - sw / 2, w + sw, h + sw          # габарит зі штрихом
    side = max(w, h) / FRAC[kind]
    vx, vy = x + w / 2 - side / 2, y + h / 2 - side / 2
    g = pr['grad'] or ['0', '0', '1', '1']
    body = paths(pr).replace('class="el-tray" data-p="grad"', 'stroke="url(#g)"')
    if pr['trayPaint'] == 'accent':
        body = body.replace('class="el-tray" data-p="accent"', f'stroke="{hexc(pr["g1"])}"')
    return (f'<!-- іконка «{kind}» · тема {theme} · згенеровано tools/brand.py icons зі стенда v17_30 (A75); руками не правити -->\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{num(vx)} {num(vy)} {num(side)} {num(side)}">'
            f'<rect x="{num(vx)}" y="{num(vy)}" width="{num(side)}" height="{num(side)}" fill="{hexc(pr["canvas"])}"/>'
            f'<defs><linearGradient id="g" x1="{g[0]}" y1="{g[1]}" x2="{g[2]}" y2="{g[3]}">'
            f'<stop stop-color="{hexc(pr["g1"])}"/><stop offset="1" stop-color="{hexc(pr["g2"])}"/></linearGradient></defs>'
            f'<g fill="none" stroke="{hexc(pr["ink"])}" stroke-width="{num(sw)}" stroke-linecap="{pr["cap"]}" '
            f'stroke-linejoin="{pr["join"]}">{body}</g></svg>\n')


def sources(pr):
    return {'mark.svg': mark_svg(pr['light']),
            'icon-any.svg': icon_svg(pr['light'], 'any', 'light'),
            'icon-mask.svg': icon_svg(pr['light'], 'mask', 'light')}


def sha(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]


def raster(svgs, sizes):
    """{(ім'я, розмір): svg} → {(ім'я, розмір): RGB Image} через Chromium (той самий рушій, що малює гліф на телефоні Android)."""
    from playwright.sync_api import sync_playwright
    from PIL import Image
    import io
    out = {}
    with sync_playwright() as p:
        b = p.chromium.launch()
        for (name, n), svg in svgs.items():
            pg = b.new_page(viewport={'width': n, 'height': n}, device_scale_factor=1)
            body = re.sub(r'^<!--.*?-->\n', '', svg).replace('<svg ', f'<svg width="{n}" height="{n}" ', 1)
            pg.set_content(f'<!doctype html><style>html,body{{margin:0}}svg{{display:block}}</style>{body}')
            out[(name, n)] = Image.open(io.BytesIO(pg.screenshot(clip={'x': 0, 'y': 0, 'width': n, 'height': n}))).convert('RGB')
            pg.close()
        b.close()
    return out


def cmd_icons(argv):
    from PIL import PngImagePlugin
    pr = probe()
    os.makedirs(BRAND, exist_ok=True)
    os.makedirs(os.path.join(SRC, 'icons'), exist_ok=True)
    src = sources(pr)
    for f, t in src.items():
        open(os.path.join(BRAND, f), 'w', encoding='utf-8').write(t)
    want = {(('icon-' + k + '.svg'), n): src['icon-' + k + '.svg'] for _, n, k in ICONS}
    imgs = raster(want, None)
    for f, n, k in ICONS:
        info = PngImagePlugin.PngInfo()
        info.add_text(SEAL, sha(src['icon-' + k + '.svg']))
        imgs[('icon-' + k + '.svg', n)].save(os.path.join(SRC, 'icons', f), pnginfo=info, optimize=True)
        print(f'  src/icons/{f} · {n}×{n} · {os.path.getsize(os.path.join(SRC, "icons", f))} Б')
    if '--sheet' in argv:
        d = argv[argv.index('--sheet') + 1]
        sheet(pr, d)
    print(f'записано src/brand/ ({", ".join(src)}) і {len(ICONS)} PNG · фон світлої {hexc(pr["light"]["canvas"])} · темної {hexc(pr["dark"]["canvas"])}')
    return 0


def sheet(pr, d):
    """Аркуш для вироку фону (A75 «фон — device-рішення»): обидві теми, 60 pt серед світлих і темних шпалер. У git — ні."""
    from PIL import Image, ImageDraw
    os.makedirs(d, exist_ok=True)
    svgs = {(f'{t}', 180): icon_svg(pr[t], 'any', t) for t in ('light', 'dark')}
    im = raster(svgs, None)
    W = Image.new('RGB', (2 * 3 * 200 + 40, 260), '#FFFFFF')
    dr = ImageDraw.Draw(W)
    walls = [('#F2F2F7', 'світлі'), ('#1C1C1E', 'темні'), ('#6B8FA8', 'фото')]
    for i, (c, _) in enumerate(walls):
        dr.rectangle([i * 400 + 10, 10, i * 400 + 400, 250], fill=c)
        for j, t in enumerate(('light', 'dark')):
            ico = im[(t, 180)]
            mask = Image.new('L', (180, 180), 0)
            ImageDraw.Draw(mask).rounded_rectangle([0, 0, 179, 179], radius=40, fill=255)   # лише показ маски iOS, у файлі — квадрат (A75 п.2)
            W.paste(ico, (i * 400 + 20 + j * 190, 40), mask)
    p = os.path.join(d, 'icon_compare.png')
    W.save(p)
    print(f'  аркуш порівняння: {p} (зліва в кожній парі — світла, справа — темна; шпалери: ' + ' · '.join(n for _, n in walls) + ')')


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


def png_meta(path):
    """IHDR (ширина, висота, тип кольору) і tEXt — stdlib, без декодування пікселів."""
    data = open(path, 'rb').read()
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        return None
    i, ihdr, text = 8, None, {}
    while i < len(data):
        ln, typ = struct.unpack('>I4s', data[i:i + 8])
        body = data[i + 8:i + 8 + ln]
        if typ == b'IHDR':
            ihdr = struct.unpack('>IIBB', body[:10])
        elif typ == b'tEXt':
            k, _, v = body.partition(b'\0')
            text[k.decode('latin-1')] = v.decode('latin-1')
        elif typ == b'zTXt':
            k, _, v = body.partition(b'\0')
            text[k.decode('latin-1')] = zlib.decompress(v[1:]).decode('latin-1')
        i += 12 + ln
    return {'w': ihdr[0], 'h': ihdr[1], 'ctype': ihdr[3], 'text': text}


def cmd_check(inject):
    errs = []
    try:
        pr = probe()
    except Exception as e:   # нема Chromium / Playwright — кажемо, не мовчимо
        print(f'  ✗ стенд не відкрито в Chromium: {e}')
        print('НЕ ЗЛОВИВ — нема Chromium' if inject else '─── знак: помилок 1 ✗ ───')
        return 1
    if inject:
        pr['light']['sw'] = '1.6px'                                   # (1) штрих гліфа ≠ стенду
    src = sources(pr)
    for f, t in src.items():
        p = os.path.join(BRAND, f)
        if not os.path.exists(p):
            errs.append(f'нема src/brand/{f} — python3 tools/brand.py icons')
        elif open(p, encoding='utf-8').read() != t:
            errs.append(f'src/brand/{f} ≠ гліфу стенда (стенд чи значення змінились, або правили руками) — python3 tools/brand.py icons')
    for f, n, k in ICONS:
        p = os.path.join(SRC, 'icons', f)
        m = png_meta(p) if os.path.exists(p) else None
        if not m:
            errs.append(f'нема або не PNG: src/icons/{f}')
            continue
        if (m['w'], m['h']) != (n, n):
            errs.append(f'src/icons/{f}: {m["w"]}×{m["h"]} ≠ {n}×{n}')
        if m['ctype'] != 2:
            errs.append(f'src/icons/{f}: тип кольору {m["ctype"]} ≠ 2 (RGB без альфи) — iOS підкладе чорне під прозоре (A75 п.1)')
        seal = sha(open(os.path.join(BRAND, 'icon-' + k + '.svg'), encoding='utf-8').read()) if os.path.exists(os.path.join(BRAND, 'icon-' + k + '.svg')) else '?'
        if inject and f == 'icon-512.png':
            seal = '0' * 16                                           # (3) застаріла печатка
        if m['text'].get(SEAL) != seal:
            errs.append(f'src/icons/{f}: печатка {m["text"].get(SEAL)} ≠ sha SVG {seal} — PNG застарів: python3 tools/brand.py icons')
    try:
        mt = open(MANIFEST, encoding='utf-8').read()
        if inject:
            mt = mt.replace('"purpose": "maskable"', '"purpose": "any maskable"', 1)   # (2)
        man = json.loads(TOK.sub(lambda m: m.group(1), mt))
    except (OSError, ValueError) as e:
        man = None
        errs.append(f'маніфест src/manifest.webmanifest не прочитано: {e}')
    if man is not None:
        for k, v in (('id', './'), ('start_url', './'), ('scope', './'), ('display', 'standalone')):
            if man.get(k) != v:
                errs.append(f'маніфест: {k} = {man.get(k)!r} ≠ {v!r}' + (' — без id зміна start_url = новий застосунок (A75 п.5)' if k == 'id' else ''))
        for k in ('name', 'short_name', 'lang'):
            if not man.get(k):
                errs.append(f'маніфест: нема {k}')
        bg = hexc(pr['light']['canvas'])
        for k in ('background_color', 'theme_color'):
            if str(man.get(k, '')).upper() != bg:
                errs.append(f'маніфест: {k} {man.get(k)} ≠ --canvas світлої стенда {bg}')
        purp = {}
        for ic in man.get('icons', []):
            pu = ic.get('purpose', 'any')
            if ' ' in pu.strip():
                errs.append(f'маніфест: purpose «{pu}» — any і maskable окремими рендерами (A75 п.3)')
            f = os.path.basename(ic.get('src', ''))
            spec = next((x for x in ICONS if x[0] == f), None)
            if not spec or not os.path.exists(os.path.join(SRC, ic.get('src', ''))):
                errs.append(f'маніфест: іконка {ic.get("src")} — нема файла в src/')
                continue
            if ic.get('sizes') != f'{spec[1]}x{spec[1]}' or (spec[2] == 'mask') != (pu == 'maskable'):
                errs.append(f'маніфест: {f} sizes/purpose ≠ файлу ({spec[1]}x{spec[1]} · {spec[2]})')
            purp.setdefault(pu, set()).add(spec[1])
        for pu in ('any', 'maskable'):
            if not {192, 512} <= purp.get(pu, set()):
                errs.append(f'маніфест: для purpose «{pu}» бракує 192 і 512')
    # знак: шапка SVG ≡ valuesLOCK (зміна wSize / wTrack / ваг без перегенерації → ✗; набір не качаємо — env_check без мережі)
    v = values()
    if inject:
        v = dict(v, wTrack=float(v['wTrack']) + 1)                   # (4) трекінг знака ≠ valuesLOCK
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
    sh = open(SHELL, encoding='utf-8').read()
    need = [('<link rel="manifest" href="{{v:manifest.webmanifest}}">', 'посилання на маніфест (окремий файл, A75 п.4)'),
            ('<link rel="apple-touch-icon" href="{{v:icons/apple-touch-icon.png}}">', 'apple-touch-icon (iOS бере з тегу, не з маніфесту)'),
            ('<link rel="icon" type="image/png" sizes="32x32" href="{{v:icons/favicon-32.png}}">', 'favicon'),
            ('viewport-fit=cover', 'viewport-fit=cover (без нього env(safe-area-*) = 0, A1)'),
            ('<meta name="apple-mobile-web-app-capable" content="yes">', 'apple-mobile-web-app-capable'),
            ('<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">', 'status-bar black-translucent'),
            (f'<meta name="theme-color" media="(prefers-color-scheme: light)" content="{hexc(pr["light"]["canvas"])}">', 'theme-color світлої ≡ --canvas стенда'),
            (f'<meta name="theme-color" media="(prefers-color-scheme: dark)" content="{hexc(pr["dark"]["canvas"])}">', 'theme-color темної ≡ --canvas стенда')]
    for s, why in need:
        if s not in sh:
            errs.append(f'оболонка src/shell.html: нема {why}')
    base = open(os.path.join(SRC, 'css', 'base.css'), encoding='utf-8').read()
    if 'min-height:calc(100% + env(safe-area-inset-top))' not in base:
        errs.append('base.css: нема html{min-height:calc(100% + env(safe-area-inset-top))} — гола смуга знизу в standalone (A55 (1))')
    print(f'знак · гліф {pr["light"]["trayPaint"] and "Н5"} · штрих {pr["light"]["sw"]} · PNG {len(ICONS)} · фон {hexc(pr["light"]["canvas"])} / {hexc(pr["dark"]["canvas"])}'
          + (' · --inject' if inject else ''))
    for e in errs:
        print('  ✗ ' + e)
    if inject:
        caught = sum(any(s in e for e in errs) for s in ('src/brand/icon-any.svg', 'any maskable', 'icon-512.png: печатка', 'wordmark.svg зроблено з'))
        print('ЗЛОВИВ' if caught == 4 else f'НЕ ЗЛОВИВ — з чотирьох підкидань спіймано {caught}')
        return 1 if caught == 4 else 0
    print(f'─── знак: помилок {len(errs)} ' + ('✓ ───' if not errs else '✗ ───'))
    return 1 if errs else 0


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:1] == ['wordmark']:
        sys.exit(cmd_wordmark(a[1:]))
    if a[:1] == ['icons']:
        sys.exit(cmd_icons(a[1:]))
    if '--check' in a:
        sys.exit(cmd_check('--inject' in a))
    print(__doc__)
    sys.exit(2)
