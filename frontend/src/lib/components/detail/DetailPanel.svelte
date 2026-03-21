<script lang="ts">
  import { companyData, activeTab, selectedTicker, chartData } from '$lib/stores/screener';
  import { getChart, getScores, type StockScores } from '$lib/api/client';
  import DetailHeader from './DetailHeader.svelte';
  import TabBar from './TabBar.svelte';
  import PriceChart from './overview/PriceChart.svelte';
  import KeyRatios from './overview/KeyRatios.svelte';
  import CompanyDescription from './overview/CompanyDescription.svelte';
  import BarChart from '$lib/components/shared/BarChart.svelte';
  import ReportTab from './report/ReportTab.svelte';
  import KeyNumbersTab from './keynumbers/KeyNumbersTab.svelte';
  import CandlestickChart from './technical/CandlestickChart.svelte';
  import PerformanceRow from './technical/PerformanceRow.svelte';
  import TechnicalIndicators from './technical/TechnicalIndicators.svelte';
  import { fmtLarge, fmt } from '$lib/utils/format';
  import type { PricePoint } from '$lib/api/types';

  let chartPeriod = $state('1y');
  let techPeriod = $state('1y');
  let techData = $state<PricePoint[]>([]);
  let scores = $state<StockScores | null>(null);

  // Fetch scores when ticker changes
  $effect(() => {
    const ticker = $selectedTicker;
    if (ticker) {
      getScores(ticker).then(s => scores = s);
    } else {
      scores = null;
    }
  });

  let finData = $derived.by(() => {
    const cd = $companyData;
    if (!cd?.financials?.length) return null;
    const sorted = [...cd.financials].sort((a, b) => a.year - b.year);
    const labels = sorted.map(f => String(f.year));
    const growthData = sorted.map((f, i) => {
      if (i === 0 || !sorted[i-1].revenue || !f.revenue) return null;
      return ((f.revenue - sorted[i-1].revenue!) / Math.abs(sorted[i-1].revenue!)) * 100;
    });
    return { sorted, labels, growthData };
  });

  const signColor = (v: number | null) => v != null ? (v >= 0 ? '#2ea04388' : '#da363388') : '#30363d88';
  const fmtPctFn = (v: number) => v != null ? v.toFixed(1) + '%' : '\u2014';
  const fmtEps = (v: number) => v != null ? v.toFixed(2) : '\u2014';
  const fmtLargeFn = (v: number) => fmtLarge(v);

  const periods = ['1m', '3m', '6m', '1y', '2y', '5y', '10y', 'max'];
  const techPeriods = ['1m', '3m', '6m', '1y', '2y', '5y'];

  async function setChartPeriod(p: string) {
    chartPeriod = p;
    const ticker = $selectedTicker;
    if (!ticker) return;
    const data = await getChart(ticker, p);
    chartData.set(data);
  }

  async function setTechPeriod(p: string) {
    techPeriod = p;
    const ticker = $selectedTicker;
    if (!ticker) return;
    techData = await getChart(ticker, p);
  }

  // Load tech data when switching to technical tab
  $effect(() => {
    if ($activeTab === 'technical' && $selectedTicker && !techData.length) {
      getChart($selectedTicker, techPeriod).then(d => techData = d);
    }
  });
</script>

