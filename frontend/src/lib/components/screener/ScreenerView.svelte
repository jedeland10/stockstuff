<script lang="ts">
	import { onMount } from 'svelte';
	import type { StockRow } from '$lib/api/types';
	import { getSectors, getCountries, getSectorAverages, type SectorAverages } from '$lib/api/client';
	import { watchlist } from '$lib/stores/watchlist';
	import { fmtLarge, fmtSignPct, fmt } from '$lib/utils/format';
	import { visibleColumns, ALL_COLUMNS, LOCKED_COLUMNS, PRESETS, type ColumnKey } from '$lib/stores/columns';

	let { stocks, total, onFilter, onSelect, selectedTicker, onLoadMore, onSort, onExport, loading, hasMore }: {
		stocks: StockRow[];
		total: number;
		onFilter: (f: { country: string|null; sector: string; search: string }) => void;
		onSelect: (ticker: string) => void;
		selectedTicker: string | null;
		onLoadMore: () => void;
		onSort: (col: string, dir: 'asc' | 'desc') => void;
		onExport: () => void;
		loading: boolean;
		hasMore: boolean;
	} = $props();

	let sectors = $state<string[]>([]);
	let countries = $state<string[]>([]);
	let sectorAvgs = $state<SectorAverages>({});
	let country = $state<string | null>(null);
	let sector = $state('');
	let search = $state('');
	let sortBy = $state('market_cap');
	let sortDir = $state<'asc' | 'desc'>('desc');
	let tableEl: HTMLDivElement;

	const FLAG: Record<string, string> = { SE: '🇸🇪', DK: '🇩🇰', FI: '🇫🇮', NO: '🇳🇴' };

	onMount(async () => {
		const [s, c, sa] = await Promise.all([getSectors(), getCountries(), getSectorAverages()]);
		sectors = s;
		countries = c;
		sectorAvgs = sa;
	});

	function emit() { onFilter({ country, sector, search }); }
	function setCountry(c: string | null) { country = c; emit(); }

	let searchTimeout: ReturnType<typeof setTimeout>;
	function handleSearch() {
		clearTimeout(searchTimeout);
		searchTimeout = setTimeout(emit, 300);
	}

	function toggleSort(col: string) {
		if (sortBy === col) {
			sortDir = sortDir === 'asc' ? 'desc' : 'asc';
		} else {
			sortBy = col;
			sortDir = 'desc';
		}
		onSort(sortBy, sortDir);
	}

	function handleScroll() {
		if (!tableEl) return;
		const { scrollTop, scrollHeight, clientHeight } = tableEl;
		if (scrollHeight - scrollTop - clientHeight < 200) {
			onLoadMore();
		}
	}

	// Active filters display
	let activeFilters = $derived.by(() => {
		const filters: { label: string; clear: () => void }[] = [];
		if (country) filters.push({ label: `Country: ${country}`, clear: () => setCountry(null) });
		if (sector) filters.push({ label: `Sector: ${sector}`, clear: () => { sector = ''; emit(); } });
		if (search) filters.push({ label: `Search: ${search}`, clear: () => { search = ''; emit(); } });
		return filters;
	});


	const columns: { key: string; label: string; align?: 'right' | 'center' }[] = [
		{ key: 'name', label: 'Name / Ticker' },
		{ key: 'price', label: 'Price' },
		{ key: 'change_pct', label: '1D % Chg', align: 'right' },
		{ key: 'perf_1y', label: '1Y % Chg', align: 'right' },
		{ key: 'market_cap', label: 'MCAP', align: 'right' },
		{ key: 'pe', label: 'P/E', align: 'right' },
		{ key: 'ps', label: 'P/S', align: 'right' },
		{ key: 'pb', label: 'P/B', align: 'right' },
		{ key: 'div_yield', label: 'Div Yield', align: 'right' },
		{ key: 'roe', label: 'ROE %', align: 'right' },
	];
</script>

