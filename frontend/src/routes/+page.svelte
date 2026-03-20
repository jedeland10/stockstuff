<script lang="ts">
  import { onMount } from 'svelte';
  import ScreenerFilters from '$lib/components/screener/ScreenerFilters.svelte';
  import ScreenerTable from '$lib/components/screener/ScreenerTable.svelte';
  import DetailPanel from '$lib/components/detail/DetailPanel.svelte';
  import { getScreener, getCompany, getChart } from '$lib/api/client';
  import { selectedTicker, companyData, chartData, activeTab } from '$lib/stores/screener';
  import type { StockRow } from '$lib/api/types';

  let stocks = $state<StockRow[]>([]);
  let total = $state(0);
  let panelWidth = $state(Math.round(window.innerWidth * 2 / 5));

  async function loadScreener(filters: { country: string|null; sector: string; search: string } = { country: null, sector: '', search: '' }) {
    const data = await getScreener({ ...filters, limit: 500 });
    stocks = data.stocks;
    total = data.total;
  }

  async function selectStock(ticker: string) {
    if ($selectedTicker === ticker) return;
    selectedTicker.set(ticker);
    activeTab.set('overview');

    const [cd, chart] = await Promise.all([
      getCompany(ticker),
      getChart(ticker, '1y'),
    ]);
    companyData.set(cd);
    chartData.set(chart);
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
    }
    document.addEventListener('mousemove', onMove);
    document.addEventListener('mouseup', onUp);
  }

  onMount(() => { loadScreener(); });
</script>

<div class="app">
  <ScreenerFilters {total} onFilter={loadScreener} />

  <div class="main">
    <!-- Table always takes full width -->
    <div class="table-panel">
      <ScreenerTable {stocks} onSelect={selectStock} selectedTicker={$selectedTicker} />
    </div>

    <!-- Detail panel floats on top, anchored to right -->
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
    box-shadow: -4px 0 20px rgba(0, 0, 0, 0.4);
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
</style>
