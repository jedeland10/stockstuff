/* ── TradingView Lightweight Charts wrapper ── */

let priceChart = null;
let areaSeries = null;
let volumeSeries = null;
let chartResizeObserver = null;

// Technical chart
let techChart = null;
let candleSeries = null;
let techVolumeSeries = null;
let ma50Series = null;
let ma200Series = null;
let techResizeObserver = null;

const CHART_THEME = {
  background: '#0d1117',
  text: '#8b949e',
  grid: '#21262d',
  crosshair: '#00bcd455',
  border: '#30363d',
  font: "'JetBrains Mono', monospace",
};

function destroyPriceChart() {
  if (chartResizeObserver) {
    chartResizeObserver.disconnect();
    chartResizeObserver = null;
  }
  if (priceChart) {
    try { priceChart.remove(); } catch (e) {}
    priceChart = null;
    areaSeries = null;
    volumeSeries = null;
  }
}

function destroyTechChart() {
  if (techResizeObserver) {
    techResizeObserver.disconnect();
    techResizeObserver = null;
  }
  if (techChart) {
    try { techChart.remove(); } catch (e) {}
    techChart = null;
    candleSeries = null;
    techVolumeSeries = null;
    ma50Series = null;
    ma200Series = null;
  }
}

function createChart(container) {
  const w = container.clientWidth || 600;
  const h = container.clientHeight || 320;

  return LightweightCharts.createChart(container, {
    width: w,
    height: h,
    layout: {
      background: { type: 'solid', color: CHART_THEME.background },
      textColor: CHART_THEME.text,
      fontFamily: CHART_THEME.font,
      fontSize: 11,
    },
    grid: {
      vertLines: { color: CHART_THEME.grid },
      horzLines: { color: CHART_THEME.grid },
    },
    crosshair: {
      mode: LightweightCharts.CrosshairMode.Normal,
      vertLine: { color: CHART_THEME.crosshair, width: 1, style: 2 },
      horzLine: { color: CHART_THEME.crosshair, width: 1, style: 2 },
    },
    rightPriceScale: { borderColor: CHART_THEME.border },
    timeScale: { borderColor: CHART_THEME.border, timeVisible: false },
    handleScroll: { vertTouchDrag: false },
  });
}

function initPriceChart(containerId) {
  destroyPriceChart();

  const container = document.getElementById(containerId);
  if (!container) return;
  container.innerHTML = '';

  priceChart = createChart(container);

  areaSeries = priceChart.addAreaSeries({
    topColor: 'rgba(0, 188, 212, 0.3)',
    bottomColor: 'rgba(0, 188, 212, 0.02)',
    lineColor: '#00bcd4',
    lineWidth: 2,
  });

  volumeSeries = priceChart.addHistogramSeries({
    color: '#30363d',
    priceFormat: { type: 'volume' },
    priceScaleId: '',
  });

  volumeSeries.priceScale().applyOptions({
    scaleMargins: { top: 0.85, bottom: 0 },
  });

  chartResizeObserver = new ResizeObserver(() => {
    if (priceChart && container.clientWidth > 0 && container.clientHeight > 0) {
      priceChart.applyOptions({
        width: container.clientWidth,
        height: container.clientHeight,
      });
    }
  });
  chartResizeObserver.observe(container);
}

function updatePriceChart(data) {
  if (!areaSeries || !volumeSeries || !data || !data.length) return;

  const priceData = data.map(d => ({ time: d.date, value: d.close }));
  const volumeData = data.map(d => ({
    time: d.date,
    value: d.volume,
    color: d.close >= d.open ? '#2ea04366' : '#da363366',
  }));

  areaSeries.setData(priceData);
  volumeSeries.setData(volumeData);
  priceChart.timeScale().fitContent();
}

