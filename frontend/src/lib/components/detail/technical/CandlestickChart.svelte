<script lang="ts">
  import { onDestroy, tick } from 'svelte';
  import { computeMA } from '$lib/utils/technicals';
  import type { PricePoint } from '$lib/api/types';
  import { cssVar, theme } from '$lib/stores/theme';

  let { data, ticker, period = 'max' }: { data: PricePoint[]; ticker: string; period?: string } = $props();

  let container: HTMLDivElement;
  let chart: any = null;
  let prevTicker = '';

  const PERIOD_DAYS: Record<string, number> = {
    '1m': 30, '3m': 90, '6m': 180, '1y': 365,
    '2y': 730, '5y': 1825, '10y': 3650, 'max': 99999,
  };
  let observer: ResizeObserver | null = null;
  let LW: any = null;

  function destroyChart() {
    observer?.disconnect();
    observer = null;
    if (chart) { try { chart.remove(); } catch {} }
    chart = null;
  }

  async function createAndApply() {
    if (!container || !data.length) return;
    if (!LW) LW = await import('lightweight-charts');

    destroyChart();

    await tick();
    await new Promise(r => requestAnimationFrame(r));
    await new Promise(r => requestAnimationFrame(r));

    const w = container.clientWidth;
    const h = container.clientHeight;
    if (w < 50 || h < 50) {
      await new Promise(r => setTimeout(r, 200));
      if (container.clientWidth < 50) return;
    }

    const bg = cssVar('--bg');
    const textMuted = cssVar('--text-muted');
    const grid = cssVar('--chart-grid');
    const border = cssVar('--border');
    const pos = cssVar('--positive');
    const neg = cssVar('--negative');
    const volume = cssVar('--chart-volume');

    chart = LW.createChart(container, {
      width: container.clientWidth,
      height: container.clientHeight,
      watermark: { visible: false },
      layout: {
        background: { type: 'solid', color: bg },
        textColor: textMuted,
        fontFamily: "'JetBrains Mono', monospace",
        fontSize: 10,
      },
      grid: { vertLines: { color: grid }, horzLines: { color: grid } },
      crosshair: { mode: LW.CrosshairMode.Normal },
      rightPriceScale: { borderColor: border },
      timeScale: { borderColor: border, timeVisible: false },
    });

    const candles = chart.addCandlestickSeries({
      upColor: pos, downColor: neg,
      borderUpColor: pos, borderDownColor: neg,
      wickUpColor: pos + '99', wickDownColor: neg + '99',
    });
    candles.setData(data.map(d => ({ time: d.date, open: d.open!, high: d.high!, low: d.low!, close: d.close! })));

    const vol = chart.addHistogramSeries({ color: volume, priceFormat: { type: 'volume' }, priceScaleId: '' });
    vol.priceScale().applyOptions({ scaleMargins: { top: 0.85, bottom: 0 } });
    vol.setData(data.map(d => ({
      time: d.date, value: d.volume ?? 0,
      color: (d.close ?? 0) >= (d.open ?? 0) ? pos + '33' : neg + '33',
    })));

    const closes = data.map(d => d.close ?? 0);
    const ma50 = computeMA(closes, 50);
    const ma200 = computeMA(closes, 200);

    if (ma50.some(v => v !== null)) {
      const s = chart.addLineSeries({ color: '#f0b90b', lineWidth: 1, priceLineVisible: false, lastValueVisible: false });
      s.setData(data.map((d, i) => ({ time: d.date, value: ma50[i]! })).filter((d: any) => d.value != null));
    }
    if (ma200.some(v => v !== null)) {
      const s = chart.addLineSeries({ color: '#da3633', lineWidth: 1, priceLineVisible: false, lastValueVisible: false });
      s.setData(data.map((d, i) => ({ time: d.date, value: ma200[i]! })).filter((d: any) => d.value != null));
    }

    setVisibleRange();

    observer = new ResizeObserver(() => {
      if (chart && container.clientWidth > 0 && container.clientHeight > 0) {
        chart.applyOptions({ width: container.clientWidth, height: container.clientHeight });
      }
    });
    observer.observe(container);
  }

  function setVisibleRange() {
    if (!chart || !data.length) return;
    const days = PERIOD_DAYS[period] ?? 99999;
    if (period === 'max' || days >= 99999) {
      chart.timeScale().fitContent();
      return;
    }
    const lastDate = data[data.length - 1].date;
    const from = new Date(lastDate);
    from.setDate(from.getDate() - days);
    const fromStr = from.toISOString().slice(0, 10);
    try {
      chart.timeScale().setVisibleRange({ from: fromStr, to: lastDate });
    } catch {
      chart.timeScale().fitContent();
    }
  }

  $effect(() => {
    const _ = data;
    const __ = ticker;
    const ___ = $theme;
    if (data.length && container) {
      if (ticker !== prevTicker || !chart) {
        prevTicker = ticker;
        createAndApply();
      }
    }
  });

  $effect(() => {
    const _ = period;
    if (chart && data.length) {
      setVisibleRange();
    }
  });

  onDestroy(destroyChart);
</script>

<div class="candle-chart">
  <div class="header">
    <span class="title">{ticker} — Candlestick</span>
    <div class="legend">
      <span style="color:#f0b90b">MA50</span>
      <span style="color:#da3633">MA200</span>
    </div>
  </div>
  <div class="chart-wrap" bind:this={container}></div>
</div>

<style>
  .candle-chart { display: flex; flex-direction: column; height: 480px; padding: 8px 10px; flex-shrink: 0; }
  .header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px; gap: 12px; flex-shrink: 0; }
  .title { font-family: var(--font-mono); font-size: 11px; color: var(--text-muted); }
  .legend { font-family: var(--font-mono); font-size: 9px; display: flex; gap: 8px; }
  .chart-wrap { flex: 1; min-height: 300px; border-radius: 5px; overflow: hidden; }
</style>
