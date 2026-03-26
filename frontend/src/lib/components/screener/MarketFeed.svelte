<script lang="ts">
  import type { StockRow } from '$lib/api/types';

  let { stocks, onSelect }: { stocks: StockRow[]; onSelect: (ticker: string) => void } = $props();

  const FLAG: Record<string, string> = { SE: '\u{1F1F8}\u{1F1EA}', DK: '\u{1F1E9}\u{1F1F0}', FI: '\u{1F1EB}\u{1F1EE}', NO: '\u{1F1F3}\u{1F1F4}' };

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
      .slice(0, 10)
  );

  // Sector breakdown
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
</script>

<div class="feed-container">
  <div class="feed-header">
    <h2 class="feed-title">Market Highlights</h2>
    <span class="feed-subtitle">Today's movers, recent reports, and sector performance</span>
  </div>

  <div class="feed-scroll">
    <div class="feed-grid">
      <!-- Top Gainers -->
      <section class="feed-card">
        <h3 class="card-title positive-title">Top Gainers</h3>
        <div class="mover-list">
          {#each gainers as stock (stock.ticker)}
            <button class="mover-row" onclick={() => onSelect(stock.ticker)}>
              <span class="mover-flag">{FLAG[stock.country ?? ''] ?? ''}</span>
              <span class="mover-name">{stock.name}</span>
              <span class="mover-ticker">{stock.ticker}</span>
              <span class="mover-change text-positive">+{stock.change_pct?.toFixed(1)}%</span>
            </button>
          {/each}
        </div>
      </section>

      <!-- Top Losers -->
      <section class="feed-card">
        <h3 class="card-title negative-title">Top Losers</h3>
        <div class="mover-list">
          {#each losers as stock (stock.ticker)}
            <button class="mover-row" onclick={() => onSelect(stock.ticker)}>
              <span class="mover-flag">{FLAG[stock.country ?? ''] ?? ''}</span>
              <span class="mover-name">{stock.name}</span>
              <span class="mover-ticker">{stock.ticker}</span>
              <span class="mover-change text-negative">{stock.change_pct?.toFixed(1)}%</span>
            </button>
          {/each}
        </div>
      </section>

      <!-- Recent Reports -->
      <section class="feed-card">
        <h3 class="card-title">Latest Reports</h3>
        <div class="mover-list">
          {#each recentReports as stock (stock.ticker)}
            <button class="mover-row" onclick={() => onSelect(stock.ticker)}>
              <span class="mover-flag">{FLAG[stock.country ?? ''] ?? ''}</span>
              <span class="mover-name">{stock.name}</span>
              <span class="mover-ticker">{stock.ticker}</span>
              <span class="report-quarter">{stock.report_quarter}</span>
            </button>
          {/each}
        </div>
      </section>

      <!-- Sector Performance -->
      <section class="feed-card">
        <h3 class="card-title">Sector Performance</h3>
        <div class="sector-list">
          {#each sectorStats as s (s.sector)}
            <div class="sector-row">
              <span class="sector-name">{s.sector}</span>
              <span class="sector-count">{s.count}</span>
              <div class="sector-bar-wrap">
                <div class="sector-bar"
                  style="width:{Math.min(Math.abs(s.avgChange) * 20, 100)}%;background:{s.avgChange >= 0 ? 'var(--positive)' : 'var(--negative)'};{s.avgChange >= 0 ? 'margin-left:50%' : `margin-left:${50 - Math.min(Math.abs(s.avgChange) * 20, 50)}%`}">
                </div>
              </div>
              <span class="sector-change" class:text-positive={s.avgChange >= 0} class:text-negative={s.avgChange < 0}>
                {s.avgChange >= 0 ? '+' : ''}{s.avgChange.toFixed(2)}%
              </span>
            </div>
          {/each}
        </div>
      </section>
    </div>
  </div>
</div>

<style>
  .feed-container {
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow: hidden;
  }
  .feed-header {
    padding: 16px 20px 12px;
    background: var(--bg-surface);
    border-bottom: 1px solid var(--border);
    flex-shrink: 0;
  }
  .feed-title {
    font-size: 16px;
    font-weight: 700;
    margin-bottom: 2px;
  }
  .feed-subtitle {
    font-size: 12px;
    color: var(--text-dim);
  }

  .feed-scroll {
    flex: 1;
    overflow-y: auto;
    padding: 16px 20px;
  }
  .feed-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }

  .feed-card {
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px;
    overflow: hidden;
  }
  .card-title {
    font-family: var(--font-mono);
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.4px;
    color: var(--text-muted);
    margin-bottom: 10px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border);
  }
  .positive-title { color: var(--positive); }
  .negative-title { color: var(--negative); }

  .mover-list {
    display: flex;
    flex-direction: column;
    gap: 1px;
  }
  .mover-row {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 8px;
    border-radius: 6px;
    cursor: pointer;
    transition: background 0.1s;
    background: none;
    border: none;
    color: var(--text);
    font-family: var(--font-mono);
    font-size: 12px;
    text-align: left;
    width: 100%;
  }
  .mover-row:hover { background: var(--bg-hover); }
  .mover-flag { font-size: 11px; flex-shrink: 0; }
  .mover-name {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-family: var(--font-ui);
    font-size: 12px;
  }
  .mover-ticker {
    color: var(--accent);
    font-weight: 600;
    font-size: 10px;
    flex-shrink: 0;
  }
  .mover-change {
    font-weight: 600;
    font-size: 11px;
    min-width: 50px;
    text-align: right;
    flex-shrink: 0;
  }
  .report-quarter {
    font-size: 10px;
    color: var(--text-dim);
    background: var(--bg);
    padding: 2px 6px;
    border-radius: 4px;
    flex-shrink: 0;
  }

  .sector-list {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  .sector-row {
    display: grid;
    grid-template-columns: 1fr 24px 80px 54px;
    align-items: center;
    gap: 6px;
    padding: 4px 0;
  }
  .sector-name {
    font-size: 11px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .sector-count {
    font-family: var(--font-mono);
    font-size: 9px;
    color: var(--text-dim);
    text-align: center;
  }
  .sector-bar-wrap {
    height: 6px;
    background: var(--bg);
    border-radius: 3px;
    overflow: hidden;
    position: relative;
  }
  .sector-bar {
    height: 100%;
    border-radius: 3px;
    min-width: 2px;
    position: absolute;
    top: 0;
  }
  .sector-change {
    font-family: var(--font-mono);
    font-size: 11px;
    font-weight: 600;
    text-align: right;
  }

  @media (max-width: 768px) {
    .feed-grid { grid-template-columns: 1fr; }
    .feed-scroll { padding: 10px 12px; }
    .feed-header { padding: 12px; }
    .mover-row { font-size: 11px; }
  }
</style>