/* ── Technical Candlestick Chart ── */
function renderTechChart(data, ticker) {
  destroyTechChart();

  const container = document.getElementById('tech-chart');
  if (!container || !data || !data.length) return;
  container.innerHTML = '';

  techChart = createChart(container);

  candleSeries = techChart.addCandlestickSeries({
    upColor: '#2ea043',
    downColor: '#da3633',
    borderUpColor: '#2ea043',
    borderDownColor: '#da3633',
    wickUpColor: '#2ea04399',
    wickDownColor: '#da363399',
  });

  const candleData = data.map(d => ({
    time: d.date,
    open: d.open,
    high: d.high,
    low: d.low,
    close: d.close,
  }));
  candleSeries.setData(candleData);

  // Volume
  techVolumeSeries = techChart.addHistogramSeries({
    color: '#30363d',
    priceFormat: { type: 'volume' },
    priceScaleId: '',
  });
  techVolumeSeries.priceScale().applyOptions({
    scaleMargins: { top: 0.85, bottom: 0 },
  });
  techVolumeSeries.setData(data.map(d => ({
    time: d.date,
    value: d.volume,
    color: d.close >= d.open ? '#2ea04344' : '#da363344',
  })));

  // MA50
  const closes = data.map(d => d.close);
  const ma50 = computeMA(closes, 50);
  const ma200 = computeMA(closes, 200);

  if (ma50.filter(v => v !== null).length > 0) {
    ma50Series = techChart.addLineSeries({
      color: '#f0b90b',
      lineWidth: 1,
      priceLineVisible: false,
      lastValueVisible: false,
    });
    ma50Series.setData(data.map((d, i) => ({
      time: d.date,
      value: ma50[i],
    })).filter(d => d.value !== null));
  }

  if (ma200.filter(v => v !== null).length > 0) {
    ma200Series = techChart.addLineSeries({
      color: '#da3633',
      lineWidth: 1,
      priceLineVisible: false,
      lastValueVisible: false,
    });
    ma200Series.setData(data.map((d, i) => ({
      time: d.date,
      value: ma200[i],
    })).filter(d => d.value !== null));
  }

  techChart.timeScale().fitContent();

  techResizeObserver = new ResizeObserver(() => {
    if (techChart && container.clientWidth > 0 && container.clientHeight > 0) {
      techChart.applyOptions({
        width: container.clientWidth,
        height: container.clientHeight,
      });
    }
  });
  techResizeObserver.observe(container);
}

/* ── Technical Indicators ── */
function renderTechIndicators(data) {
  const container = document.getElementById('tech-indicators');
  if (!container || !data || !data.length) return;

  const closes = data.map(d => d.close);
  const volumes = data.map(d => d.volume);
  const last = closes[closes.length - 1];

  const ma50 = computeMA(closes, 50);
  const ma200 = computeMA(closes, 200);
  const rsi = computeRSI(closes, 14);
  const lastMA50 = ma50.filter(v => v !== null).slice(-1)[0];
  const lastMA200 = ma200.filter(v => v !== null).slice(-1)[0];
  const lastRSI = rsi.filter(v => v !== null).slice(-1)[0];

  // Volatility (20-day std dev of returns)
  const returns20 = closes.slice(-21).map((c, i, arr) => i > 0 ? (c - arr[i-1]) / arr[i-1] : null).filter(v => v !== null);
  const vol20 = returns20.length > 1 ? Math.sqrt(returns20.reduce((s, r) => s + r * r, 0) / returns20.length) * Math.sqrt(252) * 100 : null;

  // Average volume 20d
  const avgVol20 = volumes.slice(-20).reduce((s, v) => s + v, 0) / Math.min(20, volumes.length);

  const fmtVal = (v, dec = 2) => v != null ? Number(v).toFixed(dec) : '—';
  const fmtPctVal = (v) => v != null ? (v >= 0 ? '+' : '') + v.toFixed(1) + '%' : '—';
  const pctClass = (v) => v >= 0 ? 'text-positive' : 'text-negative';

  // Price vs MA
  const vsMa50 = lastMA50 ? ((last - lastMA50) / lastMA50 * 100) : null;
  const vsMa200 = lastMA200 ? ((last - lastMA200) / lastMA200 * 100) : null;

  container.innerHTML = `
    <div class="tech-stat">
      <div class="tech-stat-label">Price</div>
      <div class="tech-stat-value">${fmtVal(last)}</div>
    </div>
    <div class="tech-stat">
      <div class="tech-stat-label">MA 50</div>
      <div class="tech-stat-value">${fmtVal(lastMA50)}</div>
    </div>
    <div class="tech-stat">
      <div class="tech-stat-label">MA 200</div>
      <div class="tech-stat-value">${fmtVal(lastMA200)}</div>
    </div>
    <div class="tech-stat">
      <div class="tech-stat-label">Price/MA50</div>
      <div class="tech-stat-value ${vsMa50 != null ? pctClass(vsMa50) : ''}">${fmtPctVal(vsMa50)}</div>
    </div>
    <div class="tech-stat">
      <div class="tech-stat-label">Price/MA200</div>
      <div class="tech-stat-value ${vsMa200 != null ? pctClass(vsMa200) : ''}">${fmtPctVal(vsMa200)}</div>
    </div>
    <div class="tech-stat">
      <div class="tech-stat-label">RSI(14)</div>
      <div class="tech-stat-value" style="color: ${lastRSI > 70 ? 'var(--negative)' : lastRSI < 30 ? 'var(--positive)' : 'var(--text)'}">${fmtVal(lastRSI, 1)}</div>
    </div>
    <div class="tech-stat">
      <div class="tech-stat-label">Volatility</div>
      <div class="tech-stat-value">${vol20 != null ? vol20.toFixed(1) + '%' : '—'}</div>
    </div>
    <div class="tech-stat">
      <div class="tech-stat-label">Avg Vol 20d</div>
      <div class="tech-stat-value">${avgVol20 > 1e6 ? (avgVol20/1e6).toFixed(1) + 'M' : Math.round(avgVol20).toLocaleString()}</div>
    </div>
    <div class="tech-stat">
      <div class="tech-stat-label">MA50/MA200</div>
      <div class="tech-stat-value" style="color: ${lastMA50 > lastMA200 ? 'var(--positive)' : 'var(--negative)'}">
        ${lastMA50 && lastMA200 ? (lastMA50 > lastMA200 ? 'Golden' : 'Death') : '—'}
      </div>
    </div>
  `;
}

