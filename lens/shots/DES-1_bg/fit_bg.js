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
    {id:'A', name:'А · Перламутр', src:'lgcl.netlify.app (знімок Konst: L .90–.92 · C .03 · 256–298°) — синій → бузок → рожевий, плями великі й бліді',
      base:{L:.938, C:.020, H:285}, s:{bg:'all', bgH1L:222, bgH2L:268, bgH3L:318, bgA1L:34, bgA2L:30, bgA3L:22, bgSatL:62, bgLtL:80, bgSpread:120, bgTiltL:2}},
    {id:'B', name:'Б · Папір і тінь', src:'Apple «Adopting Liquid Glass»: поверхні читання суцільні + GlassKit світла (C .003) — майже без кольору, глибина тінню',
      base:{L:.970, C:.005, H:240}, s:{bg:'hybrid', bgH1L:220, bgH2L:250, bgH3L:210, bgA1L:12, bgA2L:12, bgA3L:10, bgSatL:30, bgLtL:70, haAL:10, bgTiltL:5}},
    {id:'C', name:'В · Світанок', src:'Dribbble AI (синій ↔ персиковий; кремову рамку h≈90 відкинуто — жовтизна) + Paperpillar (бузок h276): тепле — рожеве, не персик',
      base:{L:.952, C:.012, H:300}, s:{bg:'all', bgH1L:212, bgH2L:345, bgH3L:262, bgA1L:36, bgA2L:30, bgA3L:20, bgSatL:64, bgLtL:80, bgSpread:125, bgTiltL:2}},
    {id:'D', name:'Г · Бірюзове скло', src:'GlassKit світла (glasskit.jungherz.com, фон, що сподобався Konst S40: холодна #F5F7FA → #E8ECF1 + бірюзова аврора) без бурштинового світіння — жовтизна',
      base:{L:.945, C:.012, H:225}, s:{bg:'all', bgH1L:186, bgH2L:200, bgH3L:212, bgA1L:44, bgA2L:34, bgA3L:30, bgSatL:58, bgLtL:66, bgSpread:120, bgTiltL:3}},
  ],
  dark: [
    {id:'now', name:'Зараз', src:'стенд v17_30: майже чорна основа (dkH 250 · C 7 · L 6) + синьо-фіолетова аврора', s:{}},
    {id:'P', name:'Д1 · Петроль', src:'GlassKit темна (glasskit.jungherz.com — фон, що сподобався Konst S40; знімок: #1B4150 · L .34–.45 · C .05 · h≈225; токени #1B3E50 → #0E2530) — кольорова й приглушена; другорядний текст світліший (mutL 86, основа dkL 13): на петролі контраст падав до 3.3 — машина S40, тепер 4.6',
      s:{dkH:200, dkC:42, dkL:13, dkS:4, dkR:8, mutL:86, valL:97, bgH1D:180, bgH2D:196, bgH3D:210, bgA1D:32, bgA2D:22, bgA3D:16, bgSatD:50, bgLtD:42, bgTiltD:2}},
    {id:'I', name:'Д2 · Індиго', src:'Paperpillar (темна кнопка #0D0C21 · h283) + бузок lgcl — глибокий індиго, аврора бузкова з рожевим',
      s:{dkH:250, dkC:34, dkL:9, dkS:6, dkR:10, bgH1D:232, bgH2D:282, bgH3D:318, bgA1D:30, bgA2D:24, bgA3D:12, bgSatD:52, bgLtD:44, bgTiltD:2}},
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
function pick(theme, id){
  Object.keys(S).forEach(k => { S[k] = NOW[k]; });
  cur = {theme, id};
  Object.assign(S, (V[theme].find(x => x.id === id) || {}).s || {});
  themeMode = theme; tab = 'ph';
  render();
  const bar = document.getElementById('fit'), v = V[theme].find(x => x.id === id) || {};
  bar.dataset.theme = theme; bar.dataset.v = id;
  bar.querySelectorAll('[data-th]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.th === theme)));
  bar.querySelector('.fv').innerHTML = V[theme].map(x => `<button data-id="${x.id}" aria-pressed="${x.id===id}">${x.name}</button>`).join('');
  bar.querySelector('.fs').textContent = v.src || '';
}
window.FIT = {V, oklchHex, pick, cur: () => cur};
const css = document.createElement('style');
css.textContent = `#fit{position:fixed;left:0;right:0;top:0;z-index:99;padding:8px 10px 6px;font:13px/1.3 system-ui,sans-serif;color:#222;background:rgba(255,255,255,.94);border-bottom:1px solid rgba(0,0,0,.1)}
#fit[data-theme=dark]{color:#eee;background:rgba(20,20,26,.94);border-color:rgba(255,255,255,.1)}
#fit .row{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:5px}
#fit button{font:inherit;padding:6px 10px;border-radius:999px;border:1px solid rgba(127,127,127,.4);background:transparent;color:inherit}
#fit button[aria-pressed=true]{background:#3a5bd9;color:#fff;border-color:#3a5bd9}
#fit .fs{opacity:.75;font-size:11.5px}
#meter,#fab.bx-fab{display:none!important}   /* службове стенда — не частина екрана */
body{padding-top:var(--fitH,120px)!important}`;
document.head.appendChild(css);
const bar = document.createElement('div'); bar.id = 'fit';
bar.innerHTML = `<div class="row"><b style="align-self:center">Фон · примірка</b><button data-th="light">Світла</button><button data-th="dark">Темна</button></div><div class="row fv"></div><div class="fs"></div>`;
document.body.appendChild(bar);
bar.addEventListener('click', e => {
  const t = e.target.closest('button'); if (!t) return;
  if (t.dataset.th) pick(t.dataset.th, 'now'); else if (t.dataset.id) pick(cur.theme, t.dataset.id);
});
try { setPanel(false); } catch(_){}
pick('light', 'now');
new ResizeObserver(() => document.body.style.setProperty('--fitH', bar.offsetHeight + 8 + 'px')).observe(bar);
})();
