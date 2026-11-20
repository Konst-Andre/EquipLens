/* живе доки: живе застосунок · вхід застосунку. Значення — JSON-блок #values (джерело — lens/EquipLens_head_valuesLOCK.md) */
const V = JSON.parse(document.getElementById('values').textContent);
document.documentElement.dataset.values = String(Object.keys(V).length);
/* iOS Safari: без слухача touchstart на документі :active на дотик не спрацьовує (ui_lint «натискання») */
document.addEventListener('touchstart', () => {}, { passive: true });
