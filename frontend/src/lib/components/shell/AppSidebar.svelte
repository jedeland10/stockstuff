<script lang="ts">
	import { page } from '$app/stores';
	import { watchlist } from '$lib/stores/watchlist';

	const navItems: { href: string; icon: string; label: string; iconFill?: boolean }[] = [
		{ href: '/dashboard', icon: 'dashboard', label: 'Dashboard', iconFill: true },
		{ href: '/screener', icon: 'filter_list', label: 'Screener' },
		{ href: '/watchlist', icon: 'visibility', label: 'Watchlist' },
		{ href: '/highlights', icon: 'trending_up', label: 'Highlights' },
		{ href: '/rankings', icon: 'leaderboard', label: 'Rankings' },
	];

	let currentPath = $derived($page.url.pathname);
</script>

<aside class="sidebar">
	<div class="sidebar-header">
		<div class="logo-row">
			<div class="logo-icon">
				<span class="material-symbols-outlined" style="font-variation-settings: 'FILL' 1; font-size: 20px; color: #001f28;">query_stats</span>
			</div>
			<span class="logo-text">StockLens</span>
		</div>
		<div class="logo-sub">
			<p class="sub-title">Command Center</p>
			<p class="sub-label">High-Velocity Intel</p>
		</div>
	</div>

	<nav class="sidebar-nav">
		{#each navItems as item}
			<a
				class="nav-item"
				class:active={currentPath === item.href}
				href={item.href}
			>
				<span
					class="material-symbols-outlined nav-icon"
					style={currentPath === item.href && item.iconFill ? "font-variation-settings: 'FILL' 1;" : ''}
				>{item.icon}</span>
				<span class="nav-label">{item.label}</span>
				{#if item.href === '/watchlist' && $watchlist.size > 0}
					<span class="nav-badge">{$watchlist.size}</span>
				{/if}
			</a>
		{/each}
	</nav>

	<div class="sidebar-footer">
		<a class="footer-link" href="/">
			<span class="material-symbols-outlined footer-icon">help</span>
			<span>Support</span>
		</a>
		<a class="footer-link" href="/">
			<span class="material-symbols-outlined footer-icon">code</span>
			<span>API</span>
		</a>
	</div>
</aside>

<style>
	.sidebar {
		width: 16rem;
		height: 100vh;
		background: #0b0e11;
		display: flex;
		flex-direction: column;
		flex-shrink: 0;
		border-right: 1px solid rgba(60, 73, 78, 0.15);
		z-index: 60;
	}

	.sidebar-header {
		padding: 32px 24px 0;
		margin-bottom: 40px;
	}
	.logo-row {
		display: flex;
		align-items: center;
		gap: 12px;
		margin-bottom: 16px;
	}
	.logo-icon {
		width: 32px;
		height: 32px;
		background: #00d1ff;
		display: flex;
		align-items: center;
		justify-content: center;
	}
	.logo-text {
		font-family: 'Manrope', system-ui, sans-serif;
		font-size: 18px;
		font-weight: 900;
		color: #00d1ff;
		letter-spacing: -0.05em;
		text-transform: uppercase;
	}
	.sub-title {
		font-family: 'Manrope', system-ui, sans-serif;
		font-weight: 700;
		font-size: 14px;
		color: #e1e2e7;
	}
	.sub-label {
		font-family: 'JetBrains Mono', monospace;
		font-size: 11px;
		letter-spacing: 0.15em;
		text-transform: uppercase;
		color: #64748b;
		margin-top: 2px;
	}

	.sidebar-nav {
		flex: 1;
		display: flex;
		flex-direction: column;
	}
	.nav-item {
		display: flex;
		align-items: center;
		gap: 12px;
		padding: 12px 24px;
		border-left: 4px solid transparent;
		color: #64748b;
		font-family: 'Inter', system-ui, sans-serif;
		font-size: 14px;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.2s;
		text-decoration: none;
	}
	.nav-item:hover {
		color: #cbd5e1;
		background: rgba(28, 31, 35, 0.5);
	}
	.nav-item.active {
		color: #00d1ff;
		border-left-color: #00d1ff;
		font-weight: 700;
	}
	.nav-icon { font-size: 20px; }
	.nav-badge {
		margin-left: auto;
		background: rgba(210, 153, 34, 0.15);
		color: #d29922;
		font-family: 'JetBrains Mono', monospace;
		font-size: 10px;
		font-weight: 700;
		padding: 2px 6px;
	}

	.sidebar-footer {
		margin-top: auto;
		padding: 24px;
		border-top: 1px solid rgba(60, 73, 78, 0.1);
	}
	.footer-link {
		display: flex;
		align-items: center;
		gap: 12px;
		padding: 8px 0;
		color: #64748b;
		text-decoration: none;
		font-size: 14px;
		transition: color 0.2s;
	}
	.footer-link:hover { color: #cbd5e1; }
	.footer-icon { font-size: 20px; }

	.material-symbols-outlined {
		font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
	}
</style>
