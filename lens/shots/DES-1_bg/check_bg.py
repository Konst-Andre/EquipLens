#!/usr/bin/env python3
# живе доки: примірка `DES-1` п.5+6 без вироку Konst; прилад `SUN-1` переїде в ядро рядком «Прилади продуктів», коли запрацює (lens/DES-1_brief.md §5 п.5+6).
"""Машина примірки фону: судить кадри знімальника shoot.js (тека з <тема>_<варіант>.png · _bg.png · .json).

Чотири судді на кожен варіант:
 1. КОНТРАСТ у найгіршій точці — кожен текст екрана (за ознакою: текстовий вузол, видимий зверху) проти пікселів фону під своєю
    коробкою (кадр без тексту); 5-й перцентиль WCAG 2.x (однопіксельний кант — не фон гліфа). Поріг: 4.5 дрібний, 3 великий (≥ 24 px або ≥ 18.66 px жирний).
    ✗ — лише коли варіант гірший за «зараз» тієї ж теми нижче порога (стан стенда — база; вироки контрасту стенда — окремий пункт К13-4).
 2. SUN-1 «сонячна проба» — той самий мінімум з відбитим світлом: ACR = (Y1 + 0.05 + A) / (Y2 + 0.05 + A)
    (контраст з відбиттям — патент US 12397623, «display ambient contrast ratio»: L_bright + E·R/π над L_dark + E·R/π).
    A = відбита яскравість відносно білого екрана: «тінь / хмари» 0.15 (10 тис. лк × відбиття 4.5 % / π ≈ 143 кд/м² при білому 1000 кд/м²;
    відбиття 4.5 % — не перевірено); «пряме сонце» 1.4 (100 тис. лк) — лише порівняння варіантів, порогу нема.
    Поріг «тінь»: 3.0 (ставка агента; джерела дисплеїв кажуть 5:1 для всього екрана — не для тексту на картці).
 3. ЖОВТИЗНА — частка пікселів фону з відтінком OKLCH 60–110° і C > 0.02 (слово Konst S39: «тепла читається як жовтизна»). ✗ > 1 %.
 4. РІЗНИЦЯ — середня відстань OKLab кадру без тексту від «зараз»: < 0.006 — варіант на телефоні не відрізнити (✗).
 5. СУСІД — відстань до найближчого іншого варіанта тієї ж теми: < 0.008 — два варіанти майже одне (⚠, не ✗: вибір звужує Konst; v6, Konst 21.11 «дай більше цікавого вибору»).
Зуби: --inject підкидає жовтий фон і блідий текст у перший варіант світлої → ✗ мусить з'явитись.
v8 — «блиск на склі» (розбір v7 п.6): ΔL OKLab між верхньою лівою смугою скла (острівець · «+» · капсула) і нижньою правою, кадр без тексту;
  варіант з «Відблиском» мусить світити сильніше за «зараз» (поріг GLASS_T). Зуб: --inject-glass вирівнює скло першого варіанта світлої → ✗.
  --json <файл> — короткий рядок чисел кожного варіанта для «i» панелі (shoot.js кладе їх у сторінку).
v10 — «деформація» світлої: нерівність краю картки вздовж верху (ALONG_T). Зуб: --inject-bend малює дугу, що гасне вздовж краю, у першому варіанті світлої → ✗.
Запуск: python3 lens/shots/DES-1_bg/check_bg.py <тека> [--inject | --inject-glass | --inject-rim | --inject-bend] [--json <тека>/metrics.json]
        python3 lens/shots/DES-1_bg/check_bg.py --engines <тека shoot.js --engine both> [--inject-engine]   (рушії: Chromium ⟂ WebKit + Android; ENGINE_T · FRAME_T)
"""
import json, math, sys, os, re
from PIL import Image

