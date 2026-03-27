<script lang="ts">
  import ScoreRanking from '$lib/components/screener/ScoreRanking.svelte';
  import { selectStock } from '$lib/stores/stockData';
</script>

<ScoreRanking onSelect={selectStock} />