<div class="detail-panel">
  <DetailHeader />
  <TabBar />

  <div class="tab-scroll">
    {#if $activeTab === 'overview'}
      <KeyRatios />
      {#if scores && (scores.graham_number != null || scores.f_score != null)}
        <div class="scores-row">
          {#if scores.graham_number != null}
            <div class="score-card">
              <span class="score-label">Graham Number</span>
              <span class="score-value">{fmt(scores.graham_number)}</span>
              {#if $companyData?.price}
                <span class="score-hint" class:text-positive={scores.graham_number > $companyData.price} class:text-negative={scores.graham_number <= $companyData.price}>
                  {scores.graham_number > $companyData.price ? 'Undervalued' : 'Overvalued'}
                </span>
              {/if}
            </div>
          {/if}
          {#if scores.f_score != null}
            <div class="score-card">
              <span class="score-label">Piotroski F-Score</span>
              <span class="score-value">{scores.f_score}<span class="score-max">/9</span></span>
              <span class="score-hint" class:text-positive={scores.f_score >= 7} class:text-negative={scores.f_score <= 3}
                style:color={scores.f_score >= 4 && scores.f_score <= 6 ? 'var(--text-muted)' : ''}>
                {scores.f_score >= 7 ? 'Strong' : scores.f_score <= 3 ? 'Weak' : 'Neutral'}
              </span>
            </div>
          {/if}
        </div>
      {/if}
      <div class="period-bar">
        {#each periods as p}
          <button class="period" class:active={chartPeriod === p} onclick={() => setChartPeriod(p)}>{p}</button>
        {/each}
      </div>
      <PriceChart data={$chartData} ticker={$selectedTicker ?? ''} />
      {#if finData}
        <div class="fin-grid">
          <BarChart id="ov-rev" title="Net Sales" labels={finData.labels} data={finData.sorted.map(f => f.revenue)} formatFn={fmtLargeFn} />
          <BarChart id="ov-growth" title="Rev Growth" labels={finData.labels} data={finData.growthData} colorFn={signColor} formatFn={fmtPctFn} />
          <BarChart id="ov-eps" title="EPS" labels={finData.labels} data={finData.sorted.map(f => f.eps)} colorFn={signColor} formatFn={fmtEps} />
          <BarChart id="ov-margin" title="Profit Margin" labels={finData.labels} data={finData.sorted.map(f => f.profit_margin)} colorFn={signColor} formatFn={fmtPctFn} />
        </div>
      {/if}
      <CompanyDescription />

    {:else if $activeTab === 'report'}
      <ReportTab />

    {:else if $activeTab === 'keynumbers'}
      <KeyNumbersTab />

    {:else if $activeTab === 'technical'}
      <div class="period-bar">
        {#each techPeriods as p}
          <button class="period" class:active={techPeriod === p} onclick={() => setTechPeriod(p)}>{p}</button>
        {/each}
      </div>
      <PerformanceRow />
      <CandlestickChart data={techData} ticker={$selectedTicker ?? ''} />
      <TechnicalIndicators />
    {/if}
  </div>
</div>

<style>
  .detail-panel {
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow: hidden;
    background: var(--bg);
  }
  .tab-scroll {
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
  }
  .fin-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    grid-template-rows: repeat(2, 150px);
    gap: 6px;
    padding: 6px 10px;
    border-top: 1px solid var(--border);
  }
  .period-bar {
    display: flex;
    gap: 1px;
    padding: 6px 10px;
    background: var(--bg-surface);
    border-bottom: 1px solid var(--border);
    flex-shrink: 0;
  }
  .period {
    padding: 3px 8px;
    border: none;
    background: transparent;
    color: var(--text-dim);
    font-family: var(--font-mono);
    font-size: 9px;
    cursor: pointer;
    border-radius: 3px;
  }
  .period:hover { color: var(--text-muted); }
  .period.active { color: var(--accent); background: var(--bg); }

  .scores-row {
    display: flex;
    gap: 8px;
    padding: 8px 14px;
    border-bottom: 1px solid var(--border);
  }
  .score-card {
    flex: 1;
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: 5px;
    padding: 10px 12px;
    display: flex;
    flex-direction: column;
    gap: 2px;
  }
  .score-label {
    font-family: var(--font-mono);
    font-size: 9px;
    color: var(--text-dim);
    text-transform: uppercase;
    letter-spacing: 0.3px;
  }
  .score-value {
    font-family: var(--font-mono);
    font-size: 20px;
    font-weight: 600;
    color: var(--text);
  }
  .score-max {
    font-size: 12px;
    color: var(--text-dim);
    font-weight: 400;
  }
  .score-hint {
    font-family: var(--font-mono);
    font-size: 10px;
    font-weight: 500;
  }
</style>
