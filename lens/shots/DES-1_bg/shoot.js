/* живе доки: примірка `DES-1` п.5+6 без вироку Konst (далі — рецепт примірки, SHOTS.md §5).
   Знімальник примірки фону: збирає сторінку (стенд v17_30 + fit_bg.js рядком перед </body>) і знімає екран таба 2 кожного варіанта обох тем.
   Запуск з кореня репо: NODE_PATH=$(npm root -g) node lens/shots/DES-1_bg/shoot.js <тека виводу> [--page-only]
   Вихід: <тека>/DES-1_bg.html (сторінка для прев'ю) · <тека>/<тема>_<варіант>.png (кадр екрана, 1:1).
   --engine both (v10, «так з підсиленням» Konst S40 21.11.2026): три проходи в підтеки — chromium/ і webkit/ (та сама ширина й DPR iPhone:
   розбіжність = вада рушія) · android/ (Chromium із профілем Pixel 7 — розкладка на ширині Android); у кожній — engine.json (проба CSS + рамки).
   Порівнює check_bg.py --engines <тека>. --engine webkit|chromium — один прохід у корінь теки. Зуб: --inject-engine зсуває острівець лише у WebKit.
   WebKit ставить гачок старту (lens-governance:tools/claude-code/webkit_ensure.sh); WebKit Linux ≠ Safari iOS — вирок iPhone (lens-governance:kernel/Lens_stagebench_manifest.md §8.18). */
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '../../..');
const out = path.resolve(process.argv[2] || '.');
const stand = fs.readFileSync(path.join(ROOT, 'tools/EquipLens_headbench_v17_30.html'), 'utf8');
const fit = fs.readFileSync(path.join(__dirname, 'fit_bg.js'), 'utf8');
const i = stand.lastIndexOf('</body>');
if (i < 0) throw new Error('стенд без </body>');
/* синтетичні дані й у ТЕКСТІ сторінки, не лише на екрані: прев'ю публічне (lens-governance:tools/PREVIEW.md §3 п.8) */
/* значення в ' або " (місто «Кам'янське» стоїть у подвійних лапках — перша редакція їх пропускала — 10 записів лишались як у стенді; дані стенда вигадані (Konst S40: «витоку не було»), перевірка — запобіжник) */
const Q = String.raw`(?:'[^']*'|"[^"]*")`;
const REC = new RegExp(String.raw`\{n:(${Q}),(\s*)a:(${Q}),(\s*)c:(${Q})`, 'g');
const real = new Set();
/* перевіряються назва й адреса — дані людей; місто — географія (у журналі змін стенда «Дніпро», «Полтава» — не запис), його лише міняємо */
for (const m of stand.slice(0, i).matchAll(REC)) for (const v of [m[1], m[3]]) { const t = v.slice(1, -1); if (t.length > 3) real.add(t); }
let k = 0;
const leak = process.argv.includes('--inject-leak');   // зуб: один запис лишається справжнім → перевірка нижче мусить упасти
const synth = stand.slice(0, i).replace(REC, (m, n, s1, a, s2) => { k++; if (leak && k === 1) return m; return `{n:'Аптека ${k}',${s1}a:'вул. Тестова, ${k*7-4}',${s2}c:'${k % 2 ? 'Місто А' : 'Місто Б'}'`; });
if (!k) throw new Error('дані стенда не знайдено — синтетична підміна не спрацювала');
/* числа машини в «i» (v8): out/metrics.json від check_bg.py --json — якщо є (другий прохід: знімок → суддя → сторінка) */
const mf = path.join(out, 'metrics.json');
const metrics = fs.existsSync(mf) ? fs.readFileSync(mf, 'utf8') : '{}';
const page = synth + '<script>\nwindow.FIT_M = ' + metrics + ';\n' + fit + '\n</script>\n' + stand.slice(i);
/* перевірка НЕЗАЛЕЖНА від заміни (звірка виходу з оригіналом, не тим самим шаблоном — hoop.dev / hackernoon «prove masking worked», 21.11.2026): кожне справжнє значення стенда шукається в готовій сторінці; знайдено — сторінку не записано */
const left = [...real].filter(v => page.includes(v));
if (left.length) { console.error(`✗ у сторінці лишились справжні дані (${left.length} з ${real.size}) — прев'ю публічне, сторінку не записано`); process.exit(1); }
console.log(`дані: справжніх значень у стенді ${real.size}, у сторінці 0 · записів замінено ${k}`);
fs.mkdirSync(out, {recursive: true});
const pagePath = path.join(out, 'DES-1_bg.html');
fs.writeFileSync(pagePath, page);
if (process.argv.includes('--page-only')) { console.log('сторінка:', pagePath); process.exit(0); }

