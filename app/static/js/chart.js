/* ── TradingView Lightweight Charts wrapper ── */

let priceChart = null;
let areaSeries = null;
let volumeSeries = null;
let chartResizeObserver = null;

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

function initPriceChart(containerId) {
  destroyPriceChart();

  const container = document.getElementById(containerId);
  if (!container) return;
  container.innerHTML = '';

  const w = container.clientWidth || 600;
  const h = container.clientHeight || 320;

  priceChart = LightweightCharts.createChart(container, {
    width: w,
    height: h,
    layout: {
      background: { type: 'solid', color: '#0d1117' },
      textColor: '#8b949e',
      fontFamily: "'JetBrains Mono', monospace",
      fontSize: 11,
    },
    grid: {
      vertLines: { color: '#21262d' },
      horzLines: { color: '#21262d' },
    },
    crosshair: {
      mode: LightweightCharts.CrosshairMode.Normal,
      vertLine: { color: '#00bcd455', width: 1, style: 2 },
      horzLine: { color: '#00bcd455', width: 1, style: 2 },
    },
    rightPriceScale: {
      borderColor: '#30363d',
    },
    timeScale: {
      borderColor: '#30363d',
      timeVisible: false,
    },
    handleScroll: { vertTouchDrag: false },
  });

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

  const priceData = data.map(d => ({
    time: d.date,
    value: d.close,
  }));

  const volumeData = data.map(d => ({
    time: d.date,
    value: d.volume,
    color: d.close >= d.open ? '#2ea04366' : '#da363366',
  }));

  areaSeries.setData(priceData);
  volumeSeries.setData(volumeData);
  priceChart.timeScale().fitContent();
}
