<script lang="ts">
  import { companyData } from '$lib/stores/screener';
  import { fmt, fmtPct } from '$lib/utils/format';

  const ratios = [
    { label: 'P/E', key: 'pe', format: fmt, tip: 'Price to Earnings — lower may indicate better value' },
    { label: 'P/B', key: 'pb', format: fmt, tip: 'Price to Book — below 1 may indicate undervaluation' },
    { label: 'P/S', key: 'ps', format: fmt, tip: 'Price to Sales — useful for unprofitable companies' },
    { label: 'EV/EBITDA', key: 'ev_ebitda', format: fmt, tip: 'Enterprise Value to EBITDA — lower is generally better' },
    { label: 'Div Yield', key: 'div_yield', format: fmtPct, tip: 'Annual dividend as percentage of share price' },
    { label: 'ROE', key: 'roe', format: fmtPct, tip: 'Return on Equity — above 15% is generally strong' },
    { label: 'Margin', key: 'margin', format: fmtPct, tip: 'Net profit margin — percentage of revenue kept as profit' },
    { label: 'EPS', key: 'eps', format: fmt, tip: 'Earnings Per Share — net income divided by shares outstanding' },
  ];
</script>

{#if $companyData}
<div class="ratios">
  <div class="grid">
    {#each ratios as r}
      <div class="card" title={r.tip}>
        <span class="label">{r.label}</span>
        <span class="value">{r.format($companyData[r.key as keyof typeof $companyData] as number | null)}</span>
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
</style>
