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
  python3 tools/brand.py --check --inject — підкидає в пам'яті: штрих гліфа, «any maskable», застарілу печатку → «ЗЛОВИВ»
Генерація — Chromium (Playwright) і Pillow; --check — stdlib + Chromium (лише для стенда).
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
        caught = sum(any(s in e for e in errs) for s in ('src/brand/icon-any.svg', 'any maskable', 'icon-512.png: печатка'))
        print('ЗЛОВИВ' if caught == 3 else f'НЕ ЗЛОВИВ — з трьох підкидань спіймано {caught}')
        return 1 if caught == 3 else 0
    print(f'─── знак: помилок {len(errs)} ' + ('✓ ───' if not errs else '✗ ───'))
    return 1 if errs else 0


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:1] == ['icons']:
        sys.exit(cmd_icons(a[1:]))
    if '--check' in a:
        sys.exit(cmd_check('--inject' in a))
    print(__doc__)
    sys.exit(2)
