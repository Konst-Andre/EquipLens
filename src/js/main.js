/* живе доки: живе застосунок · вхід застосунку. Значення — V з js/tokens.js (JSON-блок #values у <head>; джерело — lens/EquipLens_head_valuesLOCK.md) */
document.documentElement.dataset.values = String(Object.keys(V).length);
/* iOS Safari: без слухача touchstart на документі :active на дотик не спрацьовує (ui_lint «натискання») */
document.addEventListener('touchstart', () => {}, { passive: true });
