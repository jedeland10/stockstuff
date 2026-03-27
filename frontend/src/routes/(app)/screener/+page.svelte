<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import ScreenerView from '$lib/components/screener/ScreenerView.svelte';
  import { stocks, stockTotal, stockLoading, stockHasMore, loadScreener, loadMore, sortScreener, selectStock, exportCsv, ensureScreenerData } from '$lib/stores/stockData';
  import { selectedTicker } from '$lib/stores/screener';

  onMount(() => {
    ensureScreenerData();
    // Apply search from URL if present
    const search = $page.url.searchParams.get('search');
    if (search) {
      loadScreener({ country: null, sector: '', search });
    }
  });
</script>

<ScreenerView
  stocks={$stocks}
  total={$stockTotal}
  onFilter={loadScreener}
  onSelect={selectStock}
  selectedTicker={$selectedTicker}
  onLoadMore={loadMore}
  onSort={sortScreener}
  onExport={exportCsv}
  loading={$stockLoading}
  hasMore={$stockHasMore}
/>
