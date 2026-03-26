<script lang="ts">
  import { onMount } from 'svelte';
  import { companyData } from '$lib/stores/screener';
  import { fmt, fmtPct } from '$lib/utils/format';
  import { getSectorAverages, type SectorAverages } from '$lib/api/client';

  let sectorAvgs = $state<SectorAverages>({});

  onMount(async () => {
    sectorAvgs = await getSectorAverages();
  });

  const ratios: { label: string; key: string; format: (v: number | null) => string; tip: string; higherIsBetter: boolean }[] = [
    { label: 'P/E', key: 'pe', format: fmt, tip: 'Price to Earnings — lower may indicate better value', higherIsBetter: false },
    { label: 'P/B', key: 'pb', format: fmt, tip: 'Price to Book — below 1 may indicate undervaluation', higherIsBetter: false },
    { label: 'P/S', key: 'ps', format: fmt, tip: 'Price to Sales — useful for unprofitable companies', higherIsBetter: false },
    { label: 'EV/EBITDA', key: 'ev_ebitda', format: fmt, tip: 'Enterprise Value to EBITDA — lower is generally better', higherIsBetter: false },
    { label: 'Div Yield', key: 'div_yield', format: fmtPct, tip: 'Annual dividend as percentage of share price', higherIsBetter: true },
    { label: 'ROE', key: 'roe', format: fmtPct, tip: 'Return on Equity — above 15% is generally strong', higherIsBetter: true },
    { label: 'Margin', key: 'margin', format: fmtPct, tip: 'Net profit margin — percentage of revenue kept as profit', higherIsBetter: true },
    { label: 'EPS', key: 'eps', format: fmt, tip: 'Earnings Per Share — net income divided by shares outstanding', higherIsBetter: true },
  ];

  function getSectorAvg(key: string): number | null {
    const sector = $companyData?.sector;
    if (!sector || !sectorAvgs[sector]) return null;
    return sectorAvgs[sector][key as keyof typeof sectorAvgs[string]] as number | null;
  }

  function compareLabel(val: number | null, avg: number | null, higherIsBetter: boolean): { text: string; color: string } | null {
    if (val == null || avg == null || avg === 0) return null;
    const diff = ((val - avg) / Math.abs(avg)) * 100;
    if (Math.abs(diff) < 5) return { text: 'Avg', color: 'var(--text-dim)' };
    const isAbove = diff > 0;
    const isGood = higherIsBetter ? isAbove : !isAbove;
    const arrow = isAbove ? '\u25B2' : '\u25BC';
    return {
      text: `${arrow} ${Math.abs(diff).toFixed(0)}% vs sector`,
      color: isGood ? 'var(--positive)' : 'var(--negative)',
    };
  }
</script>

{#if $companyData}
<div class="ratios">
  <div class="grid">
    {#each ratios as r}
      {@const val = $companyData[r.key as keyof typeof $companyData] as number | null}
      {@const avg = getSectorAvg(r.key)}
      {@const cmp = compareLabel(val, avg, r.higherIsBetter)}
      <div class="card" title={r.tip}>
        <span class="label">{r.label}</span>
        <span class="value">{r.format(val)}</span>
        {#if cmp}
          <span class="sector-cmp" style="color:{cmp.color}">{cmp.text}</span>
        {:else if avg != null}
          <span class="sector-cmp" style="color:var(--text-dim)">Sector: {r.format(avg)}</span>
        {/if}
      </div>
    {/each}
  </div>
</div>
{/if}

<style>
  .ratios {
    padding: 12px 16px;
  }
  .grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
  }
  .card {
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 10px 12px;
    display: flex;
    flex-direction: column;
    gap: 2px;
    transition: border-color 0.15s;
    cursor: default;
  }
  .card:hover {
    border-color: var(--text-dim);
  }
  .label {
    font-size: 9px;
    font-family: var(--font-mono);
    color: var(--text-dim);
    text-transform: uppercase;
    letter-spacing: 0.3px;
  }
  .value {
    font-family: var(--font-mono);
    font-size: 15px;
    font-weight: 600;
    color: var(--text);
  }
  .sector-cmp {
    font-family: var(--font-mono);
    font-size: 9px;
    font-weight: 500;
    margin-top: 1px;
  }
</style>
