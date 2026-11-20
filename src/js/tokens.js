/* живе доки: живе застосунок · токени (BUILD-1 Ф2-3, S39). Порт функцій категорії T замороженого стенда 1:1 —
   tools/EquipLens_headbench_v17_30.html: hx · rh · mixHex (:1993–1995) · hsl (:2000) · AUR (:2392) · aurLayers (:2405) ·
   гілка «ґрунт» applyVars (:2860–2902) · hexA (:2004) · картка applyVars (:2569–2610); рядки скопійовано,
   не переписано (BUILD-1 §4-в «JS — простими файлами в одному просторі»). Стоїть у <head> синхронно — до першого кадру
   (синхронний скрипт у head блокує рендер; dev.to 137foundry «flash of wrong theme», 20.11.2026).
   Значення — JSON-блок #values (джерело — lens/EquipLens_head_valuesLOCK.md); `S` — ім'я стану в стенді, тут той самий об'єкт.
   Детектор «токени ≡ стенду» — tools/build_smoke.js (обчислений фон html ≡ #sbox стенда, обидві теми). */
const V = JSON.parse(document.getElementById('values').textContent), S = V;
const hx = h => { const n = parseInt(h.slice(1),16); return [n>>16&255,n>>8&255,n&255]; };
const rh = a => '#' + a.map(v => Math.round(Math.max(0,Math.min(255,v))).toString(16).padStart(2,'0')).join('');
const mixHex = (a,b,t) => rh(hx(a).map((v,i) => v + (hx(b)[i]-v)*t));
const hsl = (h,s,l,a) => a==null ? `hsl(${h} ${s}% ${l}%)` : `hsl(${h} ${s}% ${l}% / ${a})`;
const hexA = (h,a) => { const c = hx(h); return `rgba(${c[0]},${c[1]},${c[2]},${a.toFixed(3)})`; };
const AUR = {
  all:    [[20,40, 90, 80,55],[80,65, 85, 75,50],[50,20, 95, 85,50]],
  chrome: [[50,97, 95, 30,42],[85,88, 90, 28,34],[50, 3, 95, 26,30]],
  /* v17_27 · К1-в-аврора · ГІБРИД. Дві плями `all` (E1 низ-ліво, E2 низ-право)
     лишаються БЕЗ ЗМІН — це той баланс «синє зліва / фіолет справа», який
     залочено оком. E3 (верхній, слабкий) знято: його місце займає смуга,
     прив'язана В ПІКСЕЛЯХ від краю, а не у відсотках висоти.
     ЧОМУ ПІКСЕЛІ. Відсоток висоти робить картинку заручником контейнера:
     ті самі числа в ряду 70px і на екрані 812px дають різні картинки
     (діагноз S33 §3). Шапка й острівець мають ФІКСОВАНУ висоту в px —
     отже і світло під ними мусить мірятись у px. Полотно лишається у %. */
  hybrid: [[20,40, 90, 80,55],[80,65, 85, 75,50]]
};
function aurLayers(dark){
  if (S.bg === 'sheet' || !AUR[S.bg]) return '';
  /* v17_4 · хід 2 · відтінок роздільний по темах: на світлій аврора — кольорова
     ТІНЬ, на темній — СВІТІННЯ. Спільне число обслуговувало два різні явища (A39). */
  const hu = dark ? [S.bgH1D, S.bgH2D, S.bgH3D] : [S.bgH1L, S.bgH2L, S.bgH3L];
  const al = dark ? [S.bgA1D, S.bgA2D, S.bgA3D] : [S.bgA1L, S.bgA2L, S.bgA3L];
  /* Світлота еліпса роздільна по темах — на темній канві світлий еліпс мусить
     бути темнішим, інакше він читається як засвітка, а не як атмосфера (A39). */
  const lt = dark ? S.bgLtD : S.bgLtL, sa = dark ? S.bgSatD : S.bgSatL,
        sp = S.bgSpread / 100;
  /* v17_5 · хід 3 · bgSpread масштабує РАДІУСИ, не стоп. Стоп лишається
     прибитим: він задає м'якість краю плями, а м'якість — властивість
     матеріалу, не розміру. Масштабувати обидва означало б, що один повзунок
     міняє дві незалежні речі, і жодну з них не можна судити окремо. */
  const L = AUR[S.bg].map((p, i) =>
    `radial-gradient(ellipse ${Math.round(p[2] * sp)}% ${Math.round(p[3] * sp)}% `
    + `at ${p[0]}% ${p[1]}%, `
    + `${hsl(hu[i], sa, lt, (al[i] / 100).toFixed(3))} 0, `
    + `transparent ${p[4]}%)`);
  /* v17_27 · дві смуги хрому в ПІКСЕЛЯХ. unshift, бо перший шар малюється
     ЗВЕРХУ: смуга мусить лежати над полотняними плямами, інакше вона
     потрапить під них і замір під склом покаже одне, а око — інше.
     Ширина у %, висота і центр у px — змішана одиниця в `ellipse` дозволена
     і саме вона дає незалежність від висоти контейнера. */
  if (S.bg === 'hybrid'){
    const ha = ((dark ? S.haAD : S.haAL) / 100).toFixed(3);
    const wd = Math.round(S.haWd * sp), ht = Math.round(S.haHt * sp);
    /* верхня смуга бере відтінок E3 (він і був «верхнім»), нижня — E3 теж:
       фіолет низу вже несе E2, дублювати його смугою означало б перепал. */
    const hb = dark ? S.bgH3D : S.bgH3L;
    L.unshift(`radial-gradient(ellipse ${wd}% ${ht}px at 50% calc(100% - ${S.haYB}px), `
      + `${hsl(hb, sa, lt, ha)} 0, transparent 60%)`);
    L.unshift(`radial-gradient(ellipse ${wd}% ${ht}px at 50% ${S.haY}px, `
      + `${hsl(hb, sa, lt, ha)} 0, transparent 60%)`);
  }
  /* Нахил — окремий носій: не пляма, а перепад яскравості по всій площі.
     Останнім шаром, бо він найглибший (перший шар малюється зверху). */
  const t = (dark ? S.bgTiltD : S.bgTiltL) / 100;
  if (t > 0) L.push(`linear-gradient(170deg,rgba(255,255,255,${t.toFixed(3)}) 0%,`
    + `rgba(255,255,255,0) 55%,rgba(0,0,0,${t.toFixed(3)}) 100%)`);
  return L.join(',');
}
/* Полотно і палітра — гілка «ґрунт» applyVars стенда рядками (тема — системна, не themeMode стенда). Світла — константи
   CSS (src/css/tokens.css): removeProperty списку grd знімає те, що написала темна, — без нього перемикання теми наживо
   лишило б темні змінні в світлій (детектор: build_smoke.js «перемикання», --inject викидає цей рядок). Пропущено рядки
   змінних поза продуктом (--sheet · --well · --accent-soft — класифікатор build_smoke.js); --well-bg — з S39 (wMix — «живий без
   вироку» valuesLOCK §2). Аврора — у --bg-aur, removeProperty замість порожнього (стенд, коментар v17 · К1). */
