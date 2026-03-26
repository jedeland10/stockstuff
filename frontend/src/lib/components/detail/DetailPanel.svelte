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

  // Fetch scores when ticker changes, reset tech data
  $effect(() => {
    const ticker = $selectedTicker;
    if (ticker) {
      getScores(ticker).then(s => scores = s);
      techData = [];
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

  const signColor = (v: number | null) => {
    const s = getComputedStyle(document.documentElement);
    const pos = s.getPropertyValue('--positive-bg').trim();
    const neg = s.getPropertyValue('--negative-bg').trim();
    const neu = s.getPropertyValue('--neutral-bg').trim();
    return v != null ? (v >= 0 ? pos : neg) : neu;
  };
  const fmtPctFn = (v: number) => v != null ? v.toFixed(1) + '%' : '\u2014';
  const fmtEps = (v: number) => v != null ? v.toFixed(2) : '\u2014';
  const fmtLargeFn = (v: number) => fmtLarge(v);

  const periods = ['1m', '3m', '6m', '1y', '2y', '5y', '10y', 'max'];
  const techPeriods = ['1m', '3m', '6m', '1y', '2y', '5y'];

  function setChartPeriod(p: string) {
    chartPeriod = p;
  }

  function setTechPeriod(p: string) {
    techPeriod = p;
  }

  // Load tech data when switching to technical tab (fetch max once)
  $effect(() => {
    if ($activeTab === 'technical' && $selectedTicker && !techData.length) {
      getChart($selectedTicker, 'max').then(d => techData = d);
    }
  });
</script>

<div class="detail-panel">
  <DetailHeader />
  <TabBar />

  <div class="tab-scroll">
    {#if $activeTab === 'overview'}
      <KeyRatios />
      {#if scores && (scores.graham_number != null || scores.f_score != null || scores.magic_rank != null)}
        <div class="scores-row">
          {#if scores.graham_number != null}
            {@const isUnder = $companyData?.price ? scores.graham_number > $companyData.price : false}
            <div class="score-card" title="Graham Number estimates intrinsic value based on EPS and book value. Compare to current price.">
              <span class="score-label">Graham Number</span>
              <span class="score-value">{fmt(scores.graham_number)}</span>
              {#if $companyData?.price}
                <span class="score-badge" class:badge-positive={isUnder} class:badge-negative={!isUnder}>
                  {isUnder ? 'Undervalued' : 'Overvalued'}
                </span>
              {/if}
            </div>
          {/if}
          {#if scores.f_score != null}
            {@const level = scores.f_score >= 7 ? 'strong' : scores.f_score <= 3 ? 'weak' : 'neutral'}
            <div class="score-card" title="Piotroski F-Score rates financial strength from 0-9. 7+ is strong, 3 or below is weak.">
              <span class="score-label">Piotroski F-Score</span>
              <div class="score-row">
                <span class="score-value">{scores.f_score}<span class="score-max">/9</span></span>
                <div class="score-dots">
                  {#each Array(9) as _, i}
                    <span class="dot" class:dot-filled={i < scores.f_score}
                      class:dot-positive={level === 'strong'}
                      class:dot-negative={level === 'weak'}
                      class:dot-neutral={level === 'neutral'}></span>
                  {/each}
                </div>
              </div>
              <span class="score-badge" class:badge-positive={level === 'strong'} class:badge-negative={level === 'weak'} class:badge-neutral={level === 'neutral'}>
                {level === 'strong' ? 'Strong' : level === 'weak' ? 'Weak' : 'Neutral'}
              </span>
            </div>
          {/if}
          {#if scores.magic_rank != null}
            <div class="score-card" title="Magic Formula ranks stocks by combined earnings yield and return on capital. Lower rank = better.">
              <span class="score-label">Magic Formula</span>
              <span class="score-value">#{scores.magic_rank}</span>
              <span class="score-hint">
                of {scores.magic_total} stocks
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
      <PriceChart data={$chartData} ticker={$selectedTicker ?? ''} period={chartPeriod} />
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
      <CandlestickChart data={techData} ticker={$selectedTicker ?? ''} period={techPeriod} />
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
    min-height: 0;
    overflow-y: auto;
    overflow-x: hidden;
  }
  .fin-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    grid-template-rows: repeat(2, 170px);
    gap: 8px;
    padding: 10px 16px;
    border-top: 1px solid var(--border);
  }
  .period-bar {
    display: flex;
    gap: 2px;
    padding: 8px 16px;
    background: var(--bg-surface);
    border-bottom: 1px solid var(--border);
    flex-shrink: 0;
  }
  .period {
    padding: 4px 10px;
    border: none;
    background: transparent;
    color: var(--text-dim);
    font-family: var(--font-mono);
    font-size: 11px;
    font-weight: 500;
    cursor: pointer;
    border-radius: 6px;
    transition: all 0.15s;
  }
  .period:hover { color: var(--text-muted); background: var(--bg-hover); }
  .period.active { color: var(--accent); background: var(--accent-dim); }

  .scores-row {
    display: flex;
    gap: 8px;
    padding: 10px 16px;
    border-bottom: 1px solid var(--border);
  }
  .score-card {
    flex: 1;
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 10px 12px;
    display: flex;
    flex-direction: column;
    gap: 4px;
    cursor: default;
    transition: border-color 0.15s;
  }
  .score-card:hover { border-color: var(--text-dim); }
  .score-label {
    font-family: var(--font-mono);
    font-size: 9px;
    color: var(--text-dim);
    text-transform: uppercase;
    letter-spacing: 0.3px;
  }
  .score-value {
    font-family: var(--font-mono);
    font-size: 22px;
    font-weight: 700;
    color: var(--text);
    letter-spacing: -0.5px;
  }
  .score-max {
    font-size: 12px;
    color: var(--text-dim);
    font-weight: 400;
  }
  .score-row {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .score-dots {
    display: flex;
    gap: 3px;
    align-items: center;
  }
  .dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--bg-hover);
    border: 1px solid var(--border);
  }
  .dot-filled.dot-positive { background: var(--positive); border-color: var(--positive); }
  .dot-filled.dot-negative { background: var(--negative); border-color: var(--negative); }
  .dot-filled.dot-neutral { background: var(--gold); border-color: var(--gold); }

  .score-badge {
    font-family: var(--font-mono);
    font-size: 10px;
    font-weight: 600;
    padding: 2px 6px;
    border-radius: 4px;
    width: fit-content;
  }
  .badge-positive { color: var(--positive); background: rgba(46, 160, 67, 0.1); }
  .badge-negative { color: var(--negative); background: rgba(218, 54, 51, 0.1); }
  .badge-neutral { color: var(--gold); background: rgba(212, 160, 23, 0.1); }

  .score-hint {
    font-family: var(--font-mono);
    font-size: 10px;
    font-weight: 500;
    color: var(--text-muted);
  }
</style>
