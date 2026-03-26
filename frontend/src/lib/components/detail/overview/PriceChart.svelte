<script lang="ts">
  import { onDestroy, tick } from 'svelte';
  import type { PricePoint } from '$lib/api/types';

  let { data, ticker }: { data: PricePoint[]; ticker: string } = $props();

  let container: HTMLDivElement;
  let chart: any = null;
  let areaSeries: any = null;
  let volumeSeries: any = null;
  let observer: ResizeObserver | null = null;
  let LW: any = null;

  function destroyChart() {
    observer?.disconnect();
    observer = null;
    if (chart) { try { chart.remove(); } catch {} }
    chart = null;
    areaSeries = null;
    volumeSeries = null;
  }

  async function createAndApply() {
    if (!container || !data.length) return;
    if (!LW) LW = await import('lightweight-charts');

    destroyChart();

    // Wait for paint
    await tick();
    await new Promise(r => requestAnimationFrame(r));
    await new Promise(r => requestAnimationFrame(r));

    const w = container.clientWidth;
    const h = container.clientHeight;
    if (w < 50 || h < 50) {
      // Retry once more after a delay
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

    areaSeries = chart.addAreaSeries({
      topColor: 'rgba(0, 188, 212, 0.3)',
      bottomColor: 'rgba(0, 188, 212, 0.02)',
      lineColor: '#00bcd4',
      lineWidth: 2,
    });

    volumeSeries = chart.addHistogramSeries({
      color: '#30363d',
      priceFormat: { type: 'volume' },
      priceScaleId: '',
    });
    volumeSeries.priceScale().applyOptions({ scaleMargins: { top: 0.85, bottom: 0 } });

    applyData();

    observer = new ResizeObserver(() => {
      if (chart && container.clientWidth > 0 && container.clientHeight > 0) {
        chart.applyOptions({ width: container.clientWidth, height: container.clientHeight });
      }
    });
    observer.observe(container);
  }

  function applyData() {
    if (!areaSeries || !volumeSeries || !data.length) return;
    areaSeries.setData(data.map(d => ({ time: d.date, value: d.close ?? 0 })));
    volumeSeries.setData(data.map(d => ({
      time: d.date, value: d.volume ?? 0,
      color: (d.close ?? 0) >= (d.open ?? 0) ? '#2ea04344' : '#da363344',
    })));
    chart?.timeScale().fitContent();
  }

  $effect(() => {
    // Trigger on data or ticker change
    const _ = data;
    const __ = ticker;
    if (data.length && container) {
      if (chart && areaSeries) {
        applyData();
      } else {
        createAndApply();
      }
    }
  });

  onDestroy(destroyChart);
</script>

<div class="price-chart">
  <div class="header">
    <span class="title">{ticker} — Price</span>
  </div>
  <div class="chart-wrap" bind:this={container}></div>
</div>

<style>
  .price-chart { display: flex; flex-direction: column; height: 340px; padding: 10px 16px; flex-shrink: 0; }
  .header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; flex-shrink: 0; }
  .title { font-family: var(--font-mono); font-size: 11px; color: var(--text-muted); }
  .chart-wrap { flex: 1; min-height: 200px; border-radius: 8px; overflow: hidden; }
</style>
