<script lang="ts">
  import { onMount } from 'svelte';
  import ScreenerFilters from '$lib/components/screener/ScreenerFilters.svelte';
  import ScreenerTable from '$lib/components/screener/ScreenerTable.svelte';
  import ScoreRanking from '$lib/components/screener/ScoreRanking.svelte';
  import MarketFeed from '$lib/components/screener/MarketFeed.svelte';
  import DetailPanel from '$lib/components/detail/DetailPanel.svelte';
  import { getScreener, getCompany, getChart } from '$lib/api/client';
  import { selectedTicker, companyData, chartData, activeTab } from '$lib/stores/screener';
  import { watchlist } from '$lib/stores/watchlist';
  import type { StockRow } from '$lib/api/types';

  let stocks = $state<StockRow[]>([]);
  let total = $state(0);
  let loading = $state(false);
  let hasMore = $state(true);
  const PANEL_WIDTH_KEY = 'stonklens-panel-width';
  let panelWidth = $state((() => {
    try {
      const stored = localStorage.getItem(PANEL_WIDTH_KEY);
      if (stored) return Math.max(400, Math.min(Number(stored), window.innerWidth - 100));
    } catch {}
    return Math.round(window.innerWidth * 2 / 5);
  })());
  let watchlistActive = $state(false);
  let rankingsActive = $state(false);
  let highlightsActive = $state(false);

  type ViewMode = 'screener' | 'rankings' | 'highlights';
  let viewMode = $derived<ViewMode>(
    highlightsActive ? 'highlights' : rankingsActive ? 'rankings' : 'screener'
  );

  const PAGE_SIZE = 100;
  let currentFilters = $state<{ country: string|null; sector: string; search: string }>({ country: null, sector: '', search: '' });
  let sortBy = $state('market_cap');
  let sortDir = $state<'asc' | 'desc'>('desc');

  let displayStocks = $derived(
    watchlistActive ? stocks.filter(s => $watchlist.has(s.ticker)) : stocks
  );
  let displayTotal = $derived(
    watchlistActive ? displayStocks.length : total
  );

  async function loadScreener(filters?: { country: string|null; sector: string; search: string }) {
    if (filters) {
      currentFilters = filters;
      stocks = [];
      // Switch back to screener view when filters are applied
      if (rankingsActive || highlightsActive) {
        rankingsActive = false;
        highlightsActive = false;
        updateUrl({ view: null });
      }
    }
    loading = true;
    const data = await getScreener({
      ...currentFilters,
      sort_by: sortBy,
      sort_dir: sortDir,
      limit: PAGE_SIZE,
      offset: filters ? 0 : stocks.length,
    });
    if (filters) {
      stocks = data.stocks;
    } else {
      stocks = [...stocks, ...data.stocks];
    }
    total = data.total;
    hasMore = stocks.length < total;
    loading = false;
  }

  async function loadMore() {
    if (loading || !hasMore) return;
    await loadScreener();
  }

  async function onSort(col: string, dir: 'asc' | 'desc') {
    sortBy = col;
    sortDir = dir;
    stocks = [];
    await loadScreener(currentFilters);
  }

  async function selectStock(ticker: string, pushState = true) {
    if ($selectedTicker === ticker) return;
    selectedTicker.set(ticker);
    activeTab.set('overview');

    if (pushState) updateUrl({ stock: ticker });

    const [cd, chart] = await Promise.all([
      getCompany(ticker),
      getChart(ticker, 'max'),
    ]);
    companyData.set(cd);
    chartData.set(chart);
  }

  async function toggleWatchlist() {
    watchlistActive = !watchlistActive;
    if (watchlistActive && hasMore) {
      // Load all remaining stocks so watchlist filter has the full dataset
      loading = true;
      while (stocks.length < total) {
        const data = await getScreener({
          ...currentFilters,
          sort_by: sortBy,
          sort_dir: sortDir,
          limit: PAGE_SIZE,
          offset: stocks.length,
        });
        stocks = [...stocks, ...data.stocks];
        total = data.total;
        if (data.stocks.length === 0) break;
      }
      hasMore = false;
      loading = false;
    }
  }

  async function exportCsv() {
    // Load all stocks before exporting
    if (hasMore) {
      loading = true;
      while (stocks.length < total) {
        const data = await getScreener({
          ...currentFilters,
          sort_by: sortBy,
          sort_dir: sortDir,
          limit: PAGE_SIZE,
          offset: stocks.length,
        });
        stocks = [...stocks, ...data.stocks];
        total = data.total;
        if (data.stocks.length === 0) break;
      }
      hasMore = false;
      loading = false;
    }

    const toExport = watchlistActive ? stocks.filter(s => $watchlist.has(s.ticker)) : stocks;
    const fields: { key: keyof StockRow; label: string }[] = [
      { key: 'name', label: 'Name' },
      { key: 'ticker', label: 'Ticker' },
      { key: 'country', label: 'Country' },
      { key: 'sector', label: 'Sector' },
      { key: 'industry', label: 'Industry' },
      { key: 'price', label: 'Price' },
      { key: 'change_pct', label: '1d Change' },
      { key: 'perf_1y', label: '1y Change' },
      { key: 'market_cap', label: 'Market Cap' },
      { key: 'pe', label: 'P/E' },
      { key: 'pb', label: 'P/B' },
      { key: 'ps', label: 'P/S' },
      { key: 'ev_ebitda', label: 'EV/EBITDA' },
      { key: 'div_yield', label: 'Div Yield' },
      { key: 'roe', label: 'ROE' },
      { key: 'margin', label: 'Margin' },
      { key: 'report_quarter', label: 'Report Quarter' },
    ];
    const header = fields.map(f => f.label).join(',');
    const rows = toExport.map(stock => {
      return fields.map(f => {
        const val = stock[f.key];
        if (val == null) return '';
        if (typeof val === 'string' && val.includes(',')) return `"${val}"`;
        return String(val);
      }).join(',');
    });
    const csv = [header, ...rows].join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `stonklens-${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }

  function toggleRankings() {
    rankingsActive = !rankingsActive;
    if (rankingsActive) highlightsActive = false;
    updateUrl({ view: rankingsActive ? 'rankings' : null });
  }

  async function toggleHighlights() {
    highlightsActive = !highlightsActive;
    if (highlightsActive) {
      rankingsActive = false;
      // Load all stocks for accurate highlights
      if (hasMore) {
        loading = true;
        while (stocks.length < total) {
          const data = await getScreener({
            ...currentFilters,
            sort_by: sortBy,
            sort_dir: sortDir,
            limit: PAGE_SIZE,
            offset: stocks.length,
          });
          stocks = [...stocks, ...data.stocks];
          total = data.total;
          if (data.stocks.length === 0) break;
        }
        hasMore = false;
        loading = false;
      }
    }
    updateUrl({ view: highlightsActive ? 'highlights' : null });
  }

  function onResize(e: MouseEvent) {
    e.preventDefault();
    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';

    function onMove(ev: MouseEvent) {
      panelWidth = Math.max(400, Math.min(window.innerWidth - ev.clientX, window.innerWidth - 100));
    }
    function onUp() {
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
      document.removeEventListener('mousemove', onMove);
      document.removeEventListener('mouseup', onUp);
      localStorage.setItem(PANEL_WIDTH_KEY, String(panelWidth));
    }
    document.addEventListener('mousemove', onMove);
    document.addEventListener('mouseup', onUp);
  }

  // URL sync
  function updateUrl(params: { stock?: string | null; view?: string | null }) {
    const url = new URL(window.location.href);
    if ('stock' in params) {
      if (params.stock) url.searchParams.set('stock', params.stock);
      else url.searchParams.delete('stock');
    }
    if ('view' in params) {
      if (params.view) url.searchParams.set('view', params.view);
      else url.searchParams.delete('view');
    }
    history.pushState({}, '', url.toString());
  }

  function readUrl() {
    const params = new URLSearchParams(window.location.search);
    return {
      stock: params.get('stock'),
      view: params.get('view'),
    };
  }

  // Clear URL stock param when panel is closed
  $effect(() => {
    if ($selectedTicker === null && mounted) {
      updateUrl({ stock: null });
    }
  });

  let mounted = false;

  onMount(() => {
    mounted = true;
    const { stock, view } = readUrl();

    // Restore view mode from URL
    if (view === 'rankings') { rankingsActive = true; highlightsActive = false; }
    else if (view === 'highlights') { highlightsActive = true; rankingsActive = false; }

    loadScreener(currentFilters);

    // Auto-select stock from URL after screener loads
    if (stock) {
      selectStock(stock, false);
    }

    // Handle browser back/forward
    window.addEventListener('popstate', () => {
      const { stock: s, view: v } = readUrl();
      rankingsActive = v === 'rankings';
      highlightsActive = v === 'highlights';
      if (s && s !== $selectedTicker) {
        selectStock(s, false);
      } else if (!s && $selectedTicker) {
        selectedTicker.set(null);
        companyData.set(null);
        chartData.set([]);
        activeTab.set('overview');
      }
    });
  });
</script>

<div class="app">
  <ScreenerFilters total={displayTotal} onFilter={loadScreener} {watchlistActive} onToggleWatchlist={toggleWatchlist} onExport={exportCsv} {rankingsActive} onToggleRankings={toggleRankings} {highlightsActive} onToggleHighlights={toggleHighlights} />

  <div class="main">
    <div class="table-panel">
      {#if viewMode === 'highlights'}
        <MarketFeed stocks={stocks} onSelect={selectStock} />
      {:else if viewMode === 'rankings'}
        <ScoreRanking onSelect={selectStock} />
      {:else}
        <ScreenerTable stocks={displayStocks} onSelect={selectStock} selectedTicker={$selectedTicker} onLoadMore={loadMore} {onSort} {loading} {hasMore} />
      {/if}
    </div>

    {#if $selectedTicker}
      <div class="detail-overlay" style="width:{panelWidth}px">
        <!-- svelte-ignore a11y_no_static_element_interactions -->
        <div class="resize-handle" onmousedown={onResize}></div>
        <DetailPanel />
      </div>
    {/if}
  </div>
</div>

<style>
  .app { display: flex; flex-direction: column; height: 100vh; }
  .main { position: relative; flex: 1; overflow: hidden; }
  .table-panel { position: absolute; inset: 0; overflow: hidden; display: flex; flex-direction: column; }

  .detail-overlay {
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;
    display: flex;
    flex-direction: column;
    background: var(--bg);
    border-left: 1px solid var(--border);
    z-index: 10;
    box-shadow: -8px 0 30px rgba(0, 0, 0, 0.5);
    animation: slide-in 0.2s ease-out;
  }

  @keyframes slide-in {
    from { opacity: 0; transform: translateX(20px); }
    to { opacity: 1; transform: translateX(0); }
  }

  .resize-handle {
    position: absolute;
    left: -4px;
    top: 0;
    width: 8px;
    height: 100%;
    cursor: col-resize;
    z-index: 20;
  }
  .resize-handle::after {
    content: '';
    position: absolute;
    left: 3px;
    top: 0;
    width: 2px;
    height: 100%;
    background: transparent;
    transition: background 0.15s;
  }
  .resize-handle:hover::after { background: var(--accent); }

  @media (max-width: 768px) {
    .detail-overlay {
      width: 100% !important;
      left: 0;
      box-shadow: none;
      border-left: none;
    }
    .resize-handle { display: none; }
  }
</style>
