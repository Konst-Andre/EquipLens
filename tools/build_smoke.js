// живе доки: живе білд EquipLens (docs/index.html) — смоук зібраного в браузері (BUILD-1 Ф2-2а · Ф2-2б, S38)
// Chromium образу (Playwright), в'юпорт телефона, мережу закрито: усе має бути у файлі (SW кешує один файл — lens/BACK-1_brief.md §3).
// Обидві теми (prefers-color-scheme light і dark — кожна своя, MASTER_LOCK §13): 0 помилок JS · Manrope справді малює.
// Канарка шрифта — порт зі стенда (tools/EquipLens_headbench_v17_30.html, fontProbe): document.fonts.check() бреше на
// неіснуючій родині (прецедент S32), тому міряється ШИРИНА проти monospace; неіснуюча родина мусить дати ту саму ширину,
// інакше зламаний сам детектор.
//   node tools/build_smoke.js            — ✓ / ✗ останнім рядком
// Оболонка PWA (Ф2-2б): docs/ віддає локальний сервер, як Pages; маніфест — помилки розбору від самого Chromium (CDP
// Page.getAppManifest) · кожна іконка маніфесту (адреса відносно маніфесту, з ?v=) і apple-touch-icon / favicon вантажаться
// й мають заявлений розмір. Page.getInstallabilityErrors НЕ беремо: headless Chromium 157 дає [] навіть без маніфесту (замір S38).
// Токени ≡ стенду (Ф2-3, S39; план — lens/BUILD-1_brief.md §4-в п.3-а): полотно білда (html) ⟂ полотно стенда (#sbox
// замороженого стенда, засів LOCK_SEED, тему ставить детектор — у стенда за замовчуванням light) — ОБЧИСЛЕНІ в Chromium
// background-color · -image · -size · -position · -repeat · -attachment, рівність рядків, обидві теми. color-scheme стенда —
// normal (властивості в стенді нема) → судиться інакше: color-scheme кореня білда мусить містити свою тему.
// Практика (20.11.2026): обчислені стилі двох сторінок фіксованим переліком властивостей — dev.to «Design QA at 1:1»,
// qaskills «assert CSS computed style»; toHaveCSS з @playwright/test не беремо — тут бібліотека без раннера.
// Змінні кореня (S39): кожна CSS-змінна білда ≡ тій самій змінній #sbox стенда (перелік бере стенд, не рука); чужа змінна — ✗
// (крім BUILD_ONLY — платформа); ще не перенесені — рядок покриття «N з M» (--list — їх імена).
//   node tools/build_smoke.js --inject   — base64 шрифту зіпсовано в пам'яті, сервер віддає іконкам 404, у білд дописано
//                                          html{background:#010203 none;color-scheme:only light;--canvas:#010203;--zz-inject:1}
//                                          → шрифт, оболонка, фон, color-scheme, чужа й хибна змінна мусять бути спіймані → «ЗЛОВИВ»
const fs = require('fs'), path = require('path'), http = require('http');
// Playwright образу — /opt/node-tools (NODE_PATH хука старту веде на jsdom у ~/.deps, тож — запасний шлях)
const { chromium } = (() => { try { return require('playwright'); } catch (e) { return require('/opt/node-tools/node_modules/playwright'); } })();
const inject = process.argv.includes('--inject');
const file = path.join(__dirname, '..', 'docs', 'index.html');
const stand = path.join(__dirname, 'EquipLens_headbench_v17_30.html');   // заморожений стенд (CLAUDE.md, BUILD-1 §3)
const BG = ['backgroundColor', 'backgroundImage', 'backgroundSize', 'backgroundPosition', 'backgroundRepeat', 'backgroundAttachment'];
// Змінні білда, яких стенд не має за природою (шар платформи PWA, Ф2-2б): safe-area — у стенді рамку малює harness.
const BUILD_ONLY = ['--sat', '--sar', '--sab', '--sal'];
// Перелік змінних — перебором getComputedStyle: Chromium довго його НЕ давав (blink-dev «Intent to Ship: Custom property
// enumeration in getComputedStyle()», 09.2025); 157 дає (замір S39: 132 на #sbox) → зуби вписують змінну в саму сторінку,
// а стенд мусить дати ≥ MIN_VARS — інакше детектор осліп після оновлення браузера.
const MIN_VARS = 100;
const vars = (cs) => Object.fromEntries([...cs].filter(k => k.startsWith('--')).map(k => [k, cs.getPropertyValue(k).trim()]));

