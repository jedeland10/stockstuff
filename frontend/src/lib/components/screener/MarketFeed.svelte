<script lang="ts">
  import type { StockRow } from '$lib/api/types';

  let { stocks, onSelect }: { stocks: StockRow[]; onSelect: (ticker: string) => void } = $props();

  let gainers = $derived(
    [...stocks]
      .filter(s => s.change_pct != null)
      .sort((a, b) => (b.change_pct ?? 0) - (a.change_pct ?? 0))
      .slice(0, 8)
  );

  let losers = $derived(
    [...stocks]
      .filter(s => s.change_pct != null)
      .sort((a, b) => (a.change_pct ?? 0) - (b.change_pct ?? 0))
      .slice(0, 8)
  );

  let recentReports = $derived(
    [...stocks]
      .filter(s => s.report_quarter != null && s.report_quarter !== '')
      .sort((a, b) => (b.report_quarter ?? '').localeCompare(a.report_quarter ?? ''))
      .slice(0, 6)
  );

  let sectorStats = $derived.by(() => {
    const map = new Map<string, { count: number; avgChange: number; totalChange: number }>();
    for (const s of stocks) {
      if (!s.sector || s.change_pct == null) continue;
      const entry = map.get(s.sector) ?? { count: 0, avgChange: 0, totalChange: 0 };
      entry.count++;
      entry.totalChange += s.change_pct;
      entry.avgChange = entry.totalChange / entry.count;
      map.set(s.sector, entry);
    }
    return [...map.entries()]
      .map(([sector, stats]) => ({ sector, ...stats }))
      .sort((a, b) => b.avgChange - a.avgChange);
  });

  function fmtPct(v: number): string {
    return `${v >= 0 ? '+' : ''}${v.toFixed(2)}%`;
  }
</script>