<div class="screener">
	<!-- Header -->
	<div class="screener-header">
		<div>
			<h1 class="screener-title">STOCK_SCREENER</h1>
			<p class="screener-sub">Global Equity Markets Intelligence · Real-time Data Feed</p>
		</div>
		<div class="header-actions">
			<button class="action-btn" onclick={onExport}>
				<span class="material-symbols-outlined action-icon">ios_share</span>
				EXPORT CSV
			</button>
		</div>
	</div>

	<!-- Filter Console -->
	<section class="filter-console">
		<div class="filter-grid">
			<div class="filter-group">
				<label class="filter-label">Country</label>
				<div class="country-tabs">
					<button class="ctab" class:active={country === null} onclick={() => setCountry(null)}>All</button>
					{#each ['SE', 'DK', 'FI', 'NO'] as c}
						<button class="ctab" class:active={country === c} onclick={() => setCountry(c)}>
							<span class="tab-flag">{FLAG[c]}</span>{c}
						</button>
					{/each}
				</div>
			</div>
			<div class="filter-group">
				<label class="filter-label">Sector</label>
				<select class="filter-select" bind:value={sector} onchange={emit}>
					<option value="">ALL SECTORS</option>
					{#each sectors as s}
						<option value={s}>{s.toUpperCase()}</option>
					{/each}
				</select>
			</div>
			<div class="filter-group">
				<label class="filter-label">Search</label>
				<input class="filter-input" type="text" placeholder="TICKER, NAME..." bind:value={search} oninput={handleSearch} />
			</div>
		</div>
		{#if activeFilters.length > 0}
			<div class="active-filters">
				<span class="active-filters-label">Active Filters:</span>
				{#each activeFilters as f}
					<div class="filter-tag">
						<span>{f.label}</span>
						<button class="filter-tag-close" onclick={f.clear}>
							<span class="material-symbols-outlined" style="font-size: 14px;">close</span>
						</button>
					</div>
				{/each}
				<button class="clear-all" onclick={() => { country = null; sector = ''; search = ''; emit(); }}>Clear All</button>
			</div>
		{/if}
	</section>

	<!-- Data Table -->
	<div class="table-container" bind:this={tableEl} onscroll={handleScroll}>
		<table class="data-table">
			<thead>
				<tr>
					<th class="th-star"></th>
					{#each columns as col}
						<th
							class:text-right={col.align === 'right'}
							onclick={() => toggleSort(col.key)}
						>
							<span class="th-label">
								{col.label}
								{#if sortBy === col.key}
									<span class="sort-arrow">{sortDir === 'asc' ? '↑' : '↓'}</span>
								{/if}
							</span>
						</th>
					{/each}
				</tr>
			</thead>
			<tbody>
				{#each stocks as s}
					{@const isSelected = selectedTicker === s.ticker}
					<tr class:selected={isSelected} onclick={() => onSelect(s.ticker)}>
						<td class="td-star">
							<button class="star-btn" onclick={(e) => { e.stopPropagation(); watchlist.toggle(s.ticker); }}>
								<span class="material-symbols-outlined star-icon" style={$watchlist.has(s.ticker) ? "font-variation-settings: 'FILL' 1; color: #feb127;" : ''}>
									star
								</span>
							</button>
						</td>
						<td>
							<div class="name-cell">
								<span class="stock-name">{s.name}</span>
								<span class="stock-ticker">{s.ticker}</span>
							</div>
						</td>
						<td class="mono">{s.price != null ? s.price.toFixed(2) : '—'}</td>
						<td class="mono text-right">
							{#if s.change_pct != null}
								<span class="pct-badge" class:pct-positive={s.change_pct >= 0} class:pct-negative={s.change_pct < 0}>
									{fmtSignPct(s.change_pct)}
								</span>
							{:else}
								<span class="text-dim">—</span>
							{/if}
						</td>
						<td class="mono text-right" class:text-green={s.perf_1y != null && s.perf_1y >= 0} class:text-red={s.perf_1y != null && s.perf_1y < 0}>
							{fmtSignPct(s.perf_1y)}
						</td>
						<td class="mono text-right text-dim">{fmtLarge(s.market_cap)}</td>
						<td class="mono text-right">{fmt(s.pe, 1)}</td>
						<td class="mono text-right">{fmt(s.ps, 1)}</td>
						<td class="mono text-right">{fmt(s.pb, 1)}</td>
						<td class="mono text-right">{s.div_yield != null ? s.div_yield.toFixed(2) + '%' : '—'}</td>
						<td class="mono text-right" class:text-cyan={s.roe != null}>{s.roe != null ? s.roe.toFixed(1) + '%' : '—'}</td>
					</tr>
				{/each}
				{#if loading}
					{#each Array(5) as _}
						<tr class="skeleton-row">
							<td colspan={columns.length + 1}><div class="skeleton"></div></td>
						</tr>
					{/each}
				{/if}
			</tbody>
		</table>
	</div>

	<!-- Table Footer -->
	<div class="table-footer">
		<span class="footer-count">Showing {stocks.length} of {total} results</span>
		{#if hasMore && !loading}
			<button class="load-more-btn" onclick={onLoadMore}>Load more</button>
		{/if}
	</div>

</div>

<style>
	.screener {
		height: 100%;
		display: flex;
		flex-direction: column;
		background: #111417;
		overflow: hidden;
	}

	/* Header */
	.screener-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-end;
		padding: 24px 24px 16px;
		gap: 16px;
	}
	.screener-title {
		font-family: 'Manrope', system-ui, sans-serif;
		font-size: 1.875rem;
		font-weight: 800;
		letter-spacing: -0.04em;
		color: #e1e2e7;
	}
	.screener-sub {
		font-family: 'JetBrains Mono', monospace;
		font-size: 10px;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		color: #64748b;
		margin-top: 4px;
	}
	.header-actions { display: flex; gap: 8px; }
	.action-btn {
		display: flex;
		align-items: center;
		gap: 6px;
		padding: 8px 16px;
		background: #00d1ff;
		border: none;
		color: #003543;
		font-family: 'JetBrains Mono', monospace;
		font-size: 10px;
		font-weight: 900;
		letter-spacing: 0.15em;
		text-transform: uppercase;
		cursor: pointer;
		box-shadow: 0 0 15px rgba(0, 209, 255, 0.2);
		transition: opacity 0.15s;
	}
	.action-btn:hover { opacity: 0.85; }
	.action-icon { font-size: 14px; }

	/* Filter Console */
	.filter-console {
		background: #0b0e11;
		border-top: 1px solid rgba(50, 53, 56, 0.3);
		border-bottom: 1px solid rgba(50, 53, 56, 0.3);
		padding: 16px 24px;
	}
	.filter-grid {
		display: flex;
		gap: 16px;
		align-items: flex-end;
		flex-wrap: wrap;
	}
	.filter-group { display: flex; flex-direction: column; gap: 4px; }
	.filter-label {
		font-family: 'JetBrains Mono', monospace;
		font-size: 9px;
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.15em;
		color: #859399;
	}
	.country-tabs {
		display: flex;
		gap: 0;
	}
	.ctab {
		padding: 8px 12px;
		background: #272a2e;
		border: none;
		color: #94a3b8;
		font-family: 'Inter', system-ui, sans-serif;
		font-size: 12px;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.15s;
		display: flex;
		align-items: center;
		gap: 4px;
	}
	.ctab:first-child { border-left: none; }
	.ctab:hover { color: #e1e2e7; background: #323538; }
	.ctab.active { color: #00d1ff; background: rgba(0, 209, 255, 0.1); }
	.tab-flag { font-size: 12px; }
	.filter-select {
		background: #272a2e;
		border: none;
		color: #e1e2e7;
		padding: 8px 12px;
		font-size: 12px;
		cursor: pointer;
		min-width: 160px;
	}
	.filter-select:focus { outline: 1px solid #00d1ff; }
	.filter-input {
		background: #272a2e;
		border: none;
		color: #e1e2e7;
		padding: 8px 12px;
		font-family: 'JetBrains Mono', monospace;
		font-size: 12px;
		min-width: 180px;
	}
	.filter-input:focus { outline: 1px solid #00d1ff; }
	.filter-input::placeholder { color: #64748b; }

	.active-filters {
		display: flex;
		align-items: center;
		gap: 8px;
		margin-top: 12px;
		padding-top: 12px;
		border-top: 1px solid rgba(50, 53, 56, 0.2);
		flex-wrap: wrap;
	}
	.active-filters-label {
		font-family: 'JetBrains Mono', monospace;
		font-size: 9px;
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.15em;
		color: #859399;
	}
	.filter-tag {
		display: flex;
		align-items: center;
		gap: 4px;
		background: rgba(0, 209, 255, 0.1);
		border: 1px solid rgba(0, 209, 255, 0.2);
		padding: 2px 8px;
		font-family: 'JetBrains Mono', monospace;
		font-size: 10px;
		font-weight: 700;
		color: #a4e6ff;
	}
	.filter-tag-close {
		background: none;
		border: none;
		color: #a4e6ff;
		cursor: pointer;
		padding: 0;
		display: flex;
	}
	.clear-all {
		margin-left: auto;
		background: none;
		border: none;
		color: #ffb4ab;
		font-family: 'JetBrains Mono', monospace;
		font-size: 9px;
		font-weight: 700;
		text-transform: uppercase;
		cursor: pointer;
		transition: text-decoration 0.15s;
	}
	.clear-all:hover { text-decoration: underline; }

	/* Table */
	.table-container {
		flex: 1;
		overflow: auto;
		background: #1d2023;
		border: 1px solid rgba(50, 53, 56, 0.3);
		margin: 0 24px;
	}
	.data-table {
		width: 100%;
		border-collapse: collapse;
		text-align: left;
		min-width: 1000px;
	}
	.data-table thead {
		background: #191c1f;
		border-bottom: 1px solid rgba(50, 53, 56, 0.5);
		position: sticky;
		top: 0;
		z-index: 5;
	}
	.data-table th {
		padding: 14px 16px;
		font-family: 'JetBrains Mono', monospace;
		font-size: 10px;
		font-weight: 900;
		text-transform: uppercase;
		letter-spacing: 0.15em;
		color: #859399;
		cursor: pointer;
		user-select: none;
		white-space: nowrap;
		transition: color 0.15s;
	}
	.data-table th:hover { color: #00d1ff; }
	.th-star { width: 40px; cursor: default; }
	.th-label { display: flex; align-items: center; gap: 4px; }
	.sort-arrow { color: #00d1ff; }
	.data-table tbody tr {
		border-bottom: 1px solid rgba(50, 53, 56, 0.2);
		cursor: pointer;
		transition: background 0.15s;
	}
	.data-table tbody tr:hover { background: rgba(0, 209, 255, 0.05); }
	.data-table tbody tr.selected { background: rgba(0, 209, 255, 0.08); }
	.data-table td {
		padding: 12px 16px;
		font-size: 13px;
		color: #e1e2e7;
	}
	.td-star { padding: 12px 8px 12px 16px; }
	.star-btn {
		background: none;
		border: none;
		cursor: pointer;
		padding: 0;
		display: flex;
		color: #4a5568;
		transition: color 0.15s;
	}
	.star-btn:hover { color: #feb127; }
	.star-icon { font-size: 18px; }
	.name-cell { display: flex; flex-direction: column; }
	.stock-name {
		font-size: 13px;
		font-weight: 700;
		color: #e1e2e7;
	}
	.stock-ticker {
		font-family: 'JetBrains Mono', monospace;
		font-size: 10px;
		text-transform: uppercase;
		color: #859399;
	}
	.mono { font-family: 'JetBrains Mono', monospace; font-size: 13px; }
	.text-right { text-align: right; }
	.text-dim { color: #4a5568; }
	.text-green { color: #01f5a0; font-weight: 700; }
	.text-red { color: #ffb4ab; font-weight: 700; }
	.text-cyan { color: #a4e6ff; font-weight: 700; }
	.pct-badge {
		display: inline-block;
		padding: 2px 8px;
		font-size: 12px;
		font-weight: 700;
	}
	.pct-positive { background: rgba(1, 245, 160, 0.1); color: #01f5a0; }
	.pct-negative { background: rgba(147, 0, 10, 0.1); color: #ffb4ab; }

	.skeleton-row td { padding: 16px; }
	.skeleton {
		height: 16px;
		background: linear-gradient(90deg, #1d2023 25%, #272a2e 50%, #1d2023 75%);
		background-size: 200% 100%;
		animation: shimmer 1.5s infinite;
	}
	@keyframes shimmer {
		0% { background-position: 200% 0; }
		100% { background-position: -200% 0; }
	}

	/* Footer */
	.table-footer {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 12px 24px;
		background: #0b0e11;
	}
	.footer-count {
		font-family: 'JetBrains Mono', monospace;
		font-size: 10px;
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.15em;
		color: #859399;
	}
	.load-more-btn {
		padding: 6px 16px;
		background: #272a2e;
		border: none;
		color: #a4e6ff;
		font-family: 'JetBrains Mono', monospace;
		font-size: 10px;
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.1em;
		cursor: pointer;
		transition: background 0.15s;
	}
	.load-more-btn:hover { background: #323538; }


	.material-symbols-outlined {
		font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
	}

	@media (max-width: 768px) {
		.screener-header { flex-direction: column; align-items: flex-start; }
		.filter-grid { flex-direction: column; }
		.table-container { margin: 0 12px; }
	}
</style>
