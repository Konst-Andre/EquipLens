// живе доки: живе білд EquipLens (docs/index.html) — смоук зібраного в браузері (BUILD-1 Ф2-2а, S38)
// Chromium образу (Playwright), в'юпорт телефона, мережу закрито: усе має бути у файлі (SW кешує один файл — lens/BACK-1_brief.md §3).
// Обидві теми (prefers-color-scheme light і dark — кожна своя, MASTER_LOCK §13): 0 помилок JS · Manrope справді малює.
// Канарка шрифта — порт зі стенда (tools/EquipLens_headbench_v17_30.html, fontProbe): document.fonts.check() бреше на
// неіснуючій родині (прецедент S32), тому міряється ШИРИНА проти monospace; неіснуюча родина мусить дати ту саму ширину,
// інакше зламаний сам детектор.
//   node tools/build_smoke.js            — ✓ / ✗ останнім рядком
//   node tools/build_smoke.js --inject   — base64 шрифту зіпсовано в пам'яті → мусить бути «ЗЛОВИВ»
const fs = require('fs'), path = require('path');
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
  await browser.close();
  for (const e of errs) console.log('  ✗ ' + e);
  if (inject) { console.log(errs.length ? 'ЗЛОВИВ' : 'НЕ ЗЛОВИВ — детектор без зубів'); process.exit(errs.length ? 1 : 0); }
  console.log(`─── білд у браузері: помилок ${errs.length} ` + (errs.length ? '✗ ───' : '✓ ───'));
  process.exit(errs.length ? 1 : 0);
})().catch(e => { console.log('  ✗ ' + e.message); console.log(inject ? 'НЕ ЗЛОВИВ — смоук упав' : '─── білд у браузері: помилок 1 ✗ ───'); process.exit(1); });
