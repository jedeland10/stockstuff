<script lang="ts">
  import { onMount } from 'svelte';
  import AppSidebar from '$lib/components/shell/AppSidebar.svelte';
  import AppTopbar from '$lib/components/shell/AppTopbar.svelte';
  import Dashboard from '$lib/components/dashboard/Dashboard.svelte';
  import ScreenerView from '$lib/components/screener/ScreenerView.svelte';
  import WatchlistView from '$lib/components/screener/WatchlistView.svelte';
  import ScoreRanking from '$lib/components/screener/ScoreRanking.svelte';
  import MarketFeed from '$lib/components/screener/MarketFeed.svelte';
  import DetailPanel from '$lib/components/detail/DetailPanel.svelte';
  import { getScreener, getCompany, getChart } from '$lib/api/client';
  import { selectedTicker, companyData, chartData, activeTab } from '$lib/stores/screener';
  import { currentView, type AppView } from '$lib/stores/navigation';
  import { watchlist } from '$lib/stores/watchlist';
  import type { StockRow } from '$lib/api/types';

  let stocks = $state<StockRow[]>([]);
  let total = $state(0);
  let loading = $state(false);
  let hasMore = $state(true);
  let screenerLoaded = $state(false);

  const PANEL_WIDTH_KEY = 'stonklens-panel-width';
  let panelWidth = $state((() => {
    try {
      const stored = localStorage.getItem(PANEL_WIDTH_KEY);
      if (stored) return Math.max(400, Math.min(Number(stored), window.innerWidth - 100));
    } catch {}
    return Math.round(window.innerWidth * 2 / 5);
  })());

  const PAGE_SIZE = 100;
  let currentFilters = $state<{ country: string|null; sector: string; search: string }>({ country: null, sector: '', search: '' });
  let sortBy = $state('market_cap');
  let sortDir = $state<'asc' | 'desc'>('desc');

  // stocks and total are shared state for screener/highlights/watchlist views

  async function loadScreener(filters?: { country: string|null; sector: string; search: string }) {
    if (filters) {
      currentFilters = filters;
      stocks = [];
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
    screenerLoaded = true;
  }

  async function ensureAllStocksLoaded() {
    if (!screenerLoaded) await loadScreener(currentFilters);
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

  async function exportCsv() {
    await ensureAllStocksLoaded();
    const toExport = $currentView === 'watchlist' ? stocks.filter(s => $watchlist.has(s.ticker)) : stocks;
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

  function handleGlobalSearch(query: string) {
    if ($currentView !== 'screener' && $currentView !== 'watchlist') {
      currentView.set('screener');
    }
    currentFilters = { ...currentFilters, search: query };
    loadScreener(currentFilters);
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

  // Sync URL when view changes
  $effect(() => {
    if (mounted) {
      updateUrl({ view: $currentView });
    }
  });

  // Clear URL stock param when panel is closed
  $effect(() => {
    if ($selectedTicker === null && mounted) {
      updateUrl({ stock: null });
    }
  });

  // Load screener data when switching to a view that needs it
  let lastTriggeredView = '';
  $effect(() => {
    const view = $currentView;
    if (!mounted || view === lastTriggeredView) return;

    if (view === 'screener' || view === 'watchlist' || view === 'highlights') {
      lastTriggeredView = view;
      if (stocks.length === 0 && !loading) {
        loadScreener(currentFilters).then(() => {
          if (view === 'highlights' || view === 'watchlist') {
            ensureAllStocksLoaded();
          }
        });
      } else if (view === 'highlights' || view === 'watchlist') {
        ensureAllStocksLoaded();
      }
    }
  });

  let mounted = false;

  onMount(() => {
    mounted = true;
    const { stock } = readUrl();

    // Load screener data if starting on a view that needs it
    if ($currentView !== 'dashboard') {
      loadScreener(currentFilters);
    }

    // Auto-select stock from URL after screener loads
    if (stock) {
      selectStock(stock, false);
    }

    // Handle browser back/forward
    window.addEventListener('popstate', () => {
      const { stock: s, view: v } = readUrl();
      if (v && ['dashboard', 'screener', 'watchlist', 'rankings', 'highlights'].includes(v)) {
        currentView.set(v as AppView);
      }
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
</script>

<svelte:head>
  <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet" />
  <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet" />
</svelte:head>

<div class="app-shell">
  <AppSidebar />

  <div class="main-area">
    <AppTopbar total={total} onSearch={handleGlobalSearch} />

    <div class="content">
      {#if $currentView === 'dashboard'}
        <Dashboard onSelectStock={(ticker) => selectStock(ticker)} />
      {:else if $currentView === 'screener'}
        <ScreenerView
          {stocks}
          {total}
          onFilter={loadScreener}
          onSelect={selectStock}
          selectedTicker={$selectedTicker}
          onLoadMore={loadMore}
          {onSort}
          onExport={exportCsv}
          {loading}
          {hasMore}
        />
      {:else if $currentView === 'watchlist'}
        <WatchlistView
          {stocks}
          onSelect={selectStock}
          selectedTicker={$selectedTicker}
        />
      {:else if $currentView === 'highlights'}
        {#if loading && stocks.length === 0}
          <div class="loading-state">
            <p class="loading-text">Loading market data...</p>
          </div>
        {:else}
          <MarketFeed stocks={stocks} onSelect={selectStock} />
        {/if}
      {:else if $currentView === 'rankings'}
        <ScoreRanking onSelect={selectStock} />
      {/if}
    </div>
  </div>

  {#if $selectedTicker}
    <div class="detail-overlay" style="width:{panelWidth}px">
      <!-- svelte-ignore a11y_no_static_element_interactions -->
      <div class="resize-handle" onmousedown={onResize}></div>
      <DetailPanel />
    </div>
  {/if}
</div>

<style>
  .app-shell {
    display: flex;
    height: 100vh;
    overflow: hidden;
    background: #111417;
  }

  .main-area {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    min-width: 0;
  }

  .content {
    flex: 1;
    position: relative;
    overflow: hidden;
  }

  .loading-state {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
  }
  .loading-text {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.1em;
  }

  .detail-overlay {
    position: fixed;
    top: 0;
    right: 0;
    bottom: 0;
    display: flex;
    flex-direction: column;
    background: var(--bg);
    border-left: 1px solid var(--border);
    z-index: 70;
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
