<script lang="ts">
  import type { StockRow } from '$lib/api/types';
  import { fmtLarge } from '$lib/utils/format';
  import { watchlist } from '$lib/stores/watchlist';
  import { visibleColumns, type ColumnKey } from '$lib/stores/columns';

  let { stocks, onSelect, selectedTicker, onLoadMore, onSort, loading, hasMore }: {
    stocks: StockRow[];
    onSelect: (ticker: string) => void;
    selectedTicker: string | null;
    onLoadMore: () => void;
    onSort: (col: string, dir: 'asc' | 'desc') => void;
    loading: boolean;
    hasMore: boolean;
  } = $props();

  function toggleStar(e: MouseEvent, ticker: string) {
    e.stopPropagation();
    watchlist.toggle(ticker);
  }

  let sortBy = $state('market_cap');
  let sortDir = $state<'asc' | 'desc'>('desc');
  let tableEl: HTMLDivElement;

  function toggleSort(col: string) {
    if (sortBy === col) {
      sortDir = sortDir === 'asc' ? 'desc' : 'asc';
    } else {
      sortBy = col;
      sortDir = 'desc';
    }
    onSort(sortBy, sortDir);
  }

  function handleScroll() {
    if (!tableEl || loading || !hasMore) return;
    const { scrollTop, scrollHeight, clientHeight } = tableEl;
    if (scrollHeight - scrollTop - clientHeight < 200) {
      onLoadMore();
    }
  }

  const FLAG: Record<string, string> = { SE: '\u{1F1F8}\u{1F1EA}', DK: '\u{1F1E9}\u{1F1F0}', FI: '\u{1F1EB}\u{1F1EE}', NO: '\u{1F1F3}\u{1F1F4}' };

  type ColDef = {
    key: ColumnKey;
    label: string;
    width: string;
    align: 'left' | 'right';
    render: (stock: StockRow) => string;
    cellClass?: (stock: StockRow) => string;
  };

  const pctClass = (v: number | null) => (v ?? 0) >= 0 ? 'num text-positive' : 'num text-negative';
  const fmtPct = (v: number | null, decimals = 1) => v != null ? (v >= 0 ? '+' : '') + v.toFixed(decimals) + '%' : '\u2014';

  const allCols: ColDef[] = [
    { key: 'name', label: 'Name', width: '160px', align: 'left',
      render: () => '', cellClass: () => 'name-cell-wrap' }, // special rendering
    { key: 'ticker', label: 'Ticker', width: '95px', align: 'left',
      render: (s) => s.ticker, cellClass: () => 'ticker-cell' },
    { key: 'change_pct', label: '1d', width: '58px', align: 'right',
      render: (s) => fmtPct(s.change_pct), cellClass: (s) => pctClass(s.change_pct) },
    { key: 'perf_1y', label: '1y', width: '58px', align: 'right',
      render: (s) => fmtPct(s.perf_1y), cellClass: (s) => pctClass(s.perf_1y) },
    { key: 'div_yield', label: 'Div', width: '48px', align: 'right',
      render: (s) => s.div_yield != null ? s.div_yield.toFixed(1) : '\u2014', cellClass: () => 'num' },
    { key: 'pe', label: 'P/E', width: '52px', align: 'right',
      render: (s) => s.pe != null ? s.pe.toFixed(1) : '\u2014', cellClass: () => 'num' },
    { key: 'ps', label: 'P/S', width: '48px', align: 'right',
      render: (s) => s.ps != null ? s.ps.toFixed(1) : '\u2014', cellClass: () => 'num' },
    { key: 'pb', label: 'P/B', width: '48px', align: 'right',
      render: (s) => s.pb != null ? s.pb.toFixed(1) : '\u2014', cellClass: () => 'num' },
    { key: 'price', label: 'Price', width: '62px', align: 'right',
      render: (s) => s.price != null ? s.price.toFixed(2) : '\u2014', cellClass: () => 'num' },
    { key: 'report_quarter', label: 'Rep', width: '68px', align: 'left',
      render: (s) => s.report_quarter ?? '\u2014', cellClass: () => 'dim' },
    { key: 'sector', label: 'Sector', width: '120px', align: 'left',
      render: (s) => s.sector ?? '\u2014', cellClass: () => 'truncate' },
    { key: 'ev_ebitda', label: 'EV/EB', width: '52px', align: 'right',
      render: (s) => s.ev_ebitda != null ? s.ev_ebitda.toFixed(1) : '\u2014', cellClass: () => 'num' },
    { key: 'roe', label: 'ROE', width: '48px', align: 'right',
      render: (s) => s.roe != null ? s.roe.toFixed(0) + '%' : '\u2014', cellClass: () => 'num' },
    { key: 'margin', label: 'Mrgn', width: '52px', align: 'right',
      render: (s) => s.margin != null ? s.margin.toFixed(0) + '%' : '\u2014', cellClass: () => 'num' },
    { key: 'market_cap', label: 'MCap', width: '68px', align: 'right',
      render: (s) => fmtLarge(s.market_cap), cellClass: () => 'num' },
  ];

  // Build a map for O(1) lookup
  const colMap = new Map(allCols.map(c => [c.key, c]));

  // Derive visible columns in order, preserving the allCols order
  let cols = $derived(
    allCols.filter(c => $visibleColumns.includes(c.key))
  );
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<div class="table-container" bind:this={tableEl} onscroll={handleScroll}>
  <table>
    <thead>
      <tr>
        <th class="star-col" style="width:28px"></th>
        {#each cols as col (col.key)}
          <th style="width:{col.width};text-align:{col.align}" onclick={() => toggleSort(col.key)}
              class:sorted={sortBy === col.key}>
            {col.label}
            {#if sortBy === col.key}<span class="sort-arrow">{sortDir === 'asc' ? '\u25B2' : '\u25BC'}</span>{/if}
          </th>
        {/each}
      </tr>
    </thead>
    <tbody>
      {#each stocks as stock (stock.ticker)}
        <tr class:selected={selectedTicker === stock.ticker} onclick={() => onSelect(stock.ticker)}>
          <td class="star-cell">
            <button class="star-btn" class:starred={$watchlist.has(stock.ticker)} onclick={(e) => toggleStar(e, stock.ticker)} aria-label="Toggle watchlist">
              <svg viewBox="0 0 16 16" width="13" height="13" fill={$watchlist.has(stock.ticker) ? 'var(--gold)' : 'none'} stroke={$watchlist.has(stock.ticker) ? 'var(--gold)' : 'currentColor'} stroke-width="1.3">
                <path d="M8 1.5l2 4.1 4.5.6-3.3 3.2.8 4.5L8 11.6l-4 2.3.8-4.5L1.5 6.2 6 5.6z"/>
              </svg>
            </button>
          </td>
          {#each cols as col (col.key)}
            {#if col.key === 'name'}
              <td class="name-cell">
                <span class="flag">{FLAG[stock.country ?? ''] ?? ''}</span>
                <span class="name-text">{stock.name ?? ''}</span>
              </td>
            {:else}
              <td class={col.cellClass?.(stock) ?? ''} style="text-align:{col.align}">{col.render(stock)}</td>
            {/if}
          {/each}
        </tr>
      {/each}
      {#if loading && stocks.length === 0}
        {#each Array(20) as _}
          <tr class="skeleton-row">
            <td></td>
            {#each cols as col (col.key)}
              <td>
                <div class="skeleton" style="width:{col.key === 'name' ? '80%' : col.key === 'sector' ? '70%' : '60%'}"></div>
              </td>
            {/each}
          </tr>
        {/each}
      {/if}
    </tbody>
  </table>
  {#if loading && stocks.length > 0}
    <div class="load-more">
      <div class="load-spinner"></div>
      Loading more...
    </div>
  {/if}
</div>

<style>
  .table-container { flex: 1; overflow: auto; }
  table { border-collapse: collapse; font-family: var(--font-mono); font-size: 12px; width: 100%; }
  thead { position: sticky; top: 0; z-index: 5; }
  th {
    background: var(--bg-surface);
    color: var(--text-muted);
    font-weight: 600;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.3px;
    padding: 8px 6px;
    border-bottom: 2px solid var(--border);
    cursor: pointer;
    white-space: nowrap;
    user-select: none;
    transition: color 0.15s;
  }
  th:hover { color: var(--text); }
  th.sorted { color: var(--accent); }
  .sort-arrow { font-size: 7px; margin-left: 3px; opacity: 0.8; }

  td {
    padding: 5px 6px;
    border-bottom: 1px solid rgba(48, 54, 61, 0.3);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  tbody tr {
    height: 28px;
    cursor: pointer;
    transition: background 0.1s;
  }
  tbody tr:hover { background: var(--bg-hover); }
  tbody tr.selected {
    background: var(--accent-dim);
    border-left: 2px solid var(--accent);
  }
  tbody tr.selected td:first-child { padding-left: 4px; }

  .star-col { cursor: default !important; }
  .star-cell { text-align: center; padding: 0 2px !important; }
  .star-btn {
    background: none;
    border: none;
    cursor: pointer;
    color: var(--text-dim);
    padding: 2px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 4px;
    transition: all 0.15s;
    opacity: 0.3;
  }
  .star-btn:hover { opacity: 1; color: var(--gold); }
  .star-btn.starred { opacity: 1; }
  tbody tr:hover .star-btn { opacity: 0.7; }
  tbody tr:hover .star-btn.starred, .star-btn.starred { opacity: 1; }

  .name-cell { display: flex; align-items: center; gap: 4px; max-width: 160px; overflow: hidden; }
  .flag { font-size: 10px; flex-shrink: 0; }
  .name-text { overflow: hidden; text-overflow: ellipsis; }
  :global(.ticker-cell) { color: var(--accent); font-weight: 600; }
  :global(.num) { text-align: right; font-variant-numeric: tabular-nums; }
  :global(.dim) { color: var(--text-dim); }
  :global(.truncate) { max-width: 100px; overflow: hidden; text-overflow: ellipsis; }

  .skeleton-row {
    pointer-events: none;
  }
  .skeleton {
    height: 10px;
    border-radius: 4px;
    background: linear-gradient(90deg, var(--bg-hover) 25%, var(--bg-elevated) 50%, var(--bg-hover) 75%);
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite ease-in-out;
  }

  @keyframes shimmer {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
  }

  .load-more {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 16px;
    color: var(--text-dim);
    font-family: var(--font-mono);
    font-size: 11px;
  }
  .load-spinner {
    width: 14px;
    height: 14px;
    border: 2px solid var(--border);
    border-top-color: var(--accent);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
</style>