const eArg = process.argv.includes('--engine') ? process.argv[process.argv.indexOf('--engine') + 1] : 'chromium';
const PASSES = eArg === 'both' ? [['chromium', 'iPhone 13', 'chromium'], ['webkit', 'iPhone 13', 'webkit'], ['chromium', 'Pixel 7', 'android']]
  : [[eArg, 'iPhone 13', '']];
(async () => {
  const pw = require('playwright'); let bad = 0;
  for (const [eng, dev, sub] of PASSES) { console.log(`── ${sub || eng} · ${dev} ──`); bad += await shoot(pw, eng, dev, path.join(out, sub)); }
  process.exit(bad ? 1 : 0);
})();

async function shoot(pw, eng, dev, out) {
  fs.mkdirSync(out, {recursive: true});
  const b = await pw[eng].launch();
  const d0 = pw.devices[dev];
  const ctx = await b.newContext({ ...d0, viewport: {width: d0.viewport.width, height: 1000}, deviceScaleFactor: 1 });   // висота — щоб кадр 812 цілий під панеллю кнопок; ширина — пристрою (iPhone 390 · Pixel 7 412)
  const p = await ctx.newPage();
  const errs = []; p.on('pageerror', e => errs.push(String(e)));
  await p.goto('file://' + pagePath); await p.waitForTimeout(800);
  await p.evaluate(() => document.getElementById('zOne').click()); await p.waitForTimeout(300);   // масштаб 1:1 — скло судиться лише на 1:1 (wsd 2.14)
  if (eng === 'webkit' && process.argv.includes('--inject-engine')) await p.addStyleTag({content: '#sbox .el-nav{translate:6px 0}'});   // зуб: CSS, що діє лише в одному рушії
  /* проба підтримки CSS рушієм: скло стенда — backdrop-filter; iOS 18 не застосовує -webkit-backdrop-filter зі змінною (bugs.webkit.org 289149) */
  const css = await p.evaluate(() => { const e = document.createElement('div'); document.body.appendChild(e); e.style.setProperty('--b', '4px');
    e.style.setProperty('-webkit-backdrop-filter', 'blur(var(--b))'); e.style.setProperty('backdrop-filter', 'blur(var(--b))');
    const cs = getComputedStyle(e), nv = getComputedStyle(document.querySelector('#sbox .el-nav'));
    const r = {backdrop: CSS.supports('backdrop-filter', 'blur(2px)'), webkitBackdrop: CSS.supports('-webkit-backdrop-filter', 'blur(2px)'),
      varBlur: cs.backdropFilter || cs.webkitBackdropFilter || '', nav: nv.backdropFilter || nv.webkitBackdropFilter || '', ua: navigator.userAgent};
    e.remove(); return r; });
  console.log('CSS:', JSON.stringify({...css, ua: undefined}));
  /* панель примірки не з'їдає екран телефона: ≤ 140 px (пропуск Konst S40 — пояснення абзацом займало верх екрана; тепер за «i»).
     Зуб: --inject-panel розкриває пояснення → ✗ мусить з'явитись. */
  if (process.argv.includes('--inject-panel')) await p.evaluate(() => { document.querySelector('#fit .fs').hidden = false; });
  const barH = await p.evaluate(() => document.getElementById('fit').offsetHeight);
  if (barH > 140) errs.push(`панель примірки ${barH} px > 140 — пояснення має жити за «i», не абзацом`);
  console.log('панель примірки:', barH, 'px (≤ 140)');
  const V = await p.evaluate(() => Object.fromEntries(Object.entries(FIT.V).map(([t, a]) => [t, a.map(v => v.id)])));
  const shots = [];
  for (const theme of ['light', 'dark']) for (const id of V[theme]) {
    await p.evaluate(([t, v]) => FIT.pick(t, v), [theme, id]); await p.waitForTimeout(250);
    const st = await p.evaluate(() => ({t: document.getElementById('fit').dataset.theme, v: document.getElementById('fit').dataset.v, sb: document.getElementById('sbox').dataset.theme}));
    if (st.t !== theme || st.v !== id || st.sb !== theme) errs.push(`стан не перемкнувся: ${theme}/${id} → ${JSON.stringify(st)}`);
    const f = path.join(out, `${theme}_${id}.png`);
    await p.locator('#sbox').screenshot({ path: f }); shots.push(f);
    /* для машини (check_bg.py): кадр без тексту + коробки й колір кожного тексту — за ознакою (елемент з власним текстовим вузлом), не за класом */
    const items = await p.evaluate(() => {
      /* коробка — сам текстовий вузол (Range), не елемент: рамка й заливка бейджа — не фон тексту.
         Видимість — elementFromPoint у центрі: текст під острівцем чи шапкою не судиться (його не видно). */
      const sb = document.getElementById('sbox'), R = sb.getBoundingClientRect(), res = [];
      const tw = document.createTreeWalker(sb, NodeFilter.SHOW_TEXT);
      for (let n; (n = tw.nextNode());) {
        if (!n.textContent.trim()) continue;
        const e = n.parentElement, cs = getComputedStyle(e);
        if (cs.visibility === 'hidden' || +cs.opacity === 0) continue;
        const rg = document.createRange(); rg.selectNodeContents(n);
        const r = rg.getBoundingClientRect();
        if (r.width < 2 || r.height < 2 || r.top < R.top || r.bottom > R.bottom) continue;
        const top = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
        if (!top || !(top === e || e.contains(top) || top.contains(e))) continue;
        /* чіп / бейдж — текст на власній заливці (елемент або батько ≤ 48 px заввишки з непрозорим фоном): судиться проти заливки, не фону екрана */
        const fill = el => { const c = getComputedStyle(el).backgroundColor.match(/[\d.]+/g) || []; return el.getBoundingClientRect().height <= 48 && (c.length > 3 ? +c[3] : c.length ? 1 : 0) >= 0.1; };
        const chip = fill(e) || (e.parentElement && fill(e.parentElement));
        res.push({chip, t: n.textContent.trim().slice(0, 24), x: r.left - R.left, y: r.top - R.top, w: r.width, h: r.height, color: cs.color, fs: parseFloat(cs.fontSize), fw: +cs.fontWeight || 400});
      }
      return res;
    });
    fs.writeFileSync(path.join(out, `${theme}_${id}.json`), JSON.stringify(items));
    /* рамки скла для судді «блиск на склі» (check_bg.py): острівець · «+» · капсула шапки — за класом стенда, перевірено за ознакою (backdrop-filter) S40 */
    const glass = await p.evaluate(() => { const R = document.getElementById('sbox').getBoundingClientRect();
      const g = ['.el-nav', '.el-fab', '.el-hgrp'].map(q => { const e = document.querySelector('#sbox ' + q); if (!e) return null; const r = e.getBoundingClientRect();
        return {q, x: r.left - R.left, y: r.top - R.top, w: r.width, h: r.height}; }).filter(Boolean);
      /* v9: перші 2 картки цілком у кадрі — для судді канта (гучність · колір · видимість блиску) */
      [...document.querySelectorAll('#sbox .el-list[data-row="card"] .el-item')].map(e => e.getBoundingClientRect()).filter(r => r.top > R.top + 80 && r.bottom < R.bottom - 120).slice(0, 2)
        .forEach((r, i) => g.push({q: 'card' + (i + 1), x: r.left - R.left, y: r.top - R.top, w: r.width, h: r.height, rim: true}));
      return g; });
    fs.writeFileSync(path.join(out, `${theme}_${id}_glass.json`), JSON.stringify(glass));
    await p.addStyleTag({content: '#sbox, #sbox *{color:transparent!important;-webkit-text-fill-color:transparent!important;text-shadow:none!important}', }).then(h => h.evaluate(n => n.id = 'notext'));
    await p.locator('#sbox').screenshot({ path: path.join(out, `${theme}_${id}_bg.png`) });
    await p.evaluate(() => document.getElementById('notext').remove());
  }
  const frames = {}; for (const theme of ['light', 'dark']) frames[theme] = JSON.parse(fs.readFileSync(path.join(out, `${theme}_${V[theme][0]}_glass.json`), 'utf8'));
  fs.writeFileSync(path.join(out, 'engine.json'), JSON.stringify({engine: eng, device: dev, width: d0.viewport.width, css, frames, errs}));
  console.log('кадрів:', shots.length, '· помилок сторінки:', errs.length); errs.forEach(e => console.log('✗', e));
  await b.close(); return errs.length;
}
