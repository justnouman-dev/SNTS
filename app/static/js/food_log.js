/* ============================================================
   SNTS — food_log.js
   Live search, quantity controls, nutrient preview
   ============================================================ */

let selectedFood = null;
let debounceTimer = null;

document.addEventListener('DOMContentLoaded', () => {

  /* ── Tab switching ──────────────────────────────────────── */
  document.querySelectorAll('.fl-tab').forEach(btn => {
    btn.addEventListener('click', () => {
      const target = btn.dataset.target;
      switchTab(target, btn);
    });
  });

  /* ── Search input ───────────────────────────────────────── */
  const searchInput = document.getElementById('searchInput');
  const clearBtn    = document.getElementById('clearSearch');
  const dropdown    = document.getElementById('flDropdown');

  if (searchInput) {
    searchInput.addEventListener('input', () => {
      const q = searchInput.value.trim();
      clearBtn && (clearBtn.style.display = q ? 'block' : 'none');
      clearTimeout(debounceTimer);
      if (q.length < 2) { closeDropdown(); return; }
      debounceTimer = setTimeout(() => fetchSearch(q), 280);
    });

    searchInput.addEventListener('focus', () => {
      if (searchInput.value.trim().length >= 2) fetchSearch(searchInput.value.trim());
    });
  }

  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      searchInput.value = '';
      clearBtn.style.display = 'none';
      closeDropdown();
      searchInput.focus();
    });
  }

  /* Close dropdown when clicking outside */
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.fl-search-wrap')) closeDropdown();
  });

  /* ── Quantity controls ──────────────────────────────────── */
  const qtyInput = document.getElementById('qty');
  if (qtyInput) {
    qtyInput.addEventListener('input', updatePreview);
  }

  document.querySelectorAll('.fl-quick-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      if (!qtyInput) return;
      qtyInput.value = btn.dataset.qty;
      updatePreview();
    });
  });

  const qtyMinus = document.getElementById('qtyMinus');
  const qtyPlus  = document.getElementById('qtyPlus');
  if (qtyMinus) qtyMinus.addEventListener('click', () => adjustQty(-10));
  if (qtyPlus)  qtyPlus.addEventListener('click',  () => adjustQty(+10));
});

/* ── Fetch search results ─────────────────────────────────── */
async function fetchSearch(q) {
  try {
    const res  = await fetch(`/utils/search-foods?q=${encodeURIComponent(q)}`);
    const data = await res.json();
    renderDropdown(data);
  } catch (err) {
    console.error('Search error:', err);
  }
}

/* ── Render dropdown ──────────────────────────────────────── */
function renderDropdown(foods) {
  const dropdown = document.getElementById('flDropdown');
  if (!dropdown) return;

  if (!foods.length) {
    dropdown.innerHTML = '<div style="padding:.75rem 1rem;color:var(--gray-500);font-size:.85rem;">No foods found</div>';
    dropdown.classList.add('open');
    return;
  }

  dropdown.innerHTML = foods.map(f => `
    <div class="fl-result" onclick="selectFood(${f.id},'${escStr(f.name)}',${f.calories},${f.protein},${f.carbs},${f.fats})">
      <span class="fl-result-name">${escStr(f.name)}</span>
      <span class="fl-result-macros">
        <span class="fl-m-cal">${f.calories}kcal</span>
        <span class="fl-m-pro">P${f.protein}g</span>
        <span class="fl-m-carb">C${f.carbs}g</span>
        <span class="fl-m-fat">F${f.fats}g</span>
      </span>
    </div>
  `).join('');
  dropdown.classList.add('open');
}

/* ── Select a food ────────────────────────────────────────── */
function selectFood(id, name, cal, pro, carb, fat) {
  selectedFood = { id, name, cal, pro, carb, fat };

  /* Fill hidden fields */
  document.getElementById('hiddenFoodId').value   = id;
  document.getElementById('hiddenFoodName').value = name;

  /* Show selected panel */
  const panel = document.getElementById('flSelected');
  if (panel) {
    panel.classList.add('visible');
    panel.querySelector('.fl-selected-name').textContent = name;
  }

  /* Reset qty to 100 */
  const qtyInput = document.getElementById('qty');
  if (qtyInput) { qtyInput.value = 100; updatePreview(); }

  /* Highlight browse row */
  document.querySelectorAll('.browse-row').forEach(row => {
    row.classList.toggle('table-active', +row.dataset.foodId === +id);
  });

  closeDropdown();
  panel && panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

/* ── Update nutrient preview ──────────────────────────────── */
function updatePreview() {
  if (!selectedFood) return;
  const qty    = parseFloat(document.getElementById('qty')?.value) || 100;
  const factor = qty / 100;

  setText('prevCal',  (selectedFood.cal  * factor).toFixed(1));
  setText('prevPro',  (selectedFood.pro  * factor).toFixed(1));
  setText('prevCarb', (selectedFood.carb * factor).toFixed(1));
  setText('prevFat',  (selectedFood.fat  * factor).toFixed(1));

  const qtyHidden = document.getElementById('hiddenQty');
  if (qtyHidden) qtyHidden.value = qty;
}

/* ── Adjust qty by delta ──────────────────────────────────── */
function adjustQty(delta) {
  const input = document.getElementById('qty');
  if (!input) return;
  let val = parseFloat(input.value) || 100;
  val = Math.max(1, Math.min(5000, val + delta));
  input.value = val;
  updatePreview();
}

/* ── Helpers ──────────────────────────────────────────────── */
function closeDropdown() {
  const d = document.getElementById('flDropdown');
  if (d) d.classList.remove('open');
}

function escStr(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/'/g, '&#39;')
    .replace(/"/g, '&quot;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

function setText(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}
