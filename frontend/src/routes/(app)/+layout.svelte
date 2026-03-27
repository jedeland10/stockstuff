<script lang="ts">
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import AppSidebar from '$lib/components/shell/AppSidebar.svelte';
  import AppTopbar from '$lib/components/shell/AppTopbar.svelte';
  import DetailPanel from '$lib/components/detail/DetailPanel.svelte';
  import { selectedTicker, companyData, chartData, activeTab } from '$lib/stores/screener';
  import { stockTotal, loadScreener, selectStock } from '$lib/stores/stockData';

  let { children } = $props();

  const PANEL_WIDTH_KEY = 'stonklens-panel-width';
  let panelWidth = $state((() => {
    try {
      const stored = localStorage.getItem(PANEL_WIDTH_KEY);
      if (stored) return Math.max(400, Math.min(Number(stored), window.innerWidth - 100));
    } catch {}
    return Math.round(window.innerWidth * 2 / 5);
  })());

  function handleGlobalSearch(query: string) {
    goto(`/screener?search=${encodeURIComponent(query)}`);
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
</script>

<svelte:head>
  <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet" />
  <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet" />
</svelte:head>

<div class="app-shell">
  <AppSidebar />

  <div class="main-area">
    <AppTopbar total={$stockTotal} onSearch={handleGlobalSearch} />
    <div class="content">
      {@render children()}
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
