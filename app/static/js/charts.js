/* ============================================================
   SNTS — charts.js  (Chart.js bar + doughnut)
   ============================================================ */

let barChartInstance = null;
let pieChartInstance = null;

async function loadCharts(period) {
  try {
    const res  = await fetch(`/utils/chart-data?period=${period}`);
    const data = await res.json();
    renderBarChart(data.bar);
    renderPieChart(data.pie);
  } catch (err) {
    console.error('Chart load error:', err);
  }
}

/* ── Bar chart ─────────────────────────────────────────────── */
function renderBarChart(bar) {
  const ctx = document.getElementById('barChart');
  if (!ctx) return;

  if (barChartInstance) barChartInstance.destroy();

  const lastIdx   = bar.data.length - 1;
  const bgColors  = bar.data.map((_, i) =>
    i === lastIdx ? 'rgba(22,163,74,.9)' : 'rgba(22,163,74,.35)'
  );
  const bdrColors = bar.data.map((_, i) =>
    i === lastIdx ? 'rgba(21,128,61,1)' : 'rgba(22,163,74,.6)'
  );

  barChartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: bar.labels,
      datasets: [{
        label: 'Calories',
        data: bar.data,
        backgroundColor: bgColors,
        borderColor: bdrColors,
        borderWidth: 1.5,
        borderRadius: 5,
        borderSkipped: false,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => ` ${ctx.parsed.y.toLocaleString()} kcal`
          }
        }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { color: '#9ca3af', font: { size: 11 } }
        },
        y: {
          beginAtZero: true,
          grid: { color: '#f3f4f6' },
          ticks: {
            color: '#9ca3af', font: { size: 11 },
            callback: (v) => v >= 1000 ? `${(v/1000).toFixed(1)}k` : v
          }
        }
      }
    }
  });
}

/* ── Pie / doughnut chart ──────────────────────────────────── */
function renderPieChart(pie) {
  const ctx = document.getElementById('pieChart');
  if (!ctx) return;

  if (pieChartInstance) pieChartInstance.destroy();

  const total = pie.protein + pie.carbs + pie.fats;

  if (total === 0) {
    pieChartInstance = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['No data'],
        datasets: [{ data: [1], backgroundColor: ['#e5e7eb'], borderWidth: 0 }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: false },
          tooltip: { enabled: false }
        },
        cutout: '65%'
      }
    });
    return;
  }

  const pPct = Math.round(pie.protein / total * 100);
  const cPct = Math.round(pie.carbs   / total * 100);
  const fPct = 100 - pPct - cPct;

  pieChartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: [
        `Protein ${pPct}%`,
        `Carbs ${cPct}%`,
        `Fats ${fPct}%`
      ],
      datasets: [{
        data: [pie.protein, pie.carbs, pie.fats],
        backgroundColor: ['#3b82f6', '#f59e0b', '#8b5cf6'],
        borderColor:     ['#2563eb', '#d97706', '#7c3aed'],
        borderWidth: 2,
        hoverOffset: 6,
      }]
    },
    options: {
      responsive: true,
      cutout: '62%',
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            padding: 12,
            font: { size: 11 },
            color: '#6b7280',
            boxWidth: 12,
            boxHeight: 12,
          }
        },
        tooltip: {
          callbacks: {
            label: (ctx) => {
              const g   = ctx.parsed;
              const tot = ctx.dataset.data.reduce((a, b) => a + b, 0);
              const pct = tot > 0 ? Math.round(g / tot * 100) : 0;
              return ` ${ctx.label.split(' ')[0]}: ${g.toFixed(1)}g (${pct}%)`;
            }
          }
        }
      }
    }
  });
}
