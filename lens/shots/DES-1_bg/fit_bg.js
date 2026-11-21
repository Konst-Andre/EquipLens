/* живе доки: примірка `DES-1` п.5+6 (фон обох тем) без вироку Konst; після вироку — числа в valuesLOCK §3, файл лишається рецептом примірки (lens-governance:tools/claude-code/SHOTS.md §5).
   Накладка поверх стенда tools/EquipLens_headbench_v17_30.html (стенд заморожено — не правимо; сторінку збирає shoot.js).
   (1) новий важіль основи світлої: base {L,C,H} в OKLCH (у стенді — константа #EFEFF3 у трьох місцях: --canvas · --well-bg · --sheet);
   (2) варіанти фону обох тем — палітри з референсів Konst S40 (заміри — lens/DES-1_brief.md §5 п.5+6), не з пам'яті;
   (3) дані — синтетичні (назви й адреси стенда підмінено: прев'ю публічне, lens-governance:tools/PREVIEW.md §3 п.8);
   (4) панель кнопок: тема · варіант; стан — у #fit (data-theme, data-v) для знімальника. */
(function(){
'use strict';
/* OKLCH → sRGB hex (Björn Ottosson, «A perceptual color space for image processing», 2020 — ті самі матриці, що CSS Color 4) */
function oklchHex(L, C, H){
  const a = C*Math.cos(H*Math.PI/180), b = C*Math.sin(H*Math.PI/180);
  const l = (L + 0.3963377774*a + 0.2158037573*b)**3, m = (L - 0.1055613458*a - 0.0638541728*b)**3, s = (L - 0.0894841775*a - 1.2914855480*b)**3;
  const lin = [4.0767416621*l - 3.3077115913*m + 0.2309699292*s, -1.2684380046*l + 2.6097574011*m - 0.3413193965*s, -0.0041960863*l - 0.7034186147*m + 1.7076147010*s];
  return '#' + lin.map(v => { v = Math.max(0, Math.min(1, v)); v = v <= 0.0031308 ? 12.92*v : 1.055*Math.pow(v, 1/2.4) - 0.055; return Math.round(v*255).toString(16).padStart(2,'0'); }).join('').toUpperCase();
}
/* base — основа світлої (OKLCH); s — важелі стенда (аврора HSL: відтінок · альфа · насиченість · світлота; режим · розмах · нахил; темна — dkH · dkC · dkL). src — джерело (показується під кнопками). */
const V = {
  light: [
    {id:'now', name:'Зараз', src:'стенд v17_30: #EFEFF3 + синьо-бірюзова аврора (гібрид: дві плями + смуги під шапкою й острівцем)', base:null, s:{}},
    /* А «Перламутр» і В «Світанок» — зняті з v4: Konst S40 обрав напрям Б («наче добре… але занадто стерильно»); числа — git v3 (3346bf3) */
    {id:'B', name:'Б · Папір і тінь', src:'Apple «Adopting Liquid Glass»: поверхні читання суцільні + GlassKit світла (C .003) — майже без кольору, глибина тінню. Konst S40: «занадто стерильно, скло — статичне тіло»',
      base:{L:.970, C:.005, H:240}, s:{bg:'hybrid', bgH1L:220, bgH2L:250, bgH3L:210, bgA1L:12, bgA2L:12, bgA3L:10, bgSatL:30, bgLtL:70, haAL:10, bgTiltL:5}},
    /* v4 — слово Konst S40: «Б+В… нейтрально цікавіше, м'ятний вайб, пастельний»; відтінки — шкали kigen.design/color (Tailwind, 50–200), заміри OKLCH — lens/DES-1_brief.md §5 п.5+6.
       Скло оживає лише над кольором, який воно розмиває (clay.global «glassmorphism», nngroup «glassmorphism»): у Б кольору під склом майже нема → сила й насиченість еліпсів вищі, основа лишається спокійною. */
    {id:'BC', name:'Б+В', src:'папір Б + рожево-синя аврора В, слабша за В: спокій Б, але скло має що розмивати',
      base:{L:.970, C:.005, H:240}, s:{bg:'all', bgH1L:212, bgH2L:345, bgH3L:262, bgA1L:34, bgA2L:30, bgA3L:24, bgSatL:60, bgLtL:72, bgSpread:120, bgTiltL:2}},
    {id:'M', name:'М\u02bcята', src:'kigen: mint 50 #DFF6EA (основа, приглушена до C .014) · аврора mint 100 #B1E8CE · aqua #9FE2D8 · sky #D1E2F6',
      base:{L:.962, C:.014, H:165}, s:{bg:'all', bgH1L:152, bgH2L:171, bgH3L:212, bgA1L:34, bgA2L:28, bgA3L:22, bgSatL:56, bgLtL:80, bgSpread:120, bgTiltL:2}},
    {id:'P', name:'Пастель', src:'kigen: нейтральний папір · аврора mint #B1E8CE · lilac #E2D9F3 · blush #F7DDE7 — три пастелі, жодна не головна',
      base:{L:.965, C:.006, H:250}, s:{bg:'all', bgH1L:152, bgH2L:261, bgH3L:337, bgA1L:38, bgA2L:34, bgA3L:28, bgSatL:62, bgLtL:72, bgSpread:125, bgTiltL:2}},
    {id:'S', name:'Шавлія', src:'kigen: Mineral Green (mineral 400 #6D9180, h 164) — основа сіро-зелена, аврора тінню (як Б), але з відтінком м\u02bcяти й бузку',
      base:{L:.955, C:.016, H:160}, s:{bg:'hybrid', bgH1L:152, bgH2L:200, bgH3L:261, bgA1L:22, bgA2L:16, bgA3L:14, bgSatL:34, bgLtL:70, haAL:12, bgTiltL:4}},
    /* Г «Бірюзове скло» (GlassKit світла) — відкинуто Konst S40: «для світлої теми вона не буде працювати» */
    /* v6 — Konst 21.11: «ще варіанти… навіщо рожевий… тришарова аврора, щоб відчувався відблиск». Нові — без рожевого (рожеве прийшло з В «Світанок»);
       холодна гама навколо м'яти, відтінки — шкали kigen.design/color; третій шар — `fx` (відблиск), перемикач «Відблиск» у панелі. */
    {id:'L1', name:'Лагуна', src:'аква · бірюза · м\u02bcята (kigen aqua 100 #9FE2D8 · mint 100): морська вода на мілині', base:{L:.962, C:.012, H:195},
      s:{bg:'all', bgH1L:171, bgH2L:195, bgH3L:152, bgA1L:34, bgA2L:30, bgA3L:22, bgSatL:58, bgLtL:74, bgSpread:120, bgTiltL:2}},
    {id:'L2', name:'Лаванда й м\u02bcята', src:'бузок (kigen lilac 100 #E2D9F3) · м\u02bcята · блакить — прохолодно, без рожевого', base:{L:.966, C:.008, H:280},
      s:{bg:'all', bgH1L:261, bgH2L:152, bgH3L:212, bgA1L:34, bgA2L:28, bgA3L:22, bgSatL:56, bgLtL:76, bgSpread:120, bgTiltL:2}, fx:{irid:.12}},
    {id:'L3', name:'Перлина', src:'перламутр: три бліді відтінки (м\u02bcята · блакить · бузок) + сильний відблиск і райдужна плівка — показ третього шару', base:{L:.972, C:.006, H:260},
      s:{bg:'all', bgH1L:171, bgH2L:230, bgH3L:280, bgA1L:26, bgA2L:24, bgA3L:20, bgSatL:50, bgLtL:80, bgSpread:125, bgTiltL:2}, fx:{rim:1, top:.7, bot:.6, side:.38, irid:.14}},
    {id:'L4', name:'Морозна м\u02bcята', src:'м\u02bcята з крижаною блакиттю, основа холодніша', base:{L:.968, C:.010, H:180},
      s:{bg:'all', bgH1L:160, bgH2L:200, bgH3L:225, bgA1L:30, bgA2L:24, bgA3L:20, bgSatL:52, bgLtL:78, bgSpread:120, bgTiltL:2}, fx:{side:.40}},
    {id:'L5', name:'Евкаліпт', src:'сіро-бірюзова основа, аврора кольоровою тінню (як Б, але з характером)', base:{L:.950, C:.018, H:185},
      s:{bg:'hybrid', bgH1L:175, bgH2L:150, bgH3L:205, bgA1L:24, bgA2L:18, bgA3L:14, bgSatL:36, bgLtL:66, haAL:14, bgTiltL:4}},
    {id:'L6', name:'Північне сяйво', src:'смуги м\u02bcяти, бірюзи й фіалки — найсміливіший світлий', base:{L:.965, C:.008, H:230},
      s:{bg:'all', bgH1L:150, bgH2L:185, bgH3L:270, bgA1L:40, bgA2L:34, bgA3L:26, bgSatL:62, bgLtL:72, bgSpread:125, bgTiltL:2}},
    {id:'L7', name:'Небо', src:'блакить трьох відтінків (kigen sky 100 #D1E2F6) + яскравий відблиск угорі — ясний день', base:{L:.968, C:.010, H:240},
      s:{bg:'all', bgH1L:205, bgH2L:220, bgH3L:190, bgA1L:32, bgA2L:26, bgA3L:20, bgSatL:60, bgLtL:78, bgSpread:120, bgTiltL:2}, fx:{top:.75}},
    {id:'L8', name:'Нефрит', src:'насичена зелень каменю (Mineral Green, h 155–175) — найзеленіший', base:{L:.955, C:.020, H:160},
      s:{bg:'all', bgH1L:155, bgH2L:140, bgH3L:175, bgA1L:36, bgA2L:28, bgA3L:22, bgSatL:50, bgLtL:70, bgSpread:120, bgTiltL:2}},
    /* v7 — ще покращені (Konst 21.11 «ще більше варіантів»): відблиск у кожному — світло-рамка й кант скла */
    {id:'L9', name:'Аква-перлина', src:'аква з перламутровим кантом — найбільше «скла»', base:{L:.968, C:.010, H:200},
      s:{bg:'all', bgH1L:180, bgH2L:205, bgH3L:230, bgA1L:32, bgA2L:26, bgA3L:20, bgSatL:56, bgLtL:76, bgSpread:125, bgTiltL:2}, fx:{rim:1, top:.65, bot:.6, side:.36, irid:.10}},
    {id:'L10', name:'Ранок без рожевого', src:'блакить, бузок і м\u02bcята — світанок холодний', base:{L:.966, C:.008, H:250},
      s:{bg:'all', bgH1L:212, bgH2L:255, bgH3L:160, bgA1L:34, bgA2L:28, bgA3L:22, bgSatL:58, bgLtL:76, bgSpread:125, bgTiltL:2}},
    {id:'L11', name:'Льодовик', src:'насичена крижана блакить і ціан, найхолодніший', base:{L:.962, C:.014, H:220},
      s:{bg:'all', bgH1L:195, bgH2L:210, bgH3L:180, bgA1L:38, bgA2L:32, bgA3L:24, bgSatL:64, bgLtL:72, bgSpread:120, bgTiltL:2}, fx:{top:.7, bot:.65}},
    {id:'L12', name:'Сутінки', src:'бузково-блакитні сутінки, глибші за Лаванду', base:{L:.966, C:.012, H:275},
      s:{bg:'all', bgH1L:250, bgH2L:270, bgH3L:200, bgA1L:38, bgA2L:32, bgA3L:24, bgSatL:54, bgLtL:75, bgSpread:120, bgTiltL:2}, fx:{side:.40}},
  ],
  dark: [
    {id:'now', name:'Зараз', src:'стенд v17_30: майже чорна основа (dkH 250 · C 7 · L 6) + синьо-фіолетова аврора', s:{}},
    /* Д1 «Петроль» (GlassKit темна) — відкинуто Konst S40: «слабша, ніж у мене темна» */
    /* Д2 «Індиго» — не прийнято Konst S40: «слабша, ніж моя темна… дивна та більш однотипна» → темна — «Зараз» (числа — git v3, 3346bf3) */
    /* v6 — темна: твоя «Зараз» лишається базою; у нових яскравіше світіння, тож тихе чорнило (другорядний текст) світліше — mutL 82 замість 74 (той самий лік, що в Д1 S40: парне чорнило); нові — сусіди її настрою (глибока основа + світіння), D7 — «Зараз» лише з третім шаром */
    {id:'D1', name:'Глибоке море', src:'темна бірюза: основа h 215, світіння бірюзи й аква', s:{mutL:82, dkH:215, dkC:12, dkL:7, bgH1D:190, bgH2D:210, bgH3D:170, bgA1D:30, bgA2D:18, bgA3D:10, bgSatD:70, bgLtD:46}},
    {id:'D2', name:'Смарагдова ніч', src:'зелено-бірюзове світіння на майже чорному — м\u02bcята вночі', s:{mutL:82, dkH:180, dkC:8, dkL:6, bgH1D:160, bgH2D:175, bgH3D:200, bgA1D:28, bgA2D:16, bgA3D:10, bgSatD:64, bgLtD:44}},
    {id:'D3', name:'Північне сяйво', src:'класичне сяйво: зелень → бірюза → фіалка', s:{mutL:82, dkH:240, dkC:8, dkL:6, bgH1D:150, bgH2D:175, bgH3D:280, bgA1D:30, bgA2D:20, bgA3D:14, bgSatD:72, bgLtD:48}},
    {id:'D4', name:'Опівніч', src:'твоя «Зараз», але глибша й сильніша: синє світіння яскравіше, основа темніша', s:{mutL:82, dkH:250, dkC:9, dkL:5, bgH1D:215, bgH2D:265, bgH3D:190, bgA1D:34, bgA2D:20, bgA3D:12, bgSatD:78, bgLtD:50}},
    {id:'D5', name:'Графіт і м\u02bcята', src:'нейтральний графіт, тихе м\u02bcятне світіння', s:{mutL:82, dkH:200, dkC:3, dkL:7, bgH1D:160, bgH2D:190, bgH3D:150, bgA1D:22, bgA2D:12, bgA3D:8, bgSatD:56, bgLtD:42}},
    {id:'D6', name:'Космос', src:'три різні світіння (блакить · фіалка · бірюза) — найбільше глибини', s:{mutL:82, dkH:255, dkC:8, dkL:5, bgH1D:200, bgH2D:285, bgH3D:175, bgA1D:30, bgA2D:22, bgA3D:16, bgSatD:74, bgLtD:48}, fx:{irid:.06}},
    {id:'D7', name:'Зараз + відблиск', src:'твоя «Зараз» без змін, лише третій шар: смуга світла, блиск угорі, райдужна плівка + тихе чорнило світліше (82 замість 74), щоб другорядний текст не тонув', s:{mutL:82}, fx:{rim:.6, top:.2, bot:.2, side:.12, irid:.04}},
    {id:'D8', name:'Бірюзове сяйво', src:'сильне бірюзове світіння, кант скла яскравіший', s:{mutL:82, dkH:205, dkC:10, dkL:6, bgH1D:180, bgH2D:200, bgH3D:165, bgA1D:34, bgA2D:22, bgA3D:12, bgSatD:76, bgLtD:48}, fx:{rim:.65, top:.2, bot:.22}},
    {id:'D9', name:'Фіалка й бірюза', src:'фіалкове й бірюзове світіння навпроти — контраст кольору', s:{mutL:82, dkH:265, dkC:9, dkL:6, bgH1D:175, bgH2D:285, bgH3D:200, bgA1D:30, bgA2D:24, bgA3D:14, bgSatD:72, bgLtD:48}},
    {id:'D10', name:'Нічна м\u02bcята', src:'м\u02bcятне світіння сильніше, ніж у Смарагдовій', s:{mutL:82, dkH:175, dkC:7, dkL:5, bgH1D:155, bgH2D:170, bgH3D:185, bgA1D:34, bgA2D:22, bgA3D:12, bgSatD:66, bgLtD:46}, fx:{side:.14}},
    {id:'D11', name:'Глибокий космос', src:'темніша основа, три яскраві світіння — найглибший', s:{mutL:82, dkH:255, dkC:9, dkL:4, bgH1D:205, bgH2D:280, bgH3D:170, bgA1D:36, bgA2D:26, bgA3D:18, bgSatD:80, bgLtD:50}, fx:{rim:.6, top:.2, bot:.2, side:.12, irid:.05}},
  ]
};
const NOW = JSON.parse(JSON.stringify(S));
let cur = {theme:'light', id:'now'};
PHARM.forEach((p, i) => { p.n = 'Аптека ' + (i + 1); p.a = 'вул. Тестова, ' + (i*7 + 3); p.c = i % 2 ? 'Місто Б' : 'Місто А'; });
const base0 = applyVars;
window.applyVars = function(){
  base0();
  const v = V[cur.theme].find(x => x.id === cur.id);
  if (effTheme() === 'light' && v && v.base){
    const hx = oklchHex(v.base.L, v.base.C, v.base.H), st = sbox.style;
    st.setProperty('--canvas', hx);
    st.setProperty('--well-bg', mixHex('#FFFFFF', hx, S.wMixL/100));
    st.setProperty('--sheet', hexA(hx, S.shtAL/100));
  }
};
/* ТРЕТІЙ ШАР — ВІДБЛИСК (Konst 21.11, друга редакція: «скло грається зі світлом, переливається… зверху підсвічує хедер, знизу острівець, по центру — як по краях»).
   Перша редакція (діагональна смуга у фоні) — хибна: відблиск — властивість СКЛА, не фону. Apple Liquid Glass: «specular highlights», що реагують на рух,
   іскри ковзають по закругленому краю (apple.com/newsroom 06.2025 «new software design»; механіка з рухом — gcn.com, не перевірено), 21.11.2026.
   Тепер два носії: (а) світло-рамка у фоні — смуга під шапкою, смуга під острівцем (у px, як гібрид стенда: haY · haYB), бічні світіння посередині;
   (б) світний кант на склі (картки · острівець · «+» · капсула шапки): яскраве ребро з боку світла, кут світла `--la` повертається під час прокрутки — блиск ковзає по ребру.
   «Зараз» — без шару (база машини); перемикач «Відблиск» вимикає обидва носії. */
const FX0 = {light:{top:.55, bot:.50, side:.30, rim:.95, irid:0}, dark:{top:.16, bot:.16, side:.10, rim:.50, irid:0}};
let fxOn = true;
const aur0 = aurLayers;
function fxOf(dark){ const v = V[cur.theme].find(x => x.id === cur.id) || {}; return (!fxOn || (v.id === 'now' && !v.fx)) ? null : Object.assign({}, FX0[dark ? 'dark' : 'light'], v.fx || {}); }
window.aurLayers = function(dark){
  const b = aur0(dark), f = fxOf(dark);
  if (!b || !f) return b;
  const w = a => `rgba(255,255,255,${a.toFixed(3)})`, L = [];
  const hb = dark ? S.bgH3D : S.bgH3L, glow = a => hsl(hb, dark ? 70 : 60, dark ? 62 : 86, a.toFixed(3));   // світло з відтінком аврори варіанта
  /* світло шапки — під СКЛОМ, не в центрі (Konst 21.11: «по центру надто агресивне… скло в хедері з лівого та правого краю»): дві плями під плиткою знака
     і капсулою дій; ліва сильніша — ОДНЕ джерело світла угорі зліва, той самий кут, що в канта (`--la` 125°; brand.github.com «product UI»: блиск угорі зліва,
     загасання вниз праворуч; material.io «light and shadows»), 21.11.2026; центр шапки — тихий */
  if (f.top){ L.push(`radial-gradient(ellipse 26% 54px at 11% ${S.haY - 6}px, ${w(f.top * .8)} 0, ${glow(f.top * .45)} 40%, transparent 72%)`);
    L.push(`radial-gradient(ellipse 28% 50px at 85% ${S.haY}px, ${w(f.top * .5)} 0, ${glow(f.top * .3)} 40%, transparent 72%)`); }
  /* світло низу — так само під СКЛОМ (Konst 21.11: «врахуй острівець з табами, FAB і картки»): пляма під острівцем (він ліворуч від центру) і окрема менша
     під «+» праворуч; між ними — тихо. Картки світло бере кантом з того ж джерела (угорі зліва) */
  if (f.bot){ const nv = sbox.querySelector('.el-nav'), fb = sbox.querySelector('.el-fab'), R = sbox.getBoundingClientRect();
    const cx = e => e ? Math.round(((e.getBoundingClientRect().left + e.getBoundingClientRect().width / 2) - R.left) / R.width * 100) : null;
    const xn = cx(nv) ?? 38, xf = cx(fb) ?? 84;
    L.push(`radial-gradient(ellipse 40% 64px at ${xn}% calc(100% - ${S.haYB}px), ${w(f.bot * .75)} 0, ${glow(f.bot * .45)} 40%, transparent 72%)`);
    L.push(`radial-gradient(ellipse 16% 52px at ${xf}% calc(100% - ${S.haYB}px), ${w(f.bot * .6)} 0, ${glow(f.bot * .35)} 40%, transparent 72%)`); }
  if (f.side) { L.push(`radial-gradient(ellipse 22% 38% at 0% 50%, ${glow(f.side)} 0, transparent 70%)`); L.push(`radial-gradient(ellipse 22% 38% at 100% 55%, ${glow(f.side)} 0, transparent 70%)`); }
  if (f.irid){ const l = dark ? 60 : 72, c = h => `hsla(${h},85%,${l}%,${f.irid.toFixed(3)})`;
    L.push(`conic-gradient(from 210deg at 28% 72%, ${c(160)}, ${c(195)}, ${c(235)}, ${c(275)}, ${c(160)})`); }
  return L.concat(b).join(',');   // перший шар малюється зверху
};
const GLASS = '.el-list[data-row="card"] .el-item, .el-nav, .el-fab, .el-act';
function rimSync(){ const f = fxOf(effTheme() === 'dark'); sbox.classList.toggle('fxrim', !!(f && f.rim)); if (f) sbox.style.setProperty('--ra', f.rim); }
function pick(theme, id){
  Object.keys(S).forEach(k => { S[k] = NOW[k]; });
  cur = {theme, id};
  Object.assign(S, (V[theme].find(x => x.id === id) || {}).s || {});
  themeMode = theme; tab = 'ph';
  render(); rimSync();
  const bar = document.getElementById('fit'), v = V[theme].find(x => x.id === id) || {};
  bar.dataset.theme = theme; bar.dataset.v = id;
  bar.querySelectorAll('[data-th]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.th === theme)));
  const sel = bar.querySelector('.fsel'), k = V[theme].findIndex(x => x.id === id);
  sel.innerHTML = V[theme].map((x, n) => `<option value="${x.id}"${x.id===id ? ' selected' : ''}>${typeof top !== 'undefined' && top.includes(theme + ':' + x.id) ? '★ ' : ''}${n + 1}/${V[theme].length} · ${x.name}</option>`).join('');
  bar.querySelector('.fxb').setAttribute('aria-pressed', String(fxOn));
  const key = theme + ':' + id, st = bar.querySelector('.fstar'); if (st && typeof top !== 'undefined'){ st.textContent = top.includes(key) ? '★' : '☆'; st.setAttribute('aria-pressed', String(top.includes(key))); bar.querySelector('.ftop').textContent = `Мій топ: ${top.length} · скопіювати`; }
  bar.querySelector('.fs').textContent = v.src || '';
}
window.FIT = {V, oklchHex, pick, cur: () => cur, fx: on => { fxOn = on; pick(cur.theme, cur.id); }};
const css = document.createElement('style');
css.textContent = `#fit{position:fixed;left:0;right:0;top:0;z-index:99;padding:8px 10px 6px;font:13px/1.3 system-ui,sans-serif;color:#222;background:rgba(255,255,255,.94);border-bottom:1px solid rgba(0,0,0,.1)}
#fit[data-theme=dark]{color:#eee;background:rgba(20,20,26,.94);border-color:rgba(255,255,255,.1)}
#fit .row{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:5px}
#fit button{font:inherit;padding:6px 10px;border-radius:999px;border:1px solid rgba(127,127,127,.4);background:transparent;color:inherit}
#fit button[aria-pressed=true]{background:#3a5bd9;color:#fff;border-color:#3a5bd9}
#fit .fs{opacity:.75;font-size:11.5px}
#fit .fnav{flex-wrap:nowrap}
#fit .fsel{flex:1;min-width:0;font:16px system-ui,sans-serif;padding:6px 10px;border-radius:999px;border:1px solid rgba(127,127,127,.4);background:transparent;color:inherit}   /* 16 px — iOS не збільшує сторінку на фокусі; список — рідне колесо вибору iPhone */
#fit .fp,#fit .fn{width:44px;height:44px;padding:0;font-size:20px}
#fit .fsel{height:44px}
#fit button:active{transform:scale(.94);background:rgba(127,127,127,.18)}   /* відгук пальцю (кукбук A67); ціль 44 px — Apple */
#fit .fs[hidden]{display:none}
#fit .fi{width:36px;height:36px;padding:0;border-radius:50%;font-weight:700}   /* «i» — тап, не наведення; ціль ≥ 36 px (пошук S40: uxmovement, SAP info popover) */
#meter,#fab.bx-fab,.bx-bar{display:none!important}   /* службове стенда — не частина екрана; .bx-bar — свій перемикач теми стенда, не синхронізований з панеллю примірки (огляд прев'ю v1, S40) */
body{padding-top:var(--fitH,120px)!important}
#sbox.fxrim :is(.el-list[data-row="card"] .el-item, .el-nav, .el-fab, .el-act)::after{content:"";position:absolute;inset:0;border-radius:inherit;padding:1.3px;pointer-events:none;z-index:3;
 background:linear-gradient(var(--la,125deg), rgba(255,255,255,var(--ra)) 0%, rgba(255,255,255,0) 26%, rgba(255,255,255,0) 66%, rgba(255,255,255,calc(var(--ra) * .5)) 100%);
 -webkit-mask:linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);-webkit-mask-composite:xor;mask-composite:exclude}   /* кант-блиск: лише ребро (маска «рамка»), кут світла — --la */
#fit .fstar{width:44px;height:44px;padding:0;font-size:18px}
#fit .ftop{font-size:12px}`;
document.head.appendChild(css);
const bar = document.createElement('div'); bar.id = 'fit';
bar.innerHTML = `<div class="row"><b style="align-self:center">Фон</b><button data-th="light">Світла</button><button data-th="dark">Темна</button><button class="fxb" aria-pressed="true">Відблиск</button><button class="fi" aria-expanded="false" aria-label="Звідки цей варіант">i</button></div><div class="row fnav"><button class="fp" aria-label="Попередній варіант">‹</button><select class="fsel" aria-label="Варіант фону"></select><button class="fn" aria-label="Наступний варіант">›</button><button class="fstar" aria-pressed="false" aria-label="Додати в топ">☆</button></div><div class="row"><button class="ftop">Мій топ: 0 · скопіювати</button></div><div class="fs" hidden></div>`;
document.body.appendChild(bar);
bar.addEventListener('click', e => {
  const t = e.target.closest('button'); if (!t) return;
  if (t.classList.contains('fi')) { const f = bar.querySelector('.fs'); f.hidden = !f.hidden; t.setAttribute('aria-expanded', String(!f.hidden)); return; }   /* пояснення — за «i» (Konst S40: текст займав верх екрана телефона) */
  if (t.classList.contains('fstar')) { const k = cur.theme + ':' + cur.id; top = top.includes(k) ? top.filter(x => x !== k) : top.concat(k); saveTop(); pick(cur.theme, cur.id); return; }
  if (t.classList.contains('ftop')) { const txt = 'Топ фону: ' + (top.map(k => { const [th, id] = k.split(':'); return (th === 'light' ? 'світла ' : 'темна ') + ((V[th].find(x => x.id === id) || {}).name || id); }).join(' · ') || 'порожньо');
    (navigator.clipboard ? navigator.clipboard.writeText(txt) : Promise.reject()).then(() => { t.textContent = 'Скопійовано — встав у чат'; }, () => { window.prompt('Скопіюйте:', txt); }); return; }
  if (t.classList.contains('fxb')) { fxOn = !fxOn; pick(cur.theme, cur.id); return; }
  if (t.classList.contains('fp') || t.classList.contains('fn')) { const L = V[cur.theme], k = L.findIndex(x => x.id === cur.id); pick(cur.theme, L[(k + (t.classList.contains('fn') ? 1 : L.length - 1)) % L.length].id); return; }
  if (t.dataset.th) pick(t.dataset.th, 'now');
});
/* кант-блиск потребує позиціонованого предка: лише статичним даємо relative (острівець і «+» уже позиціоновані) */
new MutationObserver(() => sbox.querySelectorAll(GLASS).forEach(e => { if (getComputedStyle(e).position === 'static') e.style.position = 'relative'; })).observe(sbox, {childList:true, subtree:true});
/* блиск ковзає по ребру під час прокрутки (наближення руху телефона; гіроскоп на iPhone потребує дозволу — не в примірці) */
sbox.addEventListener('scroll', e => { sbox.style.setProperty('--la', (125 + (e.target.scrollTop || 0) * 0.12) % 360 + 'deg'); }, true);
/* ★ у топ (💡 агента, Konst: «це дефолт») — вибір живе лише на цьому телефоні; «Топ» копіює список для агента */
const TOPK = 'des1bg_top'; let top = []; try { top = JSON.parse(localStorage.getItem(TOPK) || '[]'); } catch(_){}
const saveTop = () => { try { localStorage.setItem(TOPK, JSON.stringify(top)); } catch(_){} };
window.FIT_TOP = () => top;
try { setPanel(false); } catch(_){}
pick('light', 'now');
bar.querySelector('.fsel').addEventListener('change', e => pick(cur.theme, e.target.value));
new ResizeObserver(() => document.body.style.setProperty('--fitH', bar.offsetHeight + 8 + 'px')).observe(bar);
})();
