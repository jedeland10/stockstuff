/* ── Chart.js bar charts for all financial views ── */

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

function computeGrowth(data, field) {
  return data.map((item, i) => {
    if (i === 0) return null;
    const prev = data[i - 1][field];
    const curr = item[field];
    if (!prev || !curr || prev === 0) return null;
    return ((curr - prev) / Math.abs(prev)) * 100;
  });
}

/* ── Overview Tab financials (existing) ── */
function renderFinancials(financials, companyData) {
  if (!financials || !financials.length) return;

  const sorted = [...financials].sort((a, b) => a.year - b.year);
  const labels = sorted.map(f => String(f.year));

  makeBarChart('revenue-chart', labels,
    sorted.map(f => f.revenue),
    () => CHART_COLORS.bar + '88',
    fmtLargeNum
  );

  const growthData = computeGrowth(sorted, 'revenue');
  makeBarChart('growth-chart', labels,
    growthData,
    (v) => v != null ? signColor(v) : '#30363d88',
    fmtPct
  );

  makeBarChart('eps-chart', labels,
    sorted.map(f => f.eps),
    (v) => v != null ? signColor(v) : '#30363d88',
    fmtNum
  );

  makeBarChart('margin-chart', labels,
    sorted.map(f => f.profit_margin),
    (v) => v != null ? signColor(v) : '#30363d88',
    fmtPct
  );
}

/* ── Ratio mini-charts ── */
function renderRatioCharts(financials, companyData) {
  if (!financials || !financials.length) return;
  renderSingleRatio('ratio-pe-chart', 'P/E', companyData?.pe, financials, 'pe');
  renderSingleRatio('ratio-ps-chart', 'P/S', companyData?.ps, financials, 'ps');
}

function renderSingleRatio(canvasId, label, currentVal, financials, type) {
  const el = document.getElementById(canvasId);
  if (!el) return;
  if (charts[canvasId]) charts[canvasId].destroy();

  const displayLabels = ['Curr'];
  const displayValues = [currentVal];

  if (!displayValues.filter(v => v != null).length) return;

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

/* ── Report Tab ── */
function renderReportTab(cd) {
  if (!cd) return;

  // Annual financials
  const fin = cd.financials ? [...cd.financials].sort((a, b) => a.year - b.year) : [];
  const labels = fin.map(f => String(f.year));

  if (fin.length) {
    makeBarChart('rpt-revenue', labels, fin.map(f => f.revenue), () => CHART_COLORS.bar + '88', fmtLargeNum);
    makeBarChart('rpt-opinc', labels, fin.map(f => f.operating_income), v => v != null ? signColor(v) : '#30363d88', fmtLargeNum);
    makeBarChart('rpt-ebitda', labels, fin.map(f => f.ebitda), () => CHART_COLORS.bar + '88', fmtLargeNum);
    makeBarChart('rpt-netinc', labels, fin.map(f => f.net_income), v => v != null ? signColor(v) : '#30363d88', fmtLargeNum);
    makeBarChart('rpt-eps', labels, fin.map(f => f.eps), v => v != null ? signColor(v) : '#30363d88', fmtNum);
    makeBarChart('rpt-margin', labels, fin.map(f => f.profit_margin), v => v != null ? signColor(v) : '#30363d88', fmtPct);

    // Growth rates
    makeBarChart('rpt-revgrowth', labels, computeGrowth(fin, 'revenue'), v => v != null ? signColor(v) : '#30363d88', fmtPct);
    makeBarChart('rpt-opincgrowth', labels, computeGrowth(fin, 'operating_income'), v => v != null ? signColor(v) : '#30363d88', fmtPct);
    makeBarChart('rpt-earngrowth', labels, computeGrowth(fin, 'net_income'), v => v != null ? signColor(v) : '#30363d88', fmtPct);
    makeBarChart('rpt-margtrend', labels, fin.map(f => f.profit_margin), v => v != null ? signColor(v) : '#30363d88', fmtPct);
  }

  // Quarterly
  const qfin = cd.quarterly_financials ? [...cd.quarterly_financials].sort((a, b) => a.period.localeCompare(b.period)) : [];
  if (qfin.length) {
    const qlabels = qfin.map(q => q.period);
    makeBarChart('rpt-qrev', qlabels, qfin.map(q => q.revenue), () => CHART_COLORS.bar + '88', fmtLargeNum);
    makeBarChart('rpt-qopinc', qlabels, qfin.map(q => q.operating_income), v => v != null ? signColor(v) : '#30363d88', fmtLargeNum);
    makeBarChart('rpt-qnetinc', qlabels, qfin.map(q => q.net_income), v => v != null ? signColor(v) : '#30363d88', fmtLargeNum);
    makeBarChart('rpt-qmargin', qlabels, qfin.map(q => q.profit_margin), v => v != null ? signColor(v) : '#30363d88', fmtPct);
  }
}

/* ── Key Numbers Tab ── */
function renderKeyNumbersTab(cd) {
  if (!cd) return;

  // Balance sheet
  const bs = cd.balance_sheet ? [...cd.balance_sheet].sort((a, b) => a.year - b.year) : [];
  if (bs.length) {
    const bsLabels = bs.map(b => String(b.year));
    makeBarChart('kn-assets', bsLabels, bs.map(b => b.total_assets), () => CHART_COLORS.bar + '88', fmtLargeNum);
    makeBarChart('kn-equity', bsLabels, bs.map(b => b.total_equity), () => CHART_COLORS.bar + '88', fmtLargeNum);

    // Equity ratio = equity / total_assets * 100
    const eqRatio = bs.map(b => {
      if (b.total_equity && b.total_assets && b.total_assets !== 0) {
        return (b.total_equity / b.total_assets) * 100;
      }
      return null;
    });
    makeBarChart('kn-eqratio', bsLabels, eqRatio, v => v != null ? signColor(v) : '#30363d88', fmtPct);

    makeBarChart('kn-netdebt', bsLabels, bs.map(b => b.net_debt), v => v != null ? signColor(v) : '#30363d88', fmtLargeNum);
    makeBarChart('kn-cash', bsLabels, bs.map(b => b.cash), () => CHART_COLORS.positive + '88', fmtLargeNum);
    makeBarChart('kn-intangible', bsLabels, bs.map(b => b.intangible_assets), () => '#d4a01788', fmtLargeNum);
  }

  // Cash flow
  const cf = cd.cashflow ? [...cd.cashflow].sort((a, b) => a.year - b.year) : [];
  if (cf.length) {
    const cfLabels = cf.map(c => String(c.year));
    makeBarChart('kn-ocf', cfLabels, cf.map(c => c.operating_cf), v => v != null ? signColor(v) : '#30363d88', fmtLargeNum);
    makeBarChart('kn-capex', cfLabels, cf.map(c => c.capex), () => CHART_COLORS.negative + '88', fmtLargeNum);
    makeBarChart('kn-fcf', cfLabels, cf.map(c => c.free_cf), v => v != null ? signColor(v) : '#30363d88', fmtLargeNum);

    // Earnings/FCF ratio
    const fin = cd.financials ? [...cd.financials].sort((a, b) => a.year - b.year) : [];
    const earnFcf = cf.map((c, i) => {
      const matchFin = fin.find(f => f.year === c.year);
      if (matchFin && matchFin.net_income && c.free_cf && c.free_cf !== 0) {
        return (matchFin.net_income / c.free_cf) * 100;
      }
      return null;
    });
    makeBarChart('kn-earnfcf', cfLabels, earnFcf, v => v != null ? signColor(v) : '#30363d88', fmtPct);
  }
}
