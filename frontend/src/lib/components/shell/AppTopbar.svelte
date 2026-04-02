<script lang="ts">
	import { onMount } from 'svelte';
	import { theme } from '$lib/stores/theme';
	import { getLastUpdated } from '$lib/api/client';

	let { total = 0 }: {
		total?: number;
	} = $props();

	let lastUpdated = $state<string | null>(null);

	function timeAgo(iso: string): string {
		const diff = Date.now() - new Date(iso).getTime();
		const mins = Math.floor(diff / 60000);
		if (mins < 1) return 'just now';
		if (mins < 60) return `${mins}m ago`;
		const hrs = Math.floor(mins / 60);
		if (hrs < 24) return `${hrs}h ago`;
		const days = Math.floor(hrs / 24);
		return `${days}d ago`;
	}

	let updatedLabel = $derived(lastUpdated ? timeAgo(lastUpdated) : null);

	onMount(async () => {
		lastUpdated = await getLastUpdated();
	});
</script>

<header class="topbar">
	<div class="topbar-left"></div>

	<div class="topbar-right">
		<div class="topbar-actions">
			<button class="action-btn" title="Notifications">
				<span class="material-symbols-outlined">notifications</span>
			</button>
			<button class="action-btn" onclick={() => theme.toggle()} title={$theme === 'dark' ? 'Light mode' : 'Dark mode'}>
				<span class="material-symbols-outlined">
					{$theme === 'dark' ? 'light_mode' : 'dark_mode'}
				</span>
			</button>
		</div>

		<div class="topbar-status">
			<span class="status-count">{total} stocks</span>
			{#if updatedLabel}
				<span class="status-updated" title={lastUpdated ? new Date(lastUpdated).toLocaleString() : ''}>
					· {updatedLabel}
				</span>
			{/if}
		</div>
	</div>
</header>

<style>
	.topbar {
		display: flex;
		justify-content: space-between;
		align-items: center;
		width: 100%;
		height: 64px;
		padding: 0 32px;
		background: var(--topbar-bg);
		flex-shrink: 0;
		z-index: 50;
	}

	.topbar-right {
		display: flex;
		align-items: center;
		gap: 24px;
	}

	.topbar-actions {
		display: flex;
		gap: 8px;
	}
	.action-btn {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 36px;
		height: 36px;
		background: none;
		border: none;
		color: var(--text-faint);
		cursor: pointer;
		transition: color 0.2s;
	}
	.action-btn:hover { color: var(--accent-soft); }
	.action-btn .material-symbols-outlined { font-size: 22px; }

	.topbar-status {
		font-family: var(--font-mono);
		font-size: 11px;
		color: var(--text-faint);
		white-space: nowrap;
		padding-left: 24px;
		border-left: 1px solid var(--border-subtle);
	}
	.status-count { color: var(--text-muted); }
	.status-updated { opacity: 0.7; }

	.material-symbols-outlined {
		font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
	}

	@media (max-width: 768px) {
		.topbar {
			padding: 0 12px;
			height: 52px;
		}
		.search-box input {
			width: 120px;
		}
		.topbar-right { gap: 12px; }
		.topbar-status {
			display: none;
		}
	}
	@media (max-width: 480px) {
		.search-box input {
			width: 80px;
		}
		.topbar-actions { gap: 4px; }
		.action-btn { width: 32px; height: 32px; }
	}
</style>
