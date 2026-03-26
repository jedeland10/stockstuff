<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { Chart, BarElement, CategoryScale, LinearScale, Tooltip, BarController } from 'chart.js';
  import { cssVar, theme } from '$lib/stores/theme';

  Chart.register(BarElement, CategoryScale, LinearScale, Tooltip, BarController);

  let {
    id,
    labels,
    data,
    title,
    formatFn,
    colorFn
  }: {
    id: string;
    labels: string[];
    data: (number | null)[];
    title: string;
    formatFn?: (v: number) => string;
    colorFn?: (v: number | null) => string;
  } = $props();

  let canvas: HTMLCanvasElement;
  let chart: Chart | null = null;

  function makeChart() {
    if (!canvas) return;
    if (chart) chart.destroy();

    const accent = cssVar('--accent');
    const elevated = cssVar('--bg-elevated');
    const border = cssVar('--border');
    const dim = cssVar('--text-dim');
    const grid = cssVar('--chart-grid');

    const bgColors = colorFn ? data.map(v => colorFn!(v)) : data.map(() => accent + '88');

    chart = new Chart(canvas, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          data,
          backgroundColor: bgColors,
          borderColor: bgColors.map(c => c.replace(/88$/, '').replace(/44$/, '')),
          borderWidth: 1,
          borderRadius: 2,
          maxBarThickness: 24,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: { duration: 300 },
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: elevated,
            borderColor: border,
            borderWidth: 1,
            titleColor: cssVar('--text'),
            bodyColor: cssVar('--text'),
            bodyFont: { family: 'JetBrains Mono', size: 10 },
            callbacks: {
              label: (ctx: any) => formatFn ? formatFn(ctx.parsed.y) : String(ctx.parsed.y)
            }
          }
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: { color: dim, font: { family: 'JetBrains Mono', size: 8 }, maxRotation: 45 },
            border: { color: border },
          },
          y: {
            grid: { color: grid },
            ticks: {
              color: dim,
              font: { family: 'JetBrains Mono', size: 8 },
              callback: (v: any) => formatFn ? formatFn(v) : v
            },
            border: { display: false },
          }
        }
      }
    });
  }

  onMount(() => { setTimeout(makeChart, 20); });
  onDestroy(() => {
    if (chart) { chart.destroy(); chart = null; }
    unsub();
  });

  // Recreate chart when theme changes
  let mounted = false;
  const unsub = theme.subscribe(() => {
    if (mounted && canvas) setTimeout(makeChart, 50);
  });
  onMount(() => { mounted = true; });
</script>

<div class="bar-chart-wrap">
  <h4 class="chart-title">{title}</h4>
  <div class="canvas-wrap">
    <canvas bind:this={canvas}></canvas>
  </div>
</div>

<style>
  .bar-chart-wrap {
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow: hidden;
  }
  .chart-title {
    font-family: var(--font-mono);
    font-size: 9px;
    color: var(--text-dim);
    text-transform: uppercase;
    text-align: center;
    margin-bottom: 2px;
    flex-shrink: 0;
  }
  .canvas-wrap {
    flex: 1;
    min-height: 0;
    position: relative;
  }
</style>
