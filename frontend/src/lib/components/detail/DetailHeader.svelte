<script lang="ts">
  import { companyData, selectedTicker, activeTab, chartData } from '$lib/stores/screener';
  import { fmt, fmtLarge } from '$lib/utils/format';
</script>

{#if $companyData}
<div class="header">
  <button class="close" onclick={() => { selectedTicker.set(null); companyData.set(null); chartData.set([]); activeTab.set('overview'); }}>&times;</button>
  <div class="row">
    <span class="name">{$companyData.name}</span>
    <span class="ticker">{$companyData.ticker}</span>
    <span class="price">{fmt($companyData.price)}</span>
    <span class={($companyData.change_pct ?? 0) >= 0 ? 'change pos' : 'change neg'}>
      {($companyData.change_pct ?? 0) >= 0 ? '+' : ''}{fmt($companyData.change_pct)}%
    </span>
  </div>
  <div class="meta">
    <span>Sector: {$companyData.sector || '\u2014'}</span>
    <span>Industry: {$companyData.industry || '\u2014'}</span>
    <span>Country: {$companyData.country || '\u2014'}</span>
    <span>MCap: {fmtLarge($companyData.market_cap)}</span>
  </div>
</div>
{/if}

<style>
  .header {
    padding: 10px 14px;
    border-bottom: 1px solid var(--border);
    background: var(--bg-surface);
    flex-shrink: 0;
  }
  .close {
    float: right;
    background: none;
    border: none;
    color: var(--text-dim);
    cursor: pointer;
    font-size: 16px;
    line-height: 1;
  }
  .close:hover {
    color: var(--text);
  }
  .row {
    display: flex;
    align-items: baseline;
    gap: 10px;
    flex-wrap: wrap;
  }
  .name {
    font-size: 14px;
    font-weight: 700;
  }
  .ticker {
    font-family: var(--font-mono);
    font-size: 12px;
    color: var(--accent);
  }
  .price {
    font-family: var(--font-mono);
    font-size: 18px;
    font-weight: 600;
  }
  .change {
    font-family: var(--font-mono);
    font-size: 12px;
    font-weight: 500;
  }
  .pos {
    color: var(--positive);
  }
  .neg {
    color: var(--negative);
  }
  .meta {
    font-size: 11px;
    color: var(--text-muted);
    display: flex;
    flex-wrap: wrap;
    gap: 4px 12px;
    margin-top: 4px;
  }
</style>
