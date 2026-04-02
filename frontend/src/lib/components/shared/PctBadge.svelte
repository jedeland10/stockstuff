<script lang="ts">
	let { value = null }: { value: number | null } = $props();

	function format(v: number): string {
		return (v >= 0 ? '+' : '') + v.toFixed(1) + '%';
	}
</script>

{#if value != null}
	<span class="pct-badge" class:positive={value >= 0} class:negative={value < 0}>
		{format(value)}
	</span>
{:else}
	<span class="dim">—</span>
{/if}

<style>
	.pct-badge {
		display: inline-block;
		padding: 2px 8px;
		font-family: var(--font-mono);
		font-size: 12px;
		font-weight: 700;
	}
	.positive { background: var(--positive-bg); color: var(--positive); }
	.negative { background: var(--negative-bg); color: var(--negative); }
	.dim { color: var(--text-dim); }
</style>