def lin(c):
    c = c / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def Y(rgb):
    r, g, b = (lin(v) for v in rgb[:3])
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def oklab(rgb):
    r, g, b = (lin(v) for v in rgb[:3])
    l = (0.4122214708*r + 0.5363325363*g + 0.0514459929*b) ** (1/3)
    m = (0.2119034982*r + 0.6806995451*g + 0.1073969566*b) ** (1/3)
    s = (0.0883024619*r + 0.2817188376*g + 0.6299787005*b) ** (1/3)
    return (0.2104542553*l + 0.7936177850*m - 0.0040720468*s, 1.9779984951*l - 2.4285922050*m + 0.4505937099*s,
            0.0259040371*l + 0.7827717662*m - 0.8086757660*s)

def cr(y1, y2, a=0.0):
    hi, lo = max(y1, y2), min(y1, y2)
    return (hi + 0.05 + a) / (lo + 0.05 + a)

def parse_color(s):
    # обчислений колір Chromium: rgb()/rgba() у 0–255 або color(srgb …) у частках 0–1 (так Chromium віддає змішане через color-mix);
    # інший формат — помилка, не мовчазне число (перша редакція читала color(srgb .61 …) як майже чорний — S40)
    n = [float(x) for x in re.findall(r'[\d.]+', s)]
    if s.startswith('rgb'):
        return (n[0], n[1], n[2], n[3] if len(n) > 3 else 1.0)
    if s.startswith('color(srgb'):
        return (n[0] * 255, n[1] * 255, n[2] * 255, n[3] if len(n) > 3 else 1.0)
    raise ValueError('невідомий формат кольору: ' + s)

FIT_FX = {}   # варіанти без «Відблиску» (мають право без блиску) — порожньо: «Відблиск» є в усіх, крім «зараз»
GLASS_T = 0.012   # ΔL OKLab: блиск на склі видно, коли верх-ліво світліше за низ-право на стільки більше, ніж у «зараз» (заміряно v8 S40 — див. REVIEW_v7.md п.6)

