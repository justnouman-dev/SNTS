/* ============================================================
   SNTS — main.js  (global utilities)
   ============================================================ */

/* ── Mobile navbar toggle ─────────────────────────────────── */
(function () {
  const toggle = document.getElementById('navToggle');
  const links  = document.getElementById('navLinks');
  if (!toggle || !links) return;

  toggle.addEventListener('click', () => {
    links.classList.toggle('open');
    const icon = toggle.querySelector('i');
    if (icon) {
      icon.classList.toggle('fa-bars');
      icon.classList.toggle('fa-xmark');
    }
  });

  document.addEventListener('click', (e) => {
    if (!toggle.contains(e.target) && !links.contains(e.target)) {
      links.classList.remove('open');
      const icon = toggle.querySelector('i');
      if (icon) { icon.classList.add('fa-bars'); icon.classList.remove('fa-xmark'); }
    }
  });
})();

/* ── Password visibility toggle ──────────────────────────── */
function togglePw(inputId, btnEl) {
  const inp = document.getElementById(inputId);
  if (!inp) return;
  const isHidden = inp.type === 'password';
  inp.type = isHidden ? 'text' : 'password';
  const icon = btnEl.querySelector('i');
  if (icon) {
    icon.classList.toggle('fa-eye',        !isHidden);
    icon.classList.toggle('fa-eye-slash',   isHidden);
  }
}

/* ── Flash auto-dismiss ───────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.flash').forEach((el) => {
    setTimeout(() => {
      el.style.transition = 'opacity .4s, transform .4s';
      el.style.opacity = '0';
      el.style.transform = 'translateY(-8px)';
      setTimeout(() => el.remove(), 400);
    }, 4000);
  });
});

/* ── Tab switcher (generic) ───────────────────────────────── */
function switchTab(tabId, btn) {
  // Determine the container from the clicked button
  const container = btn ? btn.closest('[data-tabs]') || btn.parentElement.parentElement : document;

  // Hide all panes & deactivate all buttons inside this container
  container.querySelectorAll('.fl-pane').forEach(p  => p.classList.remove('active'));
  container.querySelectorAll('.fl-tab').forEach(b   => b.classList.remove('active'));

  const pane = document.getElementById(tabId);
  if (pane) pane.classList.add('active');
  if (btn)  btn.classList.add('active');
}
