<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { Chart, BarElement, CategoryScale, LinearScale, Tooltip, BarController } from 'chart.js';

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

    const bgColors = colorFn ? data.map(v => colorFn!(v)) : data.map(() => '#00bcd488');

    chart = new Chart(canvas, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          data,
          backgroundColor: bgColors,
          borderColor: bgColors.map(c => c.replace(/88$/, '')),
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
            backgroundColor: '#1c2128',
            borderColor: '#30363d',
            borderWidth: 1,
            bodyFont: { family: 'JetBrains Mono', size: 10 },
            callbacks: {
              label: (ctx: any) => formatFn ? formatFn(ctx.parsed.y) : String(ctx.parsed.y)
            }
          }
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: { color: '#484f58', font: { family: 'JetBrains Mono', size: 8 }, maxRotation: 45 },
            border: { color: '#30363d' },
          },
          y: {
            grid: { color: '#21262d' },
            ticks: {
              color: '#484f58',
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
  onDestroy(() => { if (chart) { chart.destroy(); chart = null; } });
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
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px;
    color: #484f58;
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