const DARK = matchMedia('(prefers-color-scheme: dark)');
function applyTokens(){
  const dark = DARK.matches, s = document.documentElement.style;
  const grd = ['--canvas','--surface','--raised','--ink','--ink-2','--ink-3','--glass','--glass-rim','--line'];
  if (dark){
    const H = S.dkH, C = S.dkC, L = S.dkL, sL = L + S.dkS, rL = L + S.dkR;
    s.setProperty('--canvas',  hsl(H, C, L));
    s.setProperty('--surface', hsl(H, C*0.92, sL));
    s.setProperty('--raised',  hsl(H, C*0.85, rL));
    s.setProperty('--ink',     hsl(H, S.dkI, S.valL));
    s.setProperty('--ink-2',   hsl(H, S.dkI*0.8, S.mutL));
    s.setProperty('--ink-3',   hsl(H, S.dkI*0.7, S.mutL - 19));
    s.setProperty('--glass',   hsl(H, C*0.92, sL, .8));
    s.setProperty('--glass-rim', 'rgba(255,255,255,.11)');
    s.setProperty('--line',    'rgba(255,255,255,.075)');
    s.setProperty('--well-bg', hsl(H, C*0.92, sL - (sL - L) * S.wMixD/100));
    /* акцент темної теми — керований, а не зашитий (знахідка «вицвіле») */
    s.setProperty('--accent',      hsl(S.aH, S.aS, S.aL));
    s.setProperty('--accent-ink',  S.aL > 56 ? hsl(S.aH, 55, 10) : '#FFFFFF');
  } else {
    grd.forEach(k => s.removeProperty(k));
    /* v11 · акцент світлої тепер теж керований (був прибитий у :root) */
    s.setProperty('--accent',      hsl(S.aHL, S.aSL, S.aLL));
    s.setProperty('--accent-ink',  S.aLL > 56 ? hsl(S.aHL, 55, 10) : '#FFFFFF');
    s.setProperty('--well-bg', mixHex('#FFFFFF', '#EFEFF3', S.wMixL/100));
  }
  const aur = aurLayers(dark);
  if (aur) s.setProperty('--bg-aur', aur); else s.removeProperty('--bg-aur');
  /* К22-а · картка — стенд :2569–2610 рядками (коментарі стенда скорочено до суті; повні — у стенді) */
  s.setProperty('--cdGap',  S.cdGap+'px');
  s.setProperty('--cdR',    S.cdR+'px');
  s.setProperty('--cdPadX', S.cdPadX+'px');
  s.setProperty('--cdRimW', (S.cdRimW/10).toFixed(1)+'px');
  s.setProperty('--cdBevW', (S.cdBevW/10).toFixed(1)+'px');
  s.setProperty('--cdBody', dark ? hsl(S.dkH,S.dkC*0.92,S.dkL+S.dkS,(S.cdAD/100).toFixed(3))
                                 : hexA('#FFFFFF',S.cdAL/100));
  /* К22-б · фарба краю: полярність — фізика, важіль дає силу; --cdSh на темній — 'none' безумовно (A45);
     --cdGlass = 'none' при cdBlur=0 — blur(0px) усе одно заводить шар */
  const cdInk='#12121C', cdLit='#FFFFFF', cdShd='#101018';
  s.setProperty('--cdRimC', dark ? hexA(cdLit,S.cdRimAD/100) : hexA(cdInk,S.cdRimAL/100));
  s.setProperty('--cdBevT', dark ? hexA(cdLit,S.cdBevTD/100) : hexA(cdLit,S.cdBevTL/100));
  s.setProperty('--cdBevB', dark ? hexA(cdInk,S.cdBevBD/100) : hexA(cdInk,S.cdBevBL/100));
  s.setProperty('--cdBevS', dark ? hexA(cdLit,S.cdBevSD/100) : hexA(cdInk,S.cdBevSL/100));
  s.setProperty('--cdSh',   dark ? 'none'
    : '0 '+S.cdShY+'px '+S.cdShB+'px '+hexA(cdShd,S.cdShA/100));
  s.setProperty('--cdGlass', S.cdBlur>0 ? 'blur('+S.cdBlur+'px) saturate('+S.cdSat+'%)' : 'none');
  /* К22-в · glift і ridge: друга зупинка — альфа 0, НІКОЛИ transparent (sRGB тягне середину в сірий);
     альфа 0 → 'none' (шар з нульовою альфою все одно заводить композит); на світлій — 'none' (A45) */
  s.setProperty('--cdRidge', (dark && S.cdRdgAD>0)
    ? 'linear-gradient(180deg,'
      + hexA(cdLit,S.cdRdgAD/100) + ' 0,'
      + hexA(cdLit,0) + ' ' + S.cdRdgH + 'px)'
    : 'none');
  const cdGliftL = S.dkL + S.dkS + S.cdGliftD;
  s.setProperty('--cdGlift', (dark && S.cdGliftAD>0)
    ? 'linear-gradient(180deg,'
      + hsl(S.dkH,S.dkC*0.92,cdGliftL,(S.cdGliftAD/100).toFixed(3)) + ' 0%,'
      + hsl(S.dkH,S.dkC*0.92,cdGliftL,0) + ' ' + S.cdGliftHD + '%)'
    : 'none');
  s.setProperty('--aSize', S.aSize+'px'); s.setProperty('--mtSize', S.mtSize+'px');
  s.setProperty('--rowPadY', S.rowPadY+'px'); s.setProperty('--headGap', S.headGap+'px');
  const a = dark ? [S.aH, S.aS, S.aL] : [S.aHL, S.aSL, S.aLL];
  s.setProperty('--gang', S.gAng+'deg');
  s.setProperty('--g1', hsl(a[0], a[1], a[2]));
  s.setProperty('--g2', hsl((a[0] + S.gShift + 360) % 360, a[1], a[2]));
}
applyTokens();
DARK.addEventListener('change', applyTokens);
