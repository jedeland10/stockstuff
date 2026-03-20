<script lang="ts">
  import { onDestroy, tick } from 'svelte';
  import { computeMA } from '$lib/utils/technicals';
  import type { PricePoint } from '$lib/api/types';

  let { data, ticker }: { data: PricePoint[]; ticker: string } = $props();

  let container: HTMLDivElement;
  let chart: any = null;
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

    chart = LW.createChart(container, {
      width: container.clientWidth,
      height: container.clientHeight,
      watermark: { visible: false },
      layout: {
        background: { type: 'solid', color: '#0d1117' },
        textColor: '#8b949e',
        fontFamily: "'JetBrains Mono', monospace",
        fontSize: 10,
      },
      grid: { vertLines: { color: '#21262d' }, horzLines: { color: '#21262d' } },
      crosshair: { mode: LW.CrosshairMode.Normal },
      rightPriceScale: { borderColor: '#30363d' },
      timeScale: { borderColor: '#30363d', timeVisible: false },
    });

    const candles = chart.addCandlestickSeries({
      upColor: '#2ea043', downColor: '#da3633',
      borderUpColor: '#2ea043', borderDownColor: '#da3633',
      wickUpColor: '#2ea04399', wickDownColor: '#da363399',
    });
    candles.setData(data.map(d => ({ time: d.date, open: d.open!, high: d.high!, low: d.low!, close: d.close! })));

    const vol = chart.addHistogramSeries({ color: '#30363d', priceFormat: { type: 'volume' }, priceScaleId: '' });
    vol.priceScale().applyOptions({ scaleMargins: { top: 0.85, bottom: 0 } });
    vol.setData(data.map(d => ({
      time: d.date, value: d.volume ?? 0,
      color: (d.close ?? 0) >= (d.open ?? 0) ? '#2ea04333' : '#da363333',
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

    chart.timeScale().fitContent();

    observer = new ResizeObserver(() => {
      if (chart && container.clientWidth > 0 && container.clientHeight > 0) {
        chart.applyOptions({ width: container.clientWidth, height: container.clientHeight });
      }
    });
    observer.observe(container);
  }

  $effect(() => {
    const _ = data;
    const __ = ticker;
    if (data.length && container) {
      createAndApply();
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
