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
//   node tools/build_smoke.js --inject   — base64 шрифту зіпсовано в пам'яті І сервер віддає іконкам 404 → обидва мусять
//                                          бути спіймані → «ЗЛОВИВ»
const fs = require('fs'), path = require('path'), http = require('http');
// Playwright образу — /opt/node-tools (NODE_PATH хука старту веде на jsdom у ~/.deps, тож — запасний шлях)
const { chromium } = (() => { try { return require('playwright'); } catch (e) { return require('/opt/node-tools/node_modules/playwright'); } })();
const inject = process.argv.includes('--inject');
const file = path.join(__dirname, '..', 'docs', 'index.html');

(async () => {
  let html = fs.readFileSync(file, 'utf8');
  if (inject) html = html.replace(/base64,[A-Za-z0-9+/]{400}/, m => 'base64,' + 'A'.repeat(m.length - 7));
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
  if (inject) {   // зуби — кожен детектор окремо: шрифт і встановлюваність
    const font = errs.some(e => e.includes('Manrope не малює')), shell = errs.some(e => e.startsWith('оболонка'));
    const ok = font && shell;
    console.log(ok ? 'ЗЛОВИВ' : `НЕ ЗЛОВИВ — шрифт ${font ? '✓' : '✗'} · оболонка ${shell ? '✓' : '✗'}`);
    process.exit(ok ? 1 : 0);
  }
  console.log(`─── білд у браузері: помилок ${errs.length} ` + (errs.length ? '✗ ───' : '✓ ───'));
  process.exit(errs.length ? 1 : 0);
})().catch(e => { console.log('  ✗ ' + e.message); console.log(inject ? 'НЕ ЗЛОВИВ — смоук упав' : '─── білд у браузері: помилок 1 ✗ ───'); process.exit(1); });
