<script lang="ts">
  import type { StockRow } from '$lib/api/types';
  import { fmtLarge } from '$lib/utils/format';

  let { stocks, onSelect, selectedTicker, onLoadMore, onSort, loading, hasMore }: {
    stocks: StockRow[];
    onSelect: (ticker: string) => void;
    selectedTicker: string | null;
    onLoadMore: () => void;
    onSort: (col: string, dir: 'asc' | 'desc') => void;
    loading: boolean;
    hasMore: boolean;
  } = $props();

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

  const cols = [
    { key: 'name', label: 'Name', width: '160px', align: 'left' },
    { key: 'ticker', label: 'Ticker', width: '95px', align: 'left' },
    { key: 'change_pct', label: '1d', width: '58px', align: 'right' },
    { key: 'perf_1y', label: '1y', width: '58px', align: 'right' },
    { key: 'div_yield', label: 'Div', width: '48px', align: 'right' },
    { key: 'pe', label: 'P/E', width: '52px', align: 'right' },
    { key: 'ps', label: 'P/S', width: '48px', align: 'right' },
    { key: 'pb', label: 'P/B', width: '48px', align: 'right' },
    { key: 'price', label: 'Price', width: '62px', align: 'right' },
    { key: 'report_quarter', label: 'Rep', width: '68px', align: 'left' },
    { key: 'sector', label: 'Sector', width: '120px', align: 'left' },
    { key: 'ev_ebitda', label: 'EV/EB', width: '52px', align: 'right' },
    { key: 'roe', label: 'ROE', width: '48px', align: 'right' },
    { key: 'margin', label: 'Mrgn', width: '52px', align: 'right' },
    { key: 'market_cap', label: 'MCap', width: '68px', align: 'right' },
  ];
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<div class="table-container" bind:this={tableEl} onscroll={handleScroll}>
  <table>
    <thead>
      <tr>
        {#each cols as col}
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
          <td class="name-cell">
            <span class="flag">{FLAG[stock.country ?? ''] ?? ''}</span>
            <span class="name-text">{stock.name ?? ''}</span>
          </td>
          <td class="ticker-cell">{stock.ticker}</td>
          <td class="num" class:text-positive={(stock.change_pct ?? 0) >= 0} class:text-negative={(stock.change_pct ?? 0) < 0}>
            {stock.change_pct != null ? (stock.change_pct >= 0 ? '+' : '') + stock.change_pct.toFixed(1) + '%' : '\u2014'}
          </td>
          <td class="num" class:text-positive={(stock.perf_1y ?? 0) >= 0} class:text-negative={(stock.perf_1y ?? 0) < 0}>
            {stock.perf_1y != null ? (stock.perf_1y >= 0 ? '+' : '') + stock.perf_1y.toFixed(1) + '%' : '\u2014'}
          </td>
          <td class="num">{stock.div_yield != null ? stock.div_yield.toFixed(1) : '\u2014'}</td>
          <td class="num">{stock.pe != null ? stock.pe.toFixed(1) : '\u2014'}</td>
          <td class="num">{stock.ps != null ? stock.ps.toFixed(1) : '\u2014'}</td>
          <td class="num">{stock.pb != null ? stock.pb.toFixed(1) : '\u2014'}</td>
          <td class="num">{stock.price != null ? Math.round(stock.price) : '\u2014'}</td>
          <td class="dim">{stock.report_quarter ?? '\u2014'}</td>
          <td class="truncate">{stock.sector ?? '\u2014'}</td>
          <td class="num">{stock.ev_ebitda != null ? stock.ev_ebitda.toFixed(1) : '\u2014'}</td>
          <td class="num">{stock.roe != null ? stock.roe.toFixed(0) + '%' : '\u2014'}</td>
          <td class="num">{stock.margin != null ? stock.margin.toFixed(0) + '%' : '\u2014'}</td>
          <td class="num">{fmtLarge(stock.market_cap)}</td>
        </tr>
      {/each}
    </tbody>
  </table>
  {#if loading}
    <div class="load-more">Loading...</div>
  {/if}
</div>

<style>
  .table-container { flex: 1; overflow: auto; }
  table { border-collapse: collapse; font-family: var(--font-mono); font-size: 12px; }
  thead { position: sticky; top: 0; z-index: 5; }
  th {
    background: var(--bg-surface); color: var(--text-muted); font-weight: 600; font-size: 10px;
    text-transform: uppercase; letter-spacing: 0.2px; padding: 3px 4px; border-bottom: 1px solid var(--border);
    cursor: pointer; white-space: nowrap; user-select: none;
  }
  th:hover { color: var(--text); }
  th.sorted { color: var(--accent); }
  .sort-arrow { font-size: 6px; margin-left: 2px; }

  td { padding: 2px 4px; border-bottom: 1px solid #1c212811; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  tr { height: 20px; cursor: pointer; transition: background 0.1s; }
  tr:hover { background: var(--bg-hover); }
  tr.selected { background: var(--accent-dim); }

  .name-cell { display: flex; align-items: center; gap: 3px; max-width: 140px; overflow: hidden; }
  .flag { font-size: 9px; flex-shrink: 0; }
  .name-text { overflow: hidden; text-overflow: ellipsis; }
  .ticker-cell { color: var(--accent); font-weight: 600; }
  .num { text-align: right; font-variant-numeric: tabular-nums; }
  .dim { color: var(--text-dim); }
  .truncate { max-width: 90px; overflow: hidden; text-overflow: ellipsis; }

  .load-more {
    text-align: center; padding: 12px; color: var(--text-dim);
    font-family: var(--font-mono); font-size: 11px;
  }
</style>