/* ── Performance Row ── */
function renderPerfRow(data) {
  const container = document.getElementById('perf-row');
  if (!container || !data || !data.length) return;

  const closes = data.map(d => d.close);
  const last = closes[closes.length - 1];

  const periods = [
    { label: '1d', days: 1 },
    { label: '1w', days: 5 },
    { label: '1m', days: 21 },
    { label: '3m', days: 63 },
    { label: '6m', days: 126 },
    { label: '1y', days: 252 },
    { label: 'YTD', days: null },
  ];

  let html = '';
  for (const p of periods) {
    let perf = null;
    if (p.label === 'YTD') {
      // Find first trading day of current year
      const currentYear = new Date().getFullYear();
      const ytdStart = data.find(d => d.date.startsWith(String(currentYear)));
      if (ytdStart) {
        perf = ((last - ytdStart.close) / ytdStart.close) * 100;
      }
    } else if (closes.length > p.days) {
      const ref = closes[closes.length - 1 - p.days];
      if (ref) perf = ((last - ref) / ref) * 100;
    }

    const cls = perf != null ? (perf >= 0 ? 'text-positive' : 'text-negative') : '';
    const val = perf != null ? (perf >= 0 ? '+' : '') + perf.toFixed(1) + '%' : '—';

    html += `<div class="perf-item">
      <span class="perf-label">${p.label}</span>
      <span class="perf-value ${cls}">${val}</span>
    </div>`;
  }
  container.innerHTML = html;
}

/* ── Helpers ── */
function computeMA(data, period) {
  const result = [];
  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) {
      result.push(null);
    } else {
      let sum = 0;
      for (let j = 0; j < period; j++) {
        sum += data[i - j];
      }
      result.push(sum / period);
    }
  }
  return result;
}

function computeRSI(closes, period) {
  const result = new Array(closes.length).fill(null);
  if (closes.length < period + 1) return result;

  let avgGain = 0;
  let avgLoss = 0;

  for (let i = 1; i <= period; i++) {
    const change = closes[i] - closes[i - 1];
    if (change >= 0) avgGain += change;
    else avgLoss += Math.abs(change);
  }

  avgGain /= period;
  avgLoss /= period;

  if (avgLoss === 0) {
    result[period] = 100;
  } else {
    result[period] = 100 - (100 / (1 + avgGain / avgLoss));
  }

  for (let i = period + 1; i < closes.length; i++) {
    const change = closes[i] - closes[i - 1];
    const gain = change >= 0 ? change : 0;
    const loss = change < 0 ? Math.abs(change) : 0;

    avgGain = (avgGain * (period - 1) + gain) / period;
    avgLoss = (avgLoss * (period - 1) + loss) / period;

    if (avgLoss === 0) {
      result[i] = 100;
    } else {
      result[i] = 100 - (100 / (1 + avgGain / avgLoss));
    }
  }

  return result;
}
