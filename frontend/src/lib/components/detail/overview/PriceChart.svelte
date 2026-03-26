<script lang="ts">
  import { onDestroy, tick } from 'svelte';
  import type { PricePoint } from '$lib/api/types';
  import { cssVar, theme } from '$lib/stores/theme';

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

    const bg = cssVar('--bg');
    const textMuted = cssVar('--text-muted');
    const grid = cssVar('--chart-grid');
    const border = cssVar('--border');
    const accent = cssVar('--accent');
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

    areaSeries = chart.addAreaSeries({
      topColor: accent + '4d',
      bottomColor: accent + '05',
      lineColor: accent,
      lineWidth: 2,
    });

    volumeSeries = chart.addHistogramSeries({
      color: volume,
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
      color: (d.close ?? 0) >= (d.open ?? 0) ? cssVar('--positive') + '44' : cssVar('--negative') + '44',
    })));
    chart?.timeScale().fitContent();
  }

  $effect(() => {
    // Trigger on data, ticker, or theme change
    const _ = data;
    const __ = ticker;
    const ___ = $theme;
    if (data.length && container) {
      createAndApply();
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
