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
  ],
  dark: [
    {id:'now', name:'Зараз', src:'стенд v17_30: майже чорна основа (dkH 250 · C 7 · L 6) + синьо-фіолетова аврора', s:{}},
    /* Д1 «Петроль» (GlassKit темна) — відкинуто Konst S40: «слабша, ніж у мене темна» */
    /* Д2 «Індиго» — не прийнято Konst S40: «слабша, ніж моя темна… дивна та більш однотипна» → темна — «Зараз» (числа — git v3, 3346bf3) */
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
#fit .fs[hidden]{display:none}
#fit .fi{width:36px;height:36px;padding:0;border-radius:50%;font-weight:700}   /* «i» — тап, не наведення; ціль ≥ 36 px (пошук S40: uxmovement, SAP info popover) */
#meter,#fab.bx-fab,.bx-bar{display:none!important}   /* службове стенда — не частина екрана; .bx-bar — свій перемикач теми стенда, не синхронізований з панеллю примірки (огляд прев'ю v1, S40) */
body{padding-top:var(--fitH,120px)!important}`;
document.head.appendChild(css);
const bar = document.createElement('div'); bar.id = 'fit';
bar.innerHTML = `<div class="row"><b style="align-self:center">Фон · примірка</b><button data-th="light">Світла</button><button data-th="dark">Темна</button><button class="fi" aria-expanded="false" aria-label="Звідки цей варіант">i</button></div><div class="row fv"></div><div class="fs" hidden></div>`;
document.body.appendChild(bar);
bar.addEventListener('click', e => {
  const t = e.target.closest('button'); if (!t) return;
  if (t.classList.contains('fi')) { const f = bar.querySelector('.fs'); f.hidden = !f.hidden; t.setAttribute('aria-expanded', String(!f.hidden)); return; }   /* пояснення — за «i» (Konst S40: текст займав верх екрана телефона) */
  if (t.dataset.th) pick(t.dataset.th, 'now'); else if (t.dataset.id) pick(cur.theme, t.dataset.id);
});
try { setPanel(false); } catch(_){}
pick('light', 'now');
new ResizeObserver(() => document.body.style.setProperty('--fitH', bar.offsetHeight + 8 + 'px')).observe(bar);
})();
