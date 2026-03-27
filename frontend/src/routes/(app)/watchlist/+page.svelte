<script lang="ts">
  import { onMount } from 'svelte';
  import WatchlistView from '$lib/components/screener/WatchlistView.svelte';
  import { stocks, ensureAllStocksLoaded, ensureScreenerData, selectStock } from '$lib/stores/stockData';
  import { selectedTicker } from '$lib/stores/screener';

  onMount(() => {
    ensureScreenerData();
    ensureAllStocksLoaded();
  });
</script>

<WatchlistView
  stocks={$stocks}
  onSelect={selectStock}
  selectedTicker={$selectedTicker}
/>