<div class="highlights">
  <!-- Header -->
  <header class="hl-header">
    <h1 class="hl-title">MARKET_HIGHLIGHTS</h1>
    <p class="hl-sub">Live Market Intelligence Feed // System Version 3.4.1</p>
  </header>

  <div class="hl-scroll">
    <div class="hl-grid">
      <!-- TOP GAINERS -->
      <section class="hl-card">
        <div class="hl-card-module">MODULE::041</div>
        <div class="hl-card-header">
          <h2 class="hl-card-title">TOP_GAINERS</h2>
          <span class="material-symbols-outlined hl-icon hl-icon--green">trending_up</span>
        </div>
        <table class="hl-table">
          <thead>
            <tr>
              <th>Ticker</th>
              <th class="text-right">Price</th>
              <th class="text-right">Change %</th>
            </tr>
          </thead>
          <tbody>
            {#each gainers as stock (stock.ticker)}
              <tr onclick={() => onSelect(stock.ticker)}>
                <td>
                  <span class="ticker-link">{stock.ticker}</span>
                  <span class="ticker-name">{stock.name}</span>
                </td>
                <td class="text-right">{stock.price?.toFixed(2) ?? '—'}</td>
                <td class="text-right text-green">{fmtPct(stock.change_pct ?? 0)}</td>
              </tr>
            {/each}
          </tbody>
        </table>
      </section>

      <!-- TOP LOSERS -->
      <section class="hl-card">
        <div class="hl-card-module hl-card-module--red">MODULE::042</div>
        <div class="hl-card-header">
          <h2 class="hl-card-title">TOP_LOSERS</h2>
          <span class="material-symbols-outlined hl-icon hl-icon--red">trending_down</span>
        </div>
        <table class="hl-table">
          <thead>
            <tr>
              <th>Ticker</th>
              <th class="text-right">Price</th>
              <th class="text-right">Change %</th>
            </tr>
          </thead>
          <tbody>
            {#each losers as stock (stock.ticker)}
              <tr onclick={() => onSelect(stock.ticker)}>
                <td>
                  <span class="ticker-link">{stock.ticker}</span>
                  <span class="ticker-name">{stock.name}</span>
                </td>
                <td class="text-right">{stock.price?.toFixed(2) ?? '—'}</td>
                <td class="text-right text-red">{fmtPct(stock.change_pct ?? 0)}</td>
              </tr>
            {/each}
          </tbody>
        </table>
      </section>

      <!-- LATEST REPORTS -->
      <section class="hl-card hl-card--wide">
        <div class="hl-card-header">
          <h2 class="hl-card-title">LATEST_REPORTS</h2>
          <span class="hl-card-meta">SORT: CHRONOLOGICAL</span>
        </div>
        <div class="report-list">
          {#each recentReports as stock (stock.ticker)}
            <button class="report-row" onclick={() => onSelect(stock.ticker)}>
              <div class="report-info">
                <span class="report-ticker">{stock.ticker} // {stock.report_quarter}</span>
                <span class="report-name">{stock.name}</span>
              </div>
              <div class="report-price">
                <span class="report-price-label">PRICE</span>
                <span class="report-price-val">{stock.price?.toFixed(2) ?? '—'}</span>
              </div>
            </button>
          {/each}
        </div>
      </section>

      <!-- SECTOR HEATMAP -->
      <section class="hl-card hl-card--narrow">
        <div class="hl-card-header">
          <h2 class="hl-card-title">SECTOR_HEATMAP</h2>
        </div>
        <div class="sector-list">
          {#each sectorStats as s (s.sector)}
            <div class="sector-item">
              <div class="sector-row-header">
                <span class="sector-name">{s.sector.toUpperCase()}</span>
                <span class="sector-change" class:text-green={s.avgChange >= 0} class:text-red={s.avgChange < 0} class:text-dim={s.avgChange === 0}>
                  {fmtPct(s.avgChange)}
                </span>
              </div>
              <div class="sector-bar-track">
                {#if s.avgChange >= 0}
                  <div class="sector-bar sector-bar--green" style="width: {Math.min(s.avgChange * 30, 100)}%"></div>
                {:else}
                  <div class="sector-bar sector-bar--red" style="width: {Math.min(Math.abs(s.avgChange) * 30, 100)}%; margin-left: auto;"></div>
                {/if}
              </div>
            </div>
          {/each}
        </div>
      </section>
    </div>
  </div>
</div>

<style>
  .highlights {
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow: hidden;
    background: var(--bg);
  }

  /* Header */
  .hl-header {
    padding: 24px 32px 16px;
    border-left: 4px solid var(--accent);
    margin: 32px 32px 0;
  }
  .hl-title {
    font-family: var(--font-heading);
    font-size: 2rem;
    font-weight: 900;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: var(--text);
    margin-bottom: 8px;
  }
  .hl-sub {
    font-family: var(--font-mono);
    font-size: 12px;
    letter-spacing: 0.1em;
    color: var(--text-faint);
  }

  /* Scroll area */
  .hl-scroll {
    flex: 1;
    overflow-y: auto;
    padding: 32px;
  }

  /* Grid */
  .hl-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 32px;
  }

  /* Cards */
  .hl-card {
    background: var(--bg-surface);
    border: 1px solid rgba(255, 255, 255, 0.05);
    position: relative;
    overflow: hidden;
  }
  .hl-card--wide { grid-column: span 1; }
  .hl-card--narrow { grid-column: span 1; }

  .hl-card-module {
    position: absolute;
    top: 8px;
    right: 8px;
    font-family: var(--font-mono);
    font-size: 10px;
    color: rgba(1, 245, 160, 0.3);
  }
  .hl-card-module--red { color: rgba(255, 180, 171, 0.3); }

  .hl-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  }
  .hl-card-title {
    font-family: var(--font-heading);
    font-size: 14px;
    font-weight: 800;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--text);
  }
  .hl-card-meta {
    font-family: var(--font-mono);
    font-size: 10px;
    color: var(--text-faint);
  }
  .hl-icon { font-size: 16px; }
  .hl-icon--green { color: var(--positive); }
  .hl-icon--red { color: var(--negative); }

  /* Table */
  .hl-table {
    width: 100%;
    border-collapse: collapse;
    font-family: var(--font-mono);
    font-size: 12px;
  }
  .hl-table thead {
    background: var(--sidebar-bg);
  }
  .hl-table th {
    padding: 12px 16px;
    font-weight: 400;
    font-size: 10px;
    text-transform: uppercase;
    color: var(--text-faint);
  }
  .hl-table tbody tr {
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    cursor: pointer;
    transition: background 0.15s;
  }
  .hl-table tbody tr:hover { background: rgba(255, 255, 255, 0.05); }
  .hl-table td {
    padding: 12px 16px;
    color: var(--text);
  }
  .ticker-link {
    color: var(--accent-soft);
    font-weight: 700;
  }
  .ticker-name {
    font-size: 10px;
    color: var(--text-faint);
    margin-left: 8px;
  }
  .text-right { text-align: right; }
  .text-green { color: var(--positive); font-weight: 700; }
  .text-red { color: var(--negative); font-weight: 700; }
  .text-dim { color: var(--text-faint); }

  /* Reports */
  .report-list {
    display: flex;
    flex-direction: column;
  }
  .report-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    background: none;
    border-left: none;
    border-right: none;
    border-top: none;
    color: inherit;
    cursor: pointer;
    width: 100%;
    text-align: left;
    transition: background 0.15s;
  }
  .report-row:last-child { border-bottom: none; }
  .report-row:hover { background: rgba(255, 255, 255, 0.05); }
  .report-info { display: flex; flex-direction: column; gap: 4px; }
  .report-ticker {
    font-family: var(--font-mono);
    font-size: 12px;
    font-weight: 700;
    color: var(--accent-soft);
    text-transform: uppercase;
  }
  .report-name {
    font-size: 10px;
    color: var(--text-faint);
  }
  .report-price { text-align: right; }
  .report-price-label {
    display: block;
    font-family: var(--font-mono);
    font-size: 10px;
    color: var(--text-faint);
  }
  .report-price-val {
    font-family: var(--font-mono);
    font-size: 12px;
    color: var(--text);
  }

  /* Sector Heatmap */
  .sector-list {
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 20px;
  }
  .sector-row-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 8px;
  }
  .sector-name {
    font-family: var(--font-mono);
    font-size: 10px;
    color: var(--text-secondary);
    letter-spacing: 0.05em;
  }
  .sector-change {
    font-family: var(--font-mono);
    font-size: 10px;
    font-weight: 700;
  }
  .sector-bar-track {
    height: 8px;
    background: var(--sidebar-bg);
    display: flex;
  }
  .sector-bar {
    height: 100%;
    min-width: 2px;
  }
  .sector-bar--green { background: var(--positive); }
  .sector-bar--red { background: var(--negative); }

  .material-symbols-outlined {
    font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
  }

  @media (max-width: 1024px) {
    .hl-grid { grid-template-columns: 1fr; }
    .hl-card--wide, .hl-card--narrow { grid-column: auto; }
  }
  @media (max-width: 768px) {
    .hl-scroll { padding: 16px; }
    .hl-header { margin: 16px 16px 0; padding: 16px 24px 12px; }
    .hl-title { font-size: 1.25rem; letter-spacing: 0.15em; }
  }
</style>