(async () => {
  let html = fs.readFileSync(file, 'utf8');
  if (inject) html = html.replace(/base64,[A-Za-z0-9+/]{400}/, m => 'base64,' + 'A'.repeat(m.length - 7));
  if (inject) html = html.replace('</head>', '<style>html{background:#010203 none!important;color-scheme:only light!important;--canvas:#010203!important;--zz-inject:1}</style></head>');
  const browser = await chromium.launch();
  const errs = [];
  for (const scheme of ['light', 'dark']) {
    const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, colorScheme: scheme, offline: true });
    const page = await ctx.newPage();
    const pe = [];
    page.on('pageerror', e => pe.push(e.message));
    page.on('console', m => { if (m.type() === 'error') pe.push(m.text()); });
    await ctx.route('**/*', r => r.abort());          // жодного запиту назовні
    await page.setContent(html, { waitUntil: 'load' });
    const r = await page.evaluate(async () => {
      try { await document.fonts.load("700 60px Manrope", "EquipLens"); } catch (e) {}   // шрифт лінивий: без цього міряється запасний
      await document.fonts.ready;
      const w = ff => { const c = document.createElement('span');
        c.style.cssText = 'position:absolute;left:-9999px;top:0;white-space:nowrap;font-weight:700;font-size:60px;font-family:' + ff;
        c.textContent = 'EquipLens Аптека ґїє'; document.body.appendChild(c);
        const v = c.getBoundingClientRect().width; c.remove(); return v; };
      const base = w('monospace');
      return { on: w("'Manrope',monospace") !== base, sane: w("'__NOFONT_CANARY__',monospace") === base,
               values: document.documentElement.dataset.values || '0',
               body: getComputedStyle(document.body).fontFamily };
    });
    if (pe.length) errs.push(`${scheme}: помилки JS — ${pe.slice(0, 3).join(' | ')}`);
    if (!r.sane) errs.push(`${scheme}: канарка зламана — неіснуюча родина дала іншу ширину (детектор бреше)`);
    if (!r.on) errs.push(`${scheme}: Manrope не малює (вшитий шрифт не доїхав) — body: ${r.body}`);
    if (r.values === '0') errs.push(`${scheme}: JSON-блок значень не прочитано (data-values = 0)`);
    console.log(`  ${scheme}: помилок JS ${pe.length} · Manrope ${r.on ? '✓' : '✗'} · канарка ${r.sane ? '✓' : '✗'} · значень ${r.values}`);
    // токени ≡ стенду: полотно білда ⟂ полотно стенда тієї самої теми
    const b = await page.evaluate(([BG, vs]) => { const c = getComputedStyle(document.documentElement), vars = eval(vs);
      return { bg: Object.fromEntries(BG.map(k => [k, c[k]])), cs: c.colorScheme, v: vars(c) }; }, [BG, vars.toString()]);
    const sctx = await browser.newContext({ viewport: { width: 390, height: 844 }, colorScheme: scheme });
    await sctx.route(u => !u.protocol.startsWith('file'), r => r.abort());   // Fontshare й інше назовні — ні
    const sp = await sctx.newPage();
    await sp.goto('file://' + stand, { waitUntil: 'load' });
    const s = await sp.evaluate(([BG, sc, vs]) => { themeMode = sc; render();   // let-змінна й функція стенда (стенд :1626, :2350)
      const n = document.getElementById('sbox'), c = getComputedStyle(n), vars = eval(vs);
      return { theme: n.dataset.theme, bg: Object.fromEntries(BG.map(k => [k, c[k]])), v: vars(c) }; }, [BG, scheme, vars.toString()]);
    await sctx.close();
    if (s.theme !== scheme) errs.push(`${scheme}: стенд не перемкнувся на тему (data-theme = ${s.theme}) — детектор бреше`);
    const diff = BG.filter(k => b.bg[k] !== s.bg[k]);
    for (const k of diff) errs.push(`${scheme}: фон ≠ стенду — ${k}: білд «${b.bg[k].slice(0, 90)}» ⟂ стенд «${s.bg[k].slice(0, 90)}»`);
    const csOk = b.cs.split(/\s+/).includes(scheme);
    if (!csOk) errs.push(`${scheme}: color-scheme кореня «${b.cs}» без «${scheme}» (теми — кожна своя, MASTER_LOCK §13)`);
    console.log(`  ${scheme}: фон ≡ стенду ${diff.length ? '✗ ' + diff.length + ' з ' + BG.length : '✓ ' + BG.length + ' з ' + BG.length} · color-scheme «${b.cs}» ${csOk ? '✓' : '✗'}`);
    // змінні кореня (S39, 💡 «перелік бере стенд»): кожна змінна білда ≡ тій самій змінній #sbox стенда; змінна, якої стенд не має, — ✗
    // (крім BUILD_ONLY); ще не перенесені — покриття, не ✗: вони приходять по одній під цим детектором (BUILD-1 §4-в п.3-б)
    const bk = Object.keys(b.v).filter(k => !BUILD_ONLY.includes(k)), sk = Object.keys(s.v);
    if (sk.length < MIN_VARS) errs.push(`${scheme}: стенд дав ${sk.length} змінних < ${MIN_VARS} — перелік getComputedStyle осліп, детектор бреше`);
    const alien = bk.filter(k => !(k in s.v)), wrong = bk.filter(k => k in s.v && b.v[k] !== s.v[k]), todo = sk.filter(k => !(k in b.v));
    for (const k of alien) errs.push(`${scheme}: змінна ${k} — у стенді такої нема (вигадана чи перейменована)`);
    for (const k of wrong) errs.push(`${scheme}: змінна ${k} ≠ стенду — білд «${b.v[k].slice(0, 70)}» ⟂ стенд «${s.v[k].slice(0, 70)}»`);
    console.log(`  ${scheme}: змінні ≡ стенду ${wrong.length || alien.length ? '✗' : '✓'} ${bk.length - alien.length - wrong.length} з ${bk.length} · покриття стенда ${sk.length - todo.length} з ${sk.length}` + (process.argv.includes('--list') ? ` · не перенесено: ${todo.join(' ')}` : ''));
    await ctx.close();
  }
  // оболонка PWA — docs/ з локального сервера, як з Pages (відносні шляхи маніфесту й ?v= — справжні)
  const D = path.join(__dirname, '..', 'docs');
  const T = { '.html': 'text/html', '.webmanifest': 'application/manifest+json', '.png': 'image/png' };
  const srv = http.createServer((q, r) => {
    let u = decodeURIComponent(q.url.split('?')[0]); if (u.endsWith('/')) u += 'index.html';
    const f = path.join(D, u);
    if (!f.startsWith(D) || !fs.existsSync(f) || (inject && u.startsWith('/icons/'))) { r.writeHead(404); return r.end(); }
    r.writeHead(200, { 'content-type': T[path.extname(f)] || 'application/octet-stream' }); fs.createReadStream(f).pipe(r);
  });
  await new Promise(ok => srv.listen(0, '127.0.0.1', ok));
  {
    const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } });
    await ctx.route(u => !u.hostname.match(/^(localhost|127\.0\.0\.1)$/), r => r.abort());   // назовні — нічого
    const page = await ctx.newPage();
    await page.goto(`http://localhost:${srv.address().port}/`, { waitUntil: 'load' });
    const c = await ctx.newCDPSession(page);
    const m = await c.send('Page.getAppManifest');
    if (!m.url || !m.data) errs.push('оболонка: маніфест не знайдено чи порожній (Chromium)');
    if ((m.errors || []).length) errs.push('оболонка: помилки розбору маніфесту — ' + m.errors.map(e => e.message).slice(0, 3).join(' | '));
    const ic = await page.evaluate(async (mu) => {
      const out = [], load = (u, n, who) => new Promise(ok => { const i = new Image();
        i.onload = () => ok(i.naturalWidth === n && i.naturalHeight === n ? null : `${who}: ${i.naturalWidth}×${i.naturalHeight} ≠ ${n}`);
        i.onerror = () => ok(`${who}: не завантажилась (${u})`); i.src = u; });
      let man = {}; try { man = await (await fetch(mu)).json(); } catch (e) { return { n: 0, bad: ['маніфест не JSON'] }; }
      for (const x of man.icons || []) out.push(load(new URL(x.src, mu).href, parseInt(x.sizes), 'іконка ' + x.src));
      for (const [sel, n] of [['link[rel="apple-touch-icon"]', 180], ['link[rel="icon"]', 32]]) {
        const l = document.querySelector(sel); out.push(l ? load(l.href, n, sel) : Promise.resolve(`нема ${sel}`)); }
      const bad = (await Promise.all(out)).filter(Boolean);
      return { n: out.length, bad };
    }, m.url);
    for (const b of ic.bad) errs.push('оболонка: ' + b);
    console.log(`  оболонка PWA: маніфест ${m.data ? '✓' : '✗'} · помилок розбору ${(m.errors || []).length} · іконок ${ic.n}, з них битих ${ic.bad.length}`);
    await ctx.close();
  }
  srv.close();
  await browser.close();
  for (const e of errs) console.log('  ✗ ' + e);
  if (inject) {   // зуби — кожен детектор окремо: шрифт, встановлюваність, фон, color-scheme
    const font = errs.some(e => e.includes('Manrope не малює')), shell = errs.some(e => e.startsWith('оболонка'));
    const bg = ['light', 'dark'].every(sc => errs.some(e => e.startsWith(sc + ': фон ≠ стенду'))),
          cs = errs.some(e => e.startsWith('dark: color-scheme')),
          vr = errs.some(e => e.includes('змінна --canvas ≠')) && errs.some(e => e.includes('змінна --zz-inject'));
    const ok = font && shell && bg && cs && vr;
    console.log(ok ? 'ЗЛОВИВ' : `НЕ ЗЛОВИВ — шрифт ${font ? '✓' : '✗'} · оболонка ${shell ? '✓' : '✗'} · фон ${bg ? '✓' : '✗'} · color-scheme ${cs ? '✓' : '✗'} · змінні ${vr ? '✓' : '✗'}`);
    process.exit(ok ? 1 : 0);
  }
  console.log(`─── білд у браузері: помилок ${errs.length} ` + (errs.length ? '✗ ───' : '✓ ───'));
  process.exit(errs.length ? 1 : 0);
})().catch(e => { console.log('  ✗ ' + e.message); console.log(inject ? 'НЕ ЗЛОВИВ — смоук упав' : '─── білд у браузері: помилок 1 ✗ ───'); process.exit(1); });
