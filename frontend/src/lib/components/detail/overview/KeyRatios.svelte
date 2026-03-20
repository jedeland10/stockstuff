<script lang="ts">
  import { companyData } from '$lib/stores/screener';
  import { fmt, fmtPct } from '$lib/utils/format';

  const ratios = [
    { label: 'P/E', key: 'pe', format: fmt },
    { label: 'P/B', key: 'pb', format: fmt },
    { label: 'P/S', key: 'ps', format: fmt },
    { label: 'EV/EBITDA', key: 'ev_ebitda', format: fmt },
    { label: 'Div Yield', key: 'div_yield', format: fmtPct },
    { label: 'ROE', key: 'roe', format: fmtPct },
    { label: 'Margin', key: 'margin', format: fmtPct },
    { label: 'EPS', key: 'eps', format: fmt },
  ];
</script>

{#if $companyData}
<div class="ratios">
  <h3 class="section-label">Key Ratios</h3>
  <div class="grid">
    {#each ratios as r}
      <div class="card">
        <span class="label">{r.label}</span>
        <span class="value">{r.format($companyData[r.key as keyof typeof $companyData] as number | null)}</span>
      </div>
    {/each}
  </div>
</div>
{/if}

<style>
  .ratios {
    padding: 12px 14px;
  }
  .section-label {
    font-family: var(--font-mono);
    font-size: 10px;
    color: var(--text-dim);
    text-transform: uppercase;
    letter-spacing: 0.4px;
    margin-bottom: 8px;
  }
  .grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 6px;
  }
  .card {
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: 5px;
    padding: 8px 10px;
    display: flex;
    flex-direction: column;
  }
  .label {
    font-size: 8px;
    font-family: var(--font-mono);
    color: var(--text-dim);
    text-transform: uppercase;
  }
  .value {
    font-family: var(--font-mono);
    font-size: 14px;
    font-weight: 600;
    color: var(--text);
  }
</style>
