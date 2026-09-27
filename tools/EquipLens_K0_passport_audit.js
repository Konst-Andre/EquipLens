/* живе доки: паспорт стенда не переїхав у білд b1 (Ф3) — далі детектор або
   переїжджає разом із паспортом, або гине разом зі стендом.
   EquipLens · К0 · аудит паспорта (самері S17 §4).
   Питання, на які відповідає:
     1. чи однаковий склад ЖИВІ в 4 станах пікера/теми;
     2. чи потрапляє КОЖЕН важіль стенда хоч в один стан (втрата на порті);
     3. чи бреше рядок «CSS-СЕКЦІЯ НЕ ПОКРИВАЄ».
   Керування — КЛІКОМ по реальних кнопках, не присвоєнням S: інакше судимо
   не той шлях, яким ходить оператор (пікер існує в розмітці ≠ pick() його знає).
   Запуск: node EquipLens_K0_passport_audit.js   (поруч EquipLens_headbench_v17.html) */
const {JSDOM} = require('jsdom'), fs = require('fs');
const html = fs.readFileSync('EquipLens_headbench_v17.html', 'utf8');

const dom = new JSDOM(html, {runScripts:'dangerously', pretendToBeVisual:true,
  url:'https://konst-andre.github.io/',
  beforeParse(w){
    w.matchMedia = () => ({matches:false, addEventListener(){}, addListener(){}});
    w.confirm = () => true; w.alert = () => {};
    w.navigator.clipboard = undefined;
  }});
const W = dom.window, D = W.document;

/* --- клік по кнопці сегмента/пікера за data-v --- */
function press(boxId, v){
  const box = D.getElementById(boxId);
  if (!box) throw new Error('немає ' + boxId);
  const b = box.querySelector(`button[data-v="${v}"]`);
  if (!b) throw new Error(`немає ${boxId} [data-v=${v}]`);
  b.dispatchEvent(new W.Event('click', {bubbles:true}));
}

/* --- зняти паспорт у поточному стані --- */
function passport(){
  D.getElementById('copyBtn').dispatchEvent(new W.Event('click', {bubbles:true}));
  return D.getElementById('out').value;
}
const line = (txt, re) => (txt.match(re) || [,''])[1].trim();
function liveKeys(txt){
  const m = txt.match(/ЖИВІ = (\{[\s\S]*?\})\nверхня зона/);
  return m ? Object.keys(JSON.parse(m[1])) : null;
}

const STATES = [
  {id:'sheet · світла',  bg:'sheet',  th:'light'},
  {id:'sheet · темна',   bg:'sheet',  th:'dark'},
  {id:'chrome · світла', bg:'chrome', th:'light'},
  {id:'chrome · темна',  bg:'chrome', th:'dark'},
];

const res = [];
for (const st of STATES){
  press('pkBg', st.bg);
  press('segTheme', st.th);
  const txt = passport();
  res.push({
    ...st,
    live: liveKeys(txt),
    dead: line(txt, /мертві важелі ВИКЛЮЧЕНО: (.*)/),
    gapN: +(line(txt, /CSS-СЕКЦІЯ НЕ ПОКРИВАЄ (\d+) живих/) || 0),
    gap:  line(txt, /CSS-СЕКЦІЯ НЕ ПОКРИВАЄ \d+ живих важелів: (.*)/),
    tdead:line(txt, /⚠ НЕ СУДИЛОСЬ НА ЦІЙ ТЕМІ[^:]*: (.*)/),
    cssHasAur: /background-image:/.test(txt),
  });
}

const allKeys = Object.keys(W.S).sort();
const union = new Set(); res.forEach(r => r.live.forEach(k => union.add(k)));
const never = allKeys.filter(k => !union.has(k));

console.log('=== К0 · АУДИТ ПАСПОРТА · стенд v17_2 ===');
console.log(`важелів у S: ${allKeys.length} · кнопок [data-k]/[data-dk]: ` +
            D.querySelectorAll('[data-k],[data-dk]').length);
console.log('\n--- склад ЖИВІ по станах ---');
res.forEach(r => console.log(
  `${r.id.padEnd(16)} живих ${String(r.live.length).padStart(3)} · ` +
  `непокриття ${String(r.gapN).padStart(2)} · фон у CSS: ${r.cssHasAur ? 'є' : 'нема'}`));

console.log('\n--- п.2 К0: контрольні набори ---');
const CHECK = {
  'ґрунт темної': ['dkH','dkC','dkL','dkS','dkR','dkI'],
  'аврора · св.': ['bgA1L','bgA2L','bgA3L','bgTiltL','bgLtL','bgSatL'],
  'аврора · тем.': ['bgA1D','bgA2D','bgA3D','bgTiltD','bgLtD','bgSatD'],
  'аврора · спільні': ['bgH1','bgH2','bgH3','bgSpread'],
};
for (const [nm, keys] of Object.entries(CHECK)){
  const miss = keys.filter(k => !union.has(k));
  const where = keys.map(k => res.filter(r => r.live.includes(k)).map(r => r.id).join(' + '));
  console.log(`${miss.length ? '✗' : '✓'} ${nm.padEnd(18)} ${miss.length ? 'НЕ ПОТРАПИЛИ: ' + miss : 'усі є · стани: ' + (where[0] || '—')}`);
}

console.log('\n--- п.2 К0: важелі, що НЕ ПОТРАПИЛИ В ЖОДЕН стан ---');
console.log(never.length ? never.join(', ') : '— немає, усі 4 стани разом накривають S');

console.log('\n--- п.3 К0: рядок непокриття, склад ---');
res.forEach(r => { if (r.gapN) console.log(`${r.id}: ${r.gap}`); });

console.log('\n--- контр-проба детектора (З-10: зсунути стан і вимагати зміни виходу) ---');
press('pkBg','sheet'); press('segTheme','light');
const a = liveKeys(passport()).length;
press('pkBg','chrome');
const b = liveKeys(passport()).length;
console.log(`sheet→chrome на світлій: ${a} → ${b} живих · ${b > a ? '✓ вихід змінився' : '✗ ДЕТЕКТОР СПИТЬ'}`);

console.log('\n--- рядок «НЕ СУДИЛОСЬ НА ЦІЙ ТЕМІ» ---');
res.forEach(r => console.log(`${r.id.padEnd(16)} ${r.tdead.slice(0,110)}`));
