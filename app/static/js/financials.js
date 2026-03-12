/* ── Chart.js bar charts for financials + ratio mini-charts ── */

let charts = {};

const CHART_COLORS = {
  bar: '#00bcd4',
  barBorder: '#00bcd4',
  positive: '#2ea043',
  negative: '#da3633',
};

function baseOpts(valueFmt) {
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: '#1c2128',
        borderColor: '#30363d',
        borderWidth: 1,
        titleFont: { family: "'JetBrains Mono', monospace", size: 10 },
        bodyFont: { family: "'JetBrains Mono', monospace", size: 10 },
        callbacks: { label: (ctx) => valueFmt(ctx.parsed.y) },
      },
    },
    scales: {
      x: {
        grid: { display: false },
        ticks: { color: '#484f58', font: { family: "'JetBrains Mono'", size: 9 }, maxRotation: 45 },
        border: { color: '#30363d' },
      },
      y: {
        grid: { color: '#21262d' },
        ticks: { color: '#484f58', font: { family: "'JetBrains Mono'", size: 9 }, callback: valueFmt },
        border: { display: false },
      },
    },
  };
}

function fmtLargeNum(v) {
  if (v == null) return '—';
  if (Math.abs(v) >= 1e9) return (v / 1e9).toFixed(1) + 'B';
  if (Math.abs(v) >= 1e6) return (v / 1e6).toFixed(0) + 'M';
  return v.toLocaleString();
}

function fmtPct(v) {
  if (v == null) return '—';
  return v.toFixed(1) + '%';
}

function fmtNum(v) {
  if (v == null) return '—';
  return Number(v).toFixed(2);
}

function makeBarChart(canvasId, labels, data, colorFn, valueFmt) {
  const el = document.getElementById(canvasId);
  if (!el) return;
  if (charts[canvasId]) charts[canvasId].destroy();

  const bg = data.map(v => colorFn ? colorFn(v) : CHART_COLORS.bar + '88');
  const border = data.map(v => colorFn ? colorFn(v).replace('88', '') : CHART_COLORS.bar);

  charts[canvasId] = new Chart(el, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        data,
        backgroundColor: bg,
        borderColor: border,
        borderWidth: 1,
        borderRadius: 2,
        maxBarThickness: 28,
      }],
    },
    options: baseOpts(valueFmt || fmtLargeNum),
  });
}

function signColor(v) {
  return v >= 0 ? CHART_COLORS.positive + '88' : CHART_COLORS.negative + '88';
}

function renderFinancials(financials, companyData) {
  if (!financials || !financials.length) return;

  const sorted = [...financials].sort((a, b) => a.year - b.year);
  const labels = sorted.map(f => String(f.year));

  // 1) Net Sales (revenue)
  makeBarChart('revenue-chart', labels,
    sorted.map(f => f.revenue),
    () => CHART_COLORS.bar + '88',
    fmtLargeNum
  );

  // 2) Revenue Growth (year-over-year %)
  const growthData = sorted.map((f, i) => {
    if (i === 0 || !sorted[i - 1].revenue || !f.revenue) return null;
    return ((f.revenue - sorted[i - 1].revenue) / Math.abs(sorted[i - 1].revenue)) * 100;
  });
  makeBarChart('growth-chart', labels,
    growthData,
    (v) => v != null ? signColor(v) : '#30363d88',
    fmtPct
  );

  // 3) Earnings per Share
  makeBarChart('eps-chart', labels,
    sorted.map(f => f.eps),
    (v) => v != null ? signColor(v) : '#30363d88',
    fmtNum
  );

  // 4) Profit Margin (%)
  makeBarChart('margin-chart', labels,
    sorted.map(f => f.profit_margin),
    (v) => v != null ? signColor(v) : '#30363d88',
    fmtPct
  );
}

/* ── Ratio mini-charts (P/E, P/S from annual data) ── */
function renderRatioCharts(financials, companyData) {
  if (!financials || !financials.length) return;

  const sorted = [...financials].sort((a, b) => a.year - b.year);
  const labels = sorted.map(f => String(f.year));

  // Add current value as latest bar if we have companyData
  const peData = sorted.map(f => {
    if (f.eps && f.eps !== 0 && f.revenue) {
      // We don't have historical PE directly, skip
      return null;
    }
    return null;
  });

  // For P/E mini-chart: use current PE as single value + label, or build from annual EPS+price
  // Since we only have current ratios, show them as a simple bar with the current value
  // alongside year-labels from financials
  const peLabels = [...labels];
  const peValues = sorted.map(() => null);

  // Add current as the latest
  if (companyData && companyData.pe != null) {
    peLabels.push('Now');
    peValues.push(companyData.pe);
  }

  // For annual approximation, compute P/E from EPS if we have price at year-end (we don't really)
  // Instead show the current pe as context on the mini chart, with financials years showing EPS-derived PE
  // Best effort: if we have eps, use current price / eps_that_year as rough historical PE
  if (companyData && companyData.price) {
    sorted.forEach((f, i) => {
      if (f.eps && f.eps > 0) {
        // This is a rough proxy—not historically accurate but directionally useful
        peValues[i] = null; // We'd need historical prices, skip for now
      }
    });
  }

  // Just show current P/E and P/S as single-value mini charts
  renderSingleRatio('ratio-pe-chart', 'P/E', companyData?.pe, financials, 'pe');
  renderSingleRatio('ratio-ps-chart', 'P/S', companyData?.ps, financials, 'ps');
}

function renderSingleRatio(canvasId, label, currentVal, financials, type) {
  const el = document.getElementById(canvasId);
  if (!el) return;
  if (charts[canvasId]) charts[canvasId].destroy();

  // Build labels from financials years + "Current"
  const sorted = [...financials].sort((a, b) => a.year - b.year);
  const labels = sorted.map(f => String(f.year));
  const values = sorted.map(f => {
    // Approximate: for P/S = revenue per share doesn't exist, so just show placeholders
    // We'll compute from annual data if possible
    if (type === 'pe' && f.eps && f.eps > 0 && f.revenue) {
      // Very rough: use net_income margin pattern—but we don't have historical prices
      return null;
    }
    return null;
  });

  // Add current
  labels.push('Curr');
  values.push(currentVal);

  // Filter out nulls for display, keep the ones we have
  const displayLabels = [];
  const displayValues = [];
  labels.forEach((l, i) => {
    if (values[i] != null) {
      displayLabels.push(l);
      displayValues.push(values[i]);
    }
  });

  if (!displayValues.length) return;

  charts[canvasId] = new Chart(el, {
    type: 'bar',
    data: {
      labels: displayLabels,
      datasets: [{
        data: displayValues,
        backgroundColor: CHART_COLORS.bar + '88',
        borderColor: CHART_COLORS.bar,
        borderWidth: 1,
        borderRadius: 2,
        maxBarThickness: 20,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#1c2128',
          borderColor: '#30363d',
          borderWidth: 1,
          bodyFont: { family: "'JetBrains Mono'", size: 10 },
        },
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { color: '#484f58', font: { family: "'JetBrains Mono'", size: 8 } },
          border: { display: false },
        },
        y: {
          grid: { color: '#21262d' },
          ticks: { color: '#484f58', font: { family: "'JetBrains Mono'", size: 8 } },
          border: { display: false },
        },
      },
    },
  });
}
