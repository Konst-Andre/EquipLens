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
// Знаменник покриття (Ф2-3в, S39) — лише змінні продукту. Класифікатор за ОЗНАКОЮ, не за іменем: споживачі var(--x) — з ТЕКСТУ
// <style> стенда (CSSOM не годиться: скорочення з var(), перекрите складовою, серіалізується порожнім — csswg-drafts #6253,
// 04.2021; замір S39: так зникли --cdBody · --g1), з атрибутів DOM (style, stop-color…) і з читань JS (getPropertyValue).
// Клас змінної — найкращий з її споживачів (споживач-змінна передає свій клас): живa (елемент у #sbox) > стан (селектор
// зараз нічого не бере і не вимагає варіанта — порожній стан, відкрита картка; у знаменнику, бо в продукті є) > службова
// (лише поза #sbox — harness) > вимкнений варіант (кожна частина селектора вимагає data-k="v" / ~="v", якого засів не обрав)
// > без споживача. Знаменник = живі + стани: хибна «мертва» сховала б неперенесене, тож сумнів іде в знаменник.
// Зуби класифікатора: відомі відповіді SENT · другий канал — мертві ключі lens/EquipLens_head_valuesLOCK.md §2 за іменем
// (такий ключ у знаменнику — ✗) · --inject викидає з джерела правила data-edge → --edgeX мусить зламати відому відповідь.
//   node tools/build_smoke.js --inject   — base64 шрифту зіпсовано в пам'яті, сервер віддає іконкам 404, у білд дописано
//                                          html{background:#010203 none;color-scheme:only light;--canvas:#010203;--zz-inject:1}
//                                          → шрифт, оболонка, фон, color-scheme, чужа й хибна змінна мусять бути спіймані;
//                                          джерело класифікатора без правил data-edge → відома відповідь ✗;
//                                          з білда викинуто removeProperty світлої гілки → перемикання dark→light ✗ → «ЗЛОВИВ»
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
// Відомі відповіді класифікатора (замір S39, засів LOCK_SEED): --z — зум рамки стенда (harness), --edgeX — край аркуша
// (pkEdge = none), --hsize — герой порожнього стану (стан, не засів).
const SENT = { '--ink': 'жива', '--z': 'службова', '--edgeX': 'вимкнений варіант', '--hsize': 'стан' };
const RANK = ['без споживача', 'вимкнений варіант', 'службова', 'стан', 'жива'], PRODUCT = ['жива', 'стан'];
// атрибути варіантів — ті, що стенд пише з важеля S (dataset.onmat = S.ctlOn · data-row="${S.row}"); атрибут стану
// (data-on="${i===chipIdx?1:0}") — ні: інакше «нічого не натиснуто» читалось би як вимкнений варіант (замір S39: --on-*)
const variantAttrs = (src) => [...new Set([...src.matchAll(/dataset\.(\w+)\s*=\s*S\./g)].map(m => m[1].replace(/[A-Z]/g, c => '-' + c.toLowerCase()))
  .concat([...src.matchAll(/data-([\w-]+)="\$\{[^}]*\bS\./g)].map(m => m[1])))];
// споживачі var() з тексту стенда: { var: [{ sel, def }] } — def = змінна-визначник (передає свій клас) або null
const consumers = (src) => {
  const css = (src.match(/<style>([\s\S]*?)<\/style>/g) || []).join('\n').replace(/\/\*[\s\S]*?\*\//g, '');
  const out = {}, add = (v, c) => (out[v] = out[v] || []).push(c);
  const walk = (t, kf) => { let i = 0;
    while (i < t.length) { const o = t.indexOf('{', i); if (o < 0) break;
      const pre = t.slice(i, o).replace(/^[\s\S]*[;}]/, '').trim();
      let d = 1, j = o + 1; while (j < t.length && d) { if (t[j] === '{') d++; else if (t[j] === '}') d--; j++; }
      const body = t.slice(o + 1, j - 1);
      if (pre.startsWith('@')) walk(body, kf || /^@(-webkit-)?keyframes/.test(pre));
      else for (const dec of body.split(/;(?![^(]*\))/)) { const k = dec.indexOf(':'); if (k < 0) continue;
        const prop = dec.slice(0, k).trim();
        for (const m of dec.slice(k + 1).matchAll(/var\(\s*(--[\w-]+)/g)) add(m[1], { sel: kf ? null : pre, def: prop.startsWith('--') ? prop : null }); }
      i = j; } };
  walk(css, false);
  // читання з JS — стан, але лише коли інших споживачів нема (--z читає JS рамки стенда — це не продукт)
  for (const m of src.matchAll(/getPropertyValue\(\s*['"](--[\w-]+)/g)) if (!out[m[1]]) add(m[1], { sel: null, def: null });
  return out;
};
const vars = (cs) => Object.fromEntries([...cs].filter(k => k.startsWith('--')).map(k => [k, cs.getPropertyValue(k).trim()]));

(async () => {
  let html = fs.readFileSync(file, 'utf8');
  if (inject) html = html.replace(/base64,[A-Za-z0-9+/]{400}/, m => 'base64,' + 'A'.repeat(m.length - 7));
  if (inject) html = html.replace('grd.forEach(k => s.removeProperty(k));', '');   // зуби перемикання: темні змінні лишаються в світлій
  if (inject) html = html.replace('</head>', '<style>html{background:#010203 none!important;color-scheme:only light!important;--canvas:#010203!important;--zz-inject:1}</style></head>');
  let src = fs.readFileSync(stand, 'utf8');
  if (inject) src = src.replace(/[^{}]*\[data-edge[^{}]*\{[^}]*\}/g, '');   // зуби класифікатора: правила краю аркуша зникли
  const cons = consumers(src), va = variantAttrs(src);
  if (!['row', 'edge', 'onmat'].every(k => va.includes(k))) throw new Error(`атрибути варіантів стенда — ${va.join(' ')}: нема row · edge · onmat, ознака осліпла`);
  // другий канал — мертві ключі valuesLOCK §2 (рядки «мертві за засівом»), за іменем
  const deadKeys = fs.readFileSync(path.join(__dirname, '..', 'lens', 'EquipLens_head_valuesLOCK.md'), 'utf8').split('\n')
    .filter(l => l.startsWith('|') && l.includes('мертві за засівом')).flatMap(l => [...l.split('|')[1].matchAll(/`(\w+)`/g)].map(m => m[1]));
  if (deadKeys.length < 20) throw new Error(`valuesLOCK §2 дав ${deadKeys.length} мертвих ключів < 20 — другий канал осліп`);
  const browser = await chromium.launch();
  const errs = [], standV = {};
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
    const s = await sp.evaluate(([BG, sc, vs, sels, va]) => { themeMode = sc; render();   // let-змінна й функція стенда (стенд :1626, :2350)
      const n = document.getElementById('sbox'), c = getComputedStyle(n), vars = eval(vs), inBox = e => e === n || n.contains(e);
      // місце селектора: жива (бере елемент у #sbox) · службова (лише поза) · вимкнений варіант · стан
      const strip = q => q.replace(/::?(before|after|placeholder|selection|backdrop|-webkit-[\w-]+)/g, '').replace(/:(hover|active|focus-visible|focus-within|focus)\b/g, '');
      const off = part => [...part.matchAll(/\[data-([\w-]+)(~?)="([^"]*)"\]/g)].some(([, k, t, v]) => { if (!va.includes(k)) return false;
        const has = [n, ...n.querySelectorAll('[data-' + k + ']')].filter(e => e.hasAttribute('data-' + k));
        return has.length && has.every(e => t ? !e.getAttribute('data-' + k).split(/\s+/).includes(v) : e.getAttribute('data-' + k) !== v); });
      const place = Object.fromEntries(sels.map(sel => { let i = false, o = false;
        for (const part of sel.split(',')) { let els = []; try { els = document.querySelectorAll(strip(part).trim() || '*'); } catch (e) {}
          for (const e of els) inBox(e) ? i = true : o = true; }
        return [sel, i ? 'жива' : o ? 'службова' : sel.split(',').every(off) ? 'вимкнений варіант' : 'стан']; }));
      const attr = [];   // var() в атрибутах DOM (style, presentation-атрибути SVG) — сирий текст атрибута, не CSSOM
      for (const e of document.querySelectorAll('*')) for (const a of e.attributes) for (const m of a.value.matchAll(/var\(\s*(--[\w-]+)/g))
        attr.push([m[1], inBox(e) ? 'жива' : 'службова']);
      return { theme: n.dataset.theme, bg: Object.fromEntries(BG.map(k => [k, c[k]])), v: vars(c), place, attr }; },
      [BG, scheme, vars.toString(), [...new Set(Object.values(cons).flat().map(x => x.sel).filter(Boolean))], va]);
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
    // клас кожної змінної стенда: найкращий зі споживачів; споживач-змінна передає свій клас (до нерухомої точки)
    const cls = Object.fromEntries(sk.map(k => [k, 'без споживача'])), up = (k, c) => { if (k in cls && RANK.indexOf(c) > RANK.indexOf(cls[k])) { cls[k] = c; return true; } return false; };
    for (const [k, c] of s.attr) up(k, c);
    for (let ch = true; ch;) { ch = false;
      for (const [k, list] of Object.entries(cons)) for (const x of list) {
        const c = x.def ? (x.def in cls ? cls[x.def] : 'стан') : x.sel ? s.place[x.sel] : 'стан';
        if (c !== 'без споживача' && up(k, c)) ch = true; } }
    for (const [k, want] of Object.entries(SENT)) if (cls[k] !== want)
      errs.push(`${scheme}: класифікатор бреше — ${k} «${cls[k]}», а відома відповідь «${want}»`);
    for (const k of deadKeys.map(x => '--' + x).filter(x => x in cls && PRODUCT.includes(cls[x])))
      errs.push(`${scheme}: класифікатор ⟂ valuesLOCK §2 — ${k} мертвий за засівом, а за ознакою «${cls[k]}»`);
    const prod = sk.filter(k => PRODUCT.includes(cls[k]));
    const alien = bk.filter(k => !(k in s.v)), wrong = bk.filter(k => k in s.v && b.v[k] !== s.v[k]), todo = prod.filter(k => !(k in b.v));
    for (const k of bk.filter(k => k in cls && !PRODUCT.includes(cls[k]))) errs.push(`${scheme}: змінна ${k} перенесена, а в стенді вона «${cls[k]}» — не продукт`);
    const by = c => sk.filter(k => cls[k] === c);
    standV[scheme] = s.v;
    for (const k of alien) errs.push(`${scheme}: змінна ${k} — у стенді такої нема (вигадана чи перейменована)`);
    for (const k of wrong) errs.push(`${scheme}: змінна ${k} ≠ стенду — білд «${b.v[k].slice(0, 70)}» ⟂ стенд «${s.v[k].slice(0, 70)}»`);
    const list = process.argv.includes('--list');
    console.log(`  ${scheme}: змінні ≡ стенду ${wrong.length || alien.length ? '✗' : '✓'} ${bk.length - alien.length - wrong.length} з ${bk.length} · покриття стенда ${prod.length - todo.length} з ${prod.length} (живих ${by('жива').length} · станів ${by('стан').length}) · поза знаменником ${sk.length - prod.length} з ${sk.length}: службових ${by('службова').length} · вимкнених варіантів ${by('вимкнений варіант').length} · без споживача ${by('без споживача').length}` + (list ? ` · не перенесено: ${todo.join(' ')}` : ''));
    if (list) for (const c of RANK.slice(0, 3).concat('стан')) console.log(`    ${scheme} · ${c}: ${by(c).join(' ')}`);
    await ctx.close();
  }
  // перемикання теми наживо (S39, підсилення палітри): застосунок відкритий, система міняє тему → змінні кореня ≡ стенду НОВОЇ
  // теми. Chrome «dark mode»: JS, що читає matchMedia, мусить обробляти change (developer.chrome.com, 20.11.2026); iOS 17
  // standalone тему наживо не міняв (WebKit 262212) — це судить пристрій, тут — наш бік: світла гілка знімає темні змінні.
  for (const [from, to] of [['dark', 'light'], ['light', 'dark']]) {
    const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, colorScheme: from, offline: true });
    await ctx.route('**/*', r => r.abort());
    const page = await ctx.newPage();
    await page.setContent(html, { waitUntil: 'load' });
    await page.emulateMedia({ colorScheme: to });
    // подія change приходить з наступним кадром (замір S39: одразу після emulateMedia — 0 подій, після двох кадрів — 1)
    await page.evaluate(() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))));
    const v = await page.evaluate((vs) => eval(vs)(getComputedStyle(document.documentElement)), vars.toString());
    const bad = Object.keys(v).filter(k => !BUILD_ONLY.includes(k) && !k.startsWith('--zz') && v[k] !== standV[to][k]);
    for (const k of bad) errs.push(`перемикання ${from}→${to}: змінна ${k} «${(v[k] || '').slice(0, 60)}» ⟂ стенд «${(standV[to][k] || '—').slice(0, 60)}»`);
    console.log(`  перемикання ${from}→${to}: змінні ≡ стенду ${bad.length ? '✗ ' + bad.length : '✓'} з ${Object.keys(v).length}`);
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
          vr = errs.some(e => e.includes('змінна --canvas ≠')) && errs.some(e => e.includes('змінна --zz-inject')),
          kl = errs.some(e => e.includes('класифікатор бреше — --edgeX')),
          sw = errs.some(e => e.startsWith('перемикання dark→light: змінна --surface'));
    const ok = font && shell && bg && cs && vr && kl && sw;
    console.log(ok ? 'ЗЛОВИВ' : `НЕ ЗЛОВИВ — шрифт ${font ? '✓' : '✗'} · оболонка ${shell ? '✓' : '✗'} · фон ${bg ? '✓' : '✗'} · color-scheme ${cs ? '✓' : '✗'} · змінні ${vr ? '✓' : '✗'} · класифікатор ${kl ? '✓' : '✗'} · перемикання ${sw ? '✓' : '✗'}`);
    process.exit(ok ? 1 : 0);
  }
  console.log(`─── білд у браузері: помилок ${errs.length} ` + (errs.length ? '✗ ───' : '✓ ───'));
  process.exit(errs.length ? 1 : 0);
})().catch(e => { console.log('  ✗ ' + e.message); console.log(inject ? 'НЕ ЗЛОВИВ — смоук упав' : '─── білд у браузері: помилок 1 ✗ ───'); process.exit(1); });
