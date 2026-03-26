<script lang="ts">
  import { companyData, selectedTicker, activeTab, chartData } from '$lib/stores/screener';
  import { fmt, fmtLarge } from '$lib/utils/format';
</script>

{#if $companyData}
<div class="header">
  <div class="top-row">
    <div class="identity">
      <h1 class="name">{$companyData.name}</h1>
      <span class="ticker">{$companyData.ticker}</span>
    </div>
    <button class="close" onclick={() => { selectedTicker.set(null); companyData.set(null); chartData.set([]); activeTab.set('overview'); }}
      aria-label="Close panel">
      <svg viewBox="0 0 16 16" fill="none" width="14" height="14">
        <path d="M4 4L12 12M12 4L4 12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
      </svg>
    </button>
  </div>

  <div class="price-row">
    <span class="price">{fmt($companyData.price)}</span>
    <span class="currency">SEK</span>
    <span class={($companyData.change_pct ?? 0) >= 0 ? 'change pos' : 'change neg'}>
      {($companyData.change_pct ?? 0) >= 0 ? '+' : ''}{fmt($companyData.change_pct)}%
    </span>
  </div>

  <div class="meta">
    {#each [
      { label: 'Sector', value: $companyData.sector },
      { label: 'Industry', value: $companyData.industry },
      { label: 'Country', value: $companyData.country },
      { label: 'MCap', value: fmtLarge($companyData.market_cap) },
    ] as item}
      <span class="meta-item">
        <span class="meta-label">{item.label}</span>
        {item.value || '\u2014'}
      </span>
    {/each}
  </div>
</div>
{/if}

<style>
  .header {
    padding: 14px 16px 12px;
    border-bottom: 1px solid var(--border);
    background: var(--bg-surface);
    flex-shrink: 0;
  }

  .top-row {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 12px;
  }
  .identity {
    display: flex;
    align-items: baseline;
    gap: 8px;
    min-width: 0;
    flex-wrap: wrap;
  }
  .name {
    font-size: 16px;
    font-weight: 700;
    line-height: 1.2;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .ticker {
    font-family: var(--font-mono);
    font-size: 12px;
    color: var(--accent);
    background: var(--accent-dim);
    padding: 1px 6px;
    border-radius: 4px;
    white-space: nowrap;
  }

  .close {
    background: none;
    border: 1px solid transparent;
    color: var(--text-dim);
    cursor: pointer;
    padding: 4px;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.15s;
    flex-shrink: 0;
  }
  .close:hover {
    color: var(--text);
    background: var(--bg-hover);
    border-color: var(--border);
  }

  .price-row {
    display: flex;
    align-items: baseline;
    gap: 6px;
    margin-top: 8px;
  }
  .price {
    font-family: var(--font-mono);
    font-size: 22px;
    font-weight: 700;
    letter-spacing: -0.5px;
  }
  .currency {
    font-family: var(--font-mono);
    font-size: 11px;
    color: var(--text-dim);
  }
  .change {
    font-family: var(--font-mono);
    font-size: 13px;
    font-weight: 600;
    padding: 2px 6px;
    border-radius: 4px;
  }
  .pos {
    color: var(--positive);
    background: rgba(46, 160, 67, 0.1);
  }
  .neg {
    color: var(--negative);
    background: rgba(218, 54, 51, 0.1);
  }

  .meta {
    display: flex;
    flex-wrap: wrap;
    gap: 4px 8px;
    margin-top: 10px;
  }
  .meta-item {
    font-size: 11px;
    color: var(--text-muted);
    background: var(--bg);
    padding: 3px 8px;
    border-radius: 4px;
    border: 1px solid rgba(48, 54, 61, 0.5);
  }
  .meta-label {
    color: var(--text-dim);
    margin-right: 4px;
  }
</style>
