<script lang="ts">
  import { onMount } from 'svelte';
  import MarketFeed from '$lib/components/screener/MarketFeed.svelte';
  import { stocks, stockLoading, ensureScreenerData, ensureAllStocksLoaded, selectStock } from '$lib/stores/stockData';

  onMount(async () => {
    ensureScreenerData();
    await ensureAllStocksLoaded();
  });
</script>

{#if $stockLoading && $stocks.length === 0}
  <div class="loading-state">
    <p class="loading-text">Loading market data...</p>
  </div>
{:else}
  <MarketFeed stocks={$stocks} onSelect={selectStock} />
{/if}

<style>
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
</style>
