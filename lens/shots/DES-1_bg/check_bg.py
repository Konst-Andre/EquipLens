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
Запуск: python3 lens/shots/DES-1_bg/check_bg.py <тека> [--inject | --inject-glass] [--json <тека>/metrics.json]
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

def rim(d, theme, vid, inj=False):
    """v9 (Konst v8 на iPhone: кант «грубо… кричить», у темній «не виражено»): край картки (зовнішні 2 px) проти смуги 4–7 px усередині.
    loud — найбільша |ΔL| серед чотирьох сторін; tint — найбільший приріст кольоровості краю (кольоровий контур); vis — ΔL верху й ліва (блиск з джерела)."""
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
        res.append(dict(loud=max(abs(v[0]) for v in sd.values()), tint=max(v[1] for v in sd.values()), vis=max(sd['t'][0], sd['l'][0])))
    if not res: return None
    return {k: max(x[k] for x in res) for k in ('loud', 'tint', 'vis')}

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

def main():
    d = sys.argv[1]
    inject = '--inject' in sys.argv
    inj_glass = '--inject-glass' in sys.argv
    inj_rim = '--inject-rim' in sys.argv
    jout = sys.argv[sys.argv.index('--json') + 1] if '--json' in sys.argv else None
    M = {}
    bad = 0
    for theme in ('light', 'dark'):
        ids = sorted({f.split('_')[1].split('.')[0] for f in os.listdir(d) if f.startswith(theme + '_') and f.endswith('.json')},
                     key=lambda v: (v != 'now', v))
        res = {v: judge(d, theme, v, inject and theme == 'light' and v == ids[1]) for v in ids}
        base = res['now']
        gl = {v: glass(d, theme, v, inj_glass and theme == 'light' and v == ids[1]) for v in ids}
        rm = {v: rim(d, theme, v, inj_rim and v == ids[1]) for v in ids}
        M[theme] = {}
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
                if a['vis'] - b0['vis'] < VIS_T and (FIT_FX.get(theme, {}).get(v, True)): marks.append(f'✗ блиску канта не видно (ΔL {a["vis"]:.3f}, «зараз» {b0["vis"]:.3f})'); bad += 1
            rtxt = f'кант гучн {rm[v]["loud"]:.3f} колір {rm[v]["tint"]:+.3f} блиск {rm[v]["vis"]:+.3f}' if rm[v] else ''
            gtxt = ' '.join(f'{q.split("-")[-1]} {dl:+.3f}' for q, dl in gl[v].items())
            M[theme][v] = f'контраст {w["cr"]} (поріг {w["need"]}) · на сонці {r["sun"][0]:.2f} · ΔE від «Зараз» {de:.3f}' + (f' · блиск скла {gtxt}' if gtxt else '') + (f' · {rtxt}' if rtxt else '')
            print(f'  {v:4} [{rtxt}] блиск скла [{gtxt}] · контраст мін {w["cr"]:>5} (поріг {w["need"]}, «{w["t"]}») · SUN-1 тінь {r["sun"][0]:.2f} · сонце {r["glare"][0]:.2f}'
                  f' · жовтизна {r["yellow"]*100:.2f} % · ΔE від «зараз» {de:.4f} · (чіп/бейдж мін {r["chip"][0]:.2f} «{r["chip"][1]}»)  ' + ('  '.join(marks) if marks else '✓'))
        dist = lambda x, y: sum(math.dist(p, q) for p, q in zip(res[x]['labs'], res[y]['labs'])) / len(res[x]['labs'])
        near = [(min((dist(v, u), u) for u in ids if u != v), v) for v in ids if len(ids) > 2]
        close = sorted({tuple(sorted((v, u))) + (round(d, 4),) for (d, u), v in near if d < 0.008})
        print('  сусід (найближчий): ' + ' · '.join(f'{v}→{u} {d:.3f}' for (d, u), v in near) + ('' if not close else '   ⚠ майже одне: ' + ', '.join(f'{a}≈{b} ({d})' for a, b, d in close)))
    print(f'─── ПІДСУМОК: ✗ {bad} (зараз — база, її ✗ не рахуються) ───' + ('  [--inject]' if inject else '') + ('  [--inject-glass]' if inj_glass else '') + ('  [--inject-rim]' if inj_rim else ''))
    if jout:
        json.dump(M, open(jout, 'w', encoding='utf-8'), ensure_ascii=False); print('числа для «i»:', jout)
    if inject or inj_glass or inj_rim:
        print('ЗЛОВИВ' if bad else 'НЕ ЗЛОВИВ — у приладу нема зубів'); return 0 if bad else 1
    return 1 if bad else 0

if __name__ == '__main__':
    sys.exit(main())
