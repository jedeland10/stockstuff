<script lang="ts">
  import Dashboard from '$lib/components/dashboard/Dashboard.svelte';
  import { selectStock } from '$lib/stores/stockData';
</script>

<Dashboard onSelectStock={(ticker) => selectStock(ticker)} />