def glass(d, theme, vid, flat=False):
    """ΔL верхньої лівої смуги скла мінус нижньої правої для кожної рамки з <тема>_<варіант>_glass.json (кадр без тексту)."""
    f = os.path.join(d, f'{theme}_{vid}_glass.json')
    if not os.path.exists(f):
        return {}
    im = Image.open(os.path.join(d, f'{theme}_{vid}_bg.png')).convert('RGB'); px = im.load(); W, H = im.size
    out = {}
    for g in json.load(open(f, encoding='utf-8')):
        if g.get('rim'): continue
        x0, y0, w, h = int(g['x']) + 3, int(g['y']) + 3, int(g['w']) - 6, int(g['h']) - 6
        if w < 8 or h < 8 or x0 < 0 or y0 < 0 or x0 + w > W or y0 + h > H:
            continue
        mean = lambda xa, xb, ya, yb: sum(oklab(px[x, y])[0] for y in range(ya, yb) for x in range(xa, xb)) / max(1, (xb - xa) * (yb - ya))
        tl = mean(x0, x0 + w // 2, y0, y0 + max(2, h * 3 // 10))
        br = mean(x0 + w // 2, x0 + w, y0 + h * 6 // 10, y0 + h)
        out[g['q']] = 0.0 if flat else tl - br
    return out

def rim(d, theme, vid, inj=False, bend=False):
    """v9 (Konst v8 на iPhone: кант «грубо… кричить», у темній «не виражено»): край картки (зовнішні 2 px) проти смуги 4–7 px усередині.
    loud — найбільша |ΔL| серед чотирьох сторін; tint — найбільший приріст кольоровості краю (кольоровий контур); vis — ΔL верху й ліва (блиск з джерела);
    along — v10 «деформація»: ΔL краю у 8 сегментах верхньої сторони, max − min (блиск, що гасне вздовж краю, гне тіло — Konst v9 на iPhone;
    блиск під «не тим» кутом око читає як нахил — androidauthority.com/liquid-glass-vertigo-3598657, рецепт — рівний inset 0 1px 0, 21.11.2026).
    Межа: смужка з прозорими кінцями (симетрично гасне) теж дасть велике along — у v10 її нема."""
    f = os.path.join(d, f'{theme}_{vid}_glass.json')
    if not os.path.exists(f): return None
    im = Image.open(os.path.join(d, f'{theme}_{vid}_bg.png')).convert('RGB'); px = im.load(); W, H = im.size
    res = []
    for g in json.load(open(f, encoding='utf-8')):
        if not g.get('rim'): continue
        x0, y0, x1, y1 = int(round(g['x'])), int(round(g['y'])), int(round(g['x'] + g['w'])) - 1, int(round(g['y'] + g['h'])) - 1
        if x0 < 0 or y0 < 0 or x1 >= W or y1 >= H: continue
        if inj:   # зуб: грубий кольоровий контур 2 px
            for x in range(x0, x1 + 1):
                for y in (y0, y0 + 1, y1, y1 - 1): px[x, y] = (150, 90, 200)
            for y in range(y0, y1 + 1):
                for x in (x0, x0 + 1, x1, x1 - 1): px[x, y] = (150, 90, 200)
        if bend:   # зуб --inject-bend: дуга блиску, що гасне зліва направо вздовж верхнього краю (як v9 світлої)
            for x in range(x0, x1 + 1):
                a = 1 - 2 * (x - x0) / (x1 - x0)   # +1 зліва → −1 справа: світла дуга зліва, тихе темне ребро справа
                for y in (y0, y0 + 1):
                    c = px[x, y]; px[x, y] = tuple(int(v + (255 - v) * 0.9 * a) if a > 0 else int(v * (1 + 0.12 * a)) for v in c)
        r = 24   # кути не міряємо — радіус картки
        def band(side, a, b):
            pts = []
            if side == 't': pts = [(x, y0 + k) for x in range(x0 + r, x1 - r) for k in range(a, b)]
            if side == 'b': pts = [(x, y1 - k) for x in range(x0 + r, x1 - r) for k in range(a, b)]
            if side == 'l': pts = [(x0 + k, y) for y in range(y0 + r, y1 - r) for k in range(a, b)]
            if side == 'r': pts = [(x1 - k, y) for y in range(y0 + r, y1 - r) for k in range(a, b)]
            labs = [oklab(px[p]) for p in pts]
            return sum(l[0] for l in labs) / len(labs), sum(math.hypot(l[1], l[2]) for l in labs) / len(labs)
        sd = {}
        for side in 'tblr':
            (le, ce), (li, ci) = band(side, 0, 2), band(side, 4, 7)
            sd[side] = (le - li, ce - ci)
        xs = list(range(x0 + r, x1 - r)); n = len(xs) // 8
        seg = lambda a, b, s: sum(oklab(px[(x, y0 + k)])[0] for x in xs[s * n:(s + 1) * n] for k in range(a, b)) / (n * (b - a))
        tops = [seg(0, 2, s) - seg(4, 7, s) for s in range(8)]
        res.append(dict(loud=max(abs(v[0]) for v in sd.values()), tint=max(v[1] for v in sd.values()), vis=max(sd['t'][0], sd['l'][0]), along=max(tops) - min(tops)))
    if not res: return None
    return {k: max(x[k] for x in res) for k in ('loud', 'tint', 'vis', 'along')}

ALONG_T = 0.010   # v10 світла, «деформує тіло» (Konst v9 на iPhone): нерівність краю вздовж верху понад «зараз» ≤ ALONG_T. Калібровано 21.11.2026 (Chromium, 1:1):
                 # v9 світла .042–.066 (понад «зараз» .023 — від +.019) → ✗; v10 .005–.022 → ✓. Відкинуто: «ліво ⟂ право» (v9 .024 < стенд .049) і «верх ⟂ боки» (v9 +.030 ≈ v10 +.027) — ваду не бачать
LOUD_T, TINT_T, VIS_T = 0.045, 0.012, 0.015   # v9, понад «зараз»: гучність ≤ LOUD_T, кольоровість ≤ TINT_T, блиск ≥ VIS_T. Калібровано на v8 (Konst на iPhone): світла L3 колір +.014 → ✗ «кольоровий контур»; темна D7 блиск +.013 → ✗ «не видно» (REVIEW_v7.md п.12)

def judge(d, theme, vid, inject=False):
    bg = Image.open(os.path.join(d, f'{theme}_{vid}_bg.png')).convert('RGB')
    items = json.load(open(os.path.join(d, f'{theme}_{vid}.json'), encoding='utf-8'))
    W, H = bg.size
    if inject:
        bg = Image.blend(bg, Image.new('RGB', bg.size, (236, 222, 150)), 0.6)
        items = [dict(i, color='rgb(190, 190, 190)') for i in items]
    px = bg.load()
    worst, worst_sun, worst_glare, chip = (99, None), (99, None), (99, None), (99, None)
    for it in items:
        r, g, b, a = parse_color(it['color'])
        if a < 0.05:
            continue
        large = it['fs'] >= 24 or (it['fs'] >= 18.66 and it['fw'] >= 700)
        need = 3.0 if large else 4.5
        x0, y0 = max(0, int(it['x'])), max(0, int(it['y']))
        x1, y1 = min(W, int(it['x'] + it['w'])), min(H, int(it['y'] + it['h']))
        v0, v1, v2 = [], [], []
        for yy in range(y0, y1):
            for xx in range(x0, x1):
                p = px[xx, yy]
                # текст з альфою лягає на фон: колір тексту = змішане
                t = tuple(a * c + (1 - a) * q for c, q in zip((r, g, b), p))
                yt, yb = Y(t), Y(p)
                v0.append(cr(yt, yb)); v1.append(cr(yt, yb, 0.15)); v2.append(cr(yt, yb, 1.4))
        if not v0:
            continue
        # «найгірша точка» = 5-й перцентиль пікселів під текстом: однопіксельний кант картки, що перетинає коробку, — не фон гліфа
        # (перша редакція з абсолютним мінімумом дала хибні ✗ на «Місто Б» — кант під чіпом; S40)
        q = lambda v: sorted(v)[int(len(v) * 0.05)]
        lo, lo_s, lo_g = q(v0), q(v1), q(v2)
        if it.get('chip'):   # чіп / бейдж — на своїй заливці: окремий рядок, не ✗ фону (палітра бейджів — DES-1 п.13–15)
            if lo < chip[0]:
                chip = (lo, it['t'])
            continue
        if lo / need < worst[0]:
            worst = (lo / need, dict(t=it['t'], cr=round(lo, 2), need=need))
        if lo_s < worst_sun[0]:
            worst_sun = (lo_s, it['t'])
        if lo_g < worst_glare[0]:
            worst_glare = (lo_g, it['t'])
    # жовтизна й OKLab кадру без тексту (кожен 3-й піксель)
    yel = tot = 0
    labs = []
    for yy in range(0, H, 3):
        for xx in range(0, W, 3):
            L, A, B = oklab(px[xx, yy])
            C, h = math.hypot(A, B), (math.degrees(math.atan2(B, A)) + 360) % 360
            tot += 1
            yel += (60 <= h <= 110 and C > 0.02)
            labs.append((L, A, B))
    return dict(chip=chip, worst=worst, sun=worst_sun, glare=worst_glare, yellow=yel / tot, labs=labs)

DATA = {}   # числа останнього run(): {тема: {варіант: {cr, need, sun, glass, rim, marks}}} — для --engines

def run(d, inject=False, inj_glass=False, inj_rim=False, inj_bend=False, jout=None):
    M = {}; DATA.clear()
    bad = 0; hit = 0   # hit — ✗ саме підкинутого варіанта (ids[1]): наявне ✗ іншого варіанта (М'ята .031) не робить зуб «справжнім»
    for theme in ('light', 'dark'):
        ids = sorted({f.split('_')[1].split('.')[0] for f in os.listdir(d) if f.startswith(theme + '_') and f.endswith('.json')},
                     key=lambda v: (v != 'now', v))
        res = {v: judge(d, theme, v, inject and theme == 'light' and v == ids[1]) for v in ids}
        base = res['now']
        gl = {v: glass(d, theme, v, inj_glass and theme == 'light' and v == ids[1]) for v in ids}
        rm = {v: rim(d, theme, v, inj_rim and v == ids[1], inj_bend and theme == 'light' and v == ids[1]) for v in ids}
        M[theme] = {}; DATA[theme] = {}
        print(f'── {"світла" if theme == "light" else "темна"} ──')
        for v in ids:
            r = res[v]
            de = sum(math.dist(p, q) for p, q in zip(r['labs'], base['labs'])) / len(r['labs'])
            w = r['worst'][1]
            marks = []
            if r['worst'][0] < 1 and (v == 'now' or r['worst'][0] < base['worst'][0] - 0.02):
                marks.append(f'✗ контраст {w["cr"]} < {w["need"]} («{w["t"]}»)'); bad += v != 'now'
            if r['sun'][0] < 3.0 and (v == 'now' or r['sun'][0] < base['sun'][0] - 0.05):
                marks.append(f'✗ SUN-1 тінь {r["sun"][0]:.2f} < 3 («{r["sun"][1]}»)'); bad += v != 'now'
            if r['yellow'] > 0.01:
                marks.append(f'✗ жовтизна {r["yellow"]*100:.1f} %'); bad += 1
            if v != 'now' and de < 0.006:
                marks.append(f'✗ не відрізнити від «зараз» (ΔE {de:.4f})'); bad += 1
            if v != 'now' and gl[v]:
                for q, dl in gl[v].items():
                    n0 = gl['now'].get(q, 0)   # скло, що в «зараз» уже світить (ΔL ≥ 3·поріг, напр. «+» стенда .070), — лише не тьмяніти; неосвітлене — засвітитись
                    need = n0 - 0.005 if n0 >= 3 * GLASS_T else max(n0 + GLASS_T, GLASS_T)
                    if dl < need:
                        marks.append(f'✗ блиску на склі нема ({q} ΔL {dl:.3f} < {need:.3f})'); bad += 1
            if v != 'now' and rm[v] and rm['now']:
                a, b0 = rm[v], rm['now']
                if a['loud'] - b0['loud'] > LOUD_T: marks.append(f'✗ кант кричить (ΔL {a["loud"]:.3f}, «зараз» {b0["loud"]:.3f})'); bad += 1
                if a['tint'] - b0['tint'] > TINT_T: marks.append(f'✗ кольоровий контур (ΔC {a["tint"]:.3f}, «зараз» {b0["tint"]:.3f})'); bad += 1
                if theme == 'light' and a['along'] - b0['along'] > ALONG_T: marks.append(f'✗ кант деформує тіло (нерівний уздовж верху ΔL {a["along"]:.3f}, «зараз» {b0["along"]:.3f})'); bad += 1
                if theme == 'dark' and a['vis'] - b0['vis'] < VIS_T: marks.append(f'✗ блиску канта не видно (ΔL {a["vis"]:.3f}, «зараз» {b0["vis"]:.3f})'); bad += 1
            DATA[theme][v] = dict(cr=w['cr'], need=w['need'], sun=r['sun'][0], glass=gl[v] or {}, rim=rm[v] or {}, marks=marks)
            if v == ids[1] and marks and (inject or inj_glass or inj_bend and theme == 'light' or inj_rim): hit += 1
            rtxt = f'кант гучн {rm[v]["loud"]:.3f} колір {rm[v]["tint"]:+.3f} блиск {rm[v]["vis"]:+.3f} вздовж {rm[v]["along"]:.3f}' if rm[v] else ''
            gtxt = ' '.join(f'{q.split("-")[-1]} {dl:+.3f}' for q, dl in gl[v].items())
            M[theme][v] = f'контраст {w["cr"]} (поріг {w["need"]}) · на сонці {r["sun"][0]:.2f} · ΔE від «Зараз» {de:.3f}' + (f' · блиск скла {gtxt}' if gtxt else '') + (f' · {rtxt}' if rtxt else '')
            print(f'  {v:4} [{rtxt}] блиск скла [{gtxt}] · контраст мін {w["cr"]:>5} (поріг {w["need"]}, «{w["t"]}») · SUN-1 тінь {r["sun"][0]:.2f} · сонце {r["glare"][0]:.2f}'
                  f' · жовтизна {r["yellow"]*100:.2f} % · ΔE від «зараз» {de:.4f} · (чіп/бейдж мін {r["chip"][0]:.2f} «{r["chip"][1]}»)  ' + ('  '.join(marks) if marks else '✓'))
        dist = lambda x, y: sum(math.dist(p, q) for p, q in zip(res[x]['labs'], res[y]['labs'])) / len(res[x]['labs'])
        near = [(min((dist(v, u), u) for u in ids if u != v), v) for v in ids if len(ids) > 2]
        close = sorted({tuple(sorted((v, u))) + (round(d, 4),) for (d, u), v in near if d < 0.008})
        print('  сусід (найближчий): ' + ' · '.join(f'{v}→{u} {d:.3f}' for (d, u), v in near) + ('' if not close else '   ⚠ майже одне: ' + ', '.join(f'{a}≈{b} ({d})' for a, b, d in close)))
    print(f'─── ПІДСУМОК: ✗ {bad} (зараз — база, її ✗ не рахуються) ───' + ('  [--inject]' if inject else '') + ('  [--inject-glass]' if inj_glass else '') + ('  [--inject-rim]' if inj_rim else '') + ('  [--inject-bend]' if inj_bend else ''))
    if jout:
        json.dump(M, open(jout, 'w', encoding='utf-8'), ensure_ascii=False); print('числа для «i»:', jout)
    if inject or inj_glass or inj_rim or inj_bend:
        print('ЗЛОВИВ' if hit else 'НЕ ЗЛОВИВ — у приладу нема зубів (✗ підкинутого варіанта нема)'); return 0 if hit else 1
    return 1 if bad else 0

ENGINE_T = {'glass': 0.020, 'rim': 0.028, 'cr': 0.48, 'sun': 0.10}   # розбіжність Chromium ⟂ WebKit на тій самій ширині й DPR iPhone — понад це ✗ «вада рушія».
# Поріг = max |Δ| першого прогону ×1.5 (v10, 21.11.2026, Playwright 1.63: Chromium ⟂ WebKit 26.6, 1:1): glass .013 · rim .019 · cr .32 · sun .067 —
# системна різниця відтворення blur/saturate у темній (WebKit контрастніший), не CSS одного рушія; переглянути з новим рушієм. Ловить нове поверх цього шуму.
FRAME_T = 1.0   # рамки ключових елементів (острівець · «+» · капсула · картки), px

def engines(d):
    """--engines <тека shoot.js --engine both>: судді на кожному проході + Chromium ⟂ WebKit (міри, рамки, вирок) + Android (судді, рамки).
    Вирок, що різниться між рушіями, а значення в межах ENGINE_T від порога, — ⚠ «на межі рушія», не ✗ (поріг лежить у шумі рушія)."""
    import contextlib, io
    R, E = {}, {}
    for sub in ('chromium', 'webkit', 'android'):
        with contextlib.redirect_stdout(io.StringIO()): code = run(os.path.join(d, sub))
        R[sub] = json.loads(json.dumps(DATA)); E[sub] = json.load(open(os.path.join(d, sub, 'engine.json'), encoding='utf-8'))
        print(f'{sub:8} {E[sub]["device"]:9} ширина {E[sub]["width"]} · судді: ' + ('✓' if not code else f'є ✗ (python3 {sys.argv[0]} {os.path.join(d, sub)})')
              + f' · CSS backdrop {E[sub]["css"]["backdrop"]} -webkit- {E[sub]["css"]["webkitBackdrop"]} змінна «{E[sub]["css"]["varBlur"]}» острівець «{E[sub]["css"]["nav"]}»')
    bad, warn, mx = 0, 0, {k: 0.0 for k in ENGINE_T}
    c, w = R['chromium'], R['webkit']
    for theme in c:
        for v in c[theme]:
            a, b = c[theme][v], w[theme].get(v)
            if not b: print(f'  ✗ {theme}/{v}: у WebKit нема варіанта'); bad += 1; continue
            diffs = [('cr', a['cr'], b['cr']), ('sun', a['sun'], b['sun'])] + [('glass', a['glass'][q], b['glass'].get(q, 0)) for q in a['glass']] \
                    + [('rim', a['rim'][k], b['rim'].get(k, 0)) for k in a['rim']]
            for k, x, y in diffs:
                mx[k] = max(mx[k], abs(x - y))
                if abs(x - y) > ENGINE_T[k]: print(f'  ✗ вада рушія {theme}/{v} {k}: Chromium {x:.3f} ⟂ WebKit {y:.3f} (Δ {abs(x - y):.3f} > {ENGINE_T[k]})'); bad += 1
            if bool(a['marks']) != bool(b['marks']):
                print(f'  ⚠ на межі рушія {theme}/{v}: ' + ('Chromium ' + '; '.join(a['marks']) if a['marks'] else 'WebKit ' + '; '.join(b['marks'])) + ' — міри в межах ENGINE_T, вирок за порогом різниться → вирішує iPhone'); warn += 1
    print('  Chromium ⟂ WebKit max |Δ|: ' + ' · '.join(f'{k} {v:.3f} (поріг {ENGINE_T[k]})' for k, v in mx.items()))
    for theme in ('light', 'dark'):
        fc = {g['q']: g for g in E['chromium']['frames'][theme]}
        for g in E['webkit']['frames'][theme]:
            f = fc.get(g['q'])
            dd = max(abs(f[k] - g[k]) for k in ('x', 'y', 'w', 'h')) if f else 99
            if dd > FRAME_T: print(f'  ✗ рамка {theme} {g["q"]}: Chromium ⟂ WebKit Δ {dd:.1f} px > {FRAME_T}'); bad += 1
        an = {g['q']: g for g in E['android']['frames'][theme]}; W0, W1 = E['chromium']['width'], E['android']['width']
        lay = ' · '.join(f'{q} {an[q]["w"]:.0f}×{an[q]["h"]:.0f}' for q in ('.el-nav', '.el-fab', 'card1') if q in an)
        same = all(abs(an[q][k] - fc[q][k]) <= FRAME_T for q in an if q in fc for k in ('x', 'w'))
        # стенд малює екран фіксованої ширини (рамка #sbox, 375 px) — розкладку на ширині Android побачить білд PWA (BUILD-1), не стенд (заміряно 21.11.2026)
        print(f'  Android {theme} (вікно {W1} px ⟂ iPhone {W0}): {lay}' + (' — екран стенда фіксованої ширини, розкладка ≡ iPhone; ширину Android судить білд' if same else ' — розкладка інша, ніж на iPhone: перевір'))
    nA = sum(bool(x['marks']) for t_ in R['android'].values() for v, x in t_.items() if v != 'now')
    if nA: print(f'  ✗ Android: судді дали ✗ — {nA} варіант(ів)'); bad += nA
    print(f'─── РУШІЇ: ✗ {bad} · ⚠ на межі рушія {warn} ───')
    return 1 if bad else 0

def main():
    if '--engines' in sys.argv:
        r = engines(sys.argv[sys.argv.index('--engines') + 1])
        if '--inject-engine' in sys.argv: print('ЗЛОВИВ' if r else 'НЕ ЗЛОВИВ — розбіжність рушія не видно'); return 0 if r else 1
        return r
    a = sys.argv
    return run(a[1], '--inject' in a, '--inject-glass' in a, '--inject-rim' in a, '--inject-bend' in a, a[a.index('--json') + 1] if '--json' in a else None)

if __name__ == '__main__':
    sys.exit(main())
