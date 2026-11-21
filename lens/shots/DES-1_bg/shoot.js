/* живе доки: примірка `DES-1` п.5+6 без вироку Konst (далі — рецепт примірки, SHOTS.md §5).
   Знімальник примірки фону: збирає сторінку (стенд v17_30 + fit_bg.js рядком перед </body>) і знімає екран таба 2 кожного варіанта обох тем.
   Запуск з кореня репо: NODE_PATH=$(npm root -g) node lens/shots/DES-1_bg/shoot.js <тека виводу> [--page-only]
   Вихід: <тека>/DES-1_bg.html (сторінка для прев'ю) · <тека>/<тема>_<варіант>.png (кадр екрана, 1:1). */
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
const page = synth + '<script>\n' + fit + '\n</script>\n' + stand.slice(i);
/* перевірка НЕЗАЛЕЖНА від заміни (звірка виходу з оригіналом, не тим самим шаблоном — hoop.dev / hackernoon «prove masking worked», 21.11.2026): кожне справжнє значення стенда шукається в готовій сторінці; знайдено — сторінку не записано */
const left = [...real].filter(v => page.includes(v));
if (left.length) { console.error(`✗ у сторінці лишились справжні дані (${left.length} з ${real.size}) — прев'ю публічне, сторінку не записано`); process.exit(1); }
console.log(`дані: справжніх значень у стенді ${real.size}, у сторінці 0 · записів замінено ${k}`);
fs.mkdirSync(out, {recursive: true});
const pagePath = path.join(out, 'DES-1_bg.html');
fs.writeFileSync(pagePath, page);
if (process.argv.includes('--page-only')) { console.log('сторінка:', pagePath); process.exit(0); }

(async () => {
  const { chromium, devices } = require('playwright');
  const b = await chromium.launch();
  const ctx = await b.newContext({ ...devices['iPhone 13'], viewport: {width: 390, height: 1000}, deviceScaleFactor: 1 });   // висота — щоб кадр 812 цілий під панеллю кнопок
  const p = await ctx.newPage();
  const errs = []; p.on('pageerror', e => errs.push(String(e)));
  await p.goto('file://' + pagePath); await p.waitForTimeout(800);
  await p.evaluate(() => document.getElementById('zOne').click()); await p.waitForTimeout(300);   // масштаб 1:1 — скло судиться лише на 1:1 (wsd 2.14)
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
    await p.addStyleTag({content: '#sbox, #sbox *{color:transparent!important;-webkit-text-fill-color:transparent!important;text-shadow:none!important}', }).then(h => h.evaluate(n => n.id = 'notext'));
    await p.locator('#sbox').screenshot({ path: path.join(out, `${theme}_${id}_bg.png`) });
    await p.evaluate(() => document.getElementById('notext').remove());
  }
  console.log('кадрів:', shots.length, '· помилок сторінки:', errs.length); errs.forEach(e => console.log('✗', e));
  await b.close(); process.exit(errs.length ? 1 : 0);
})();
