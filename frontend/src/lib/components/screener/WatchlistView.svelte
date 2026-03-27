<script lang="ts">
	import type { StockRow } from '$lib/api/types';
	import { watchlist } from '$lib/stores/watchlist';
	import { fmtLarge, fmtSignPct, fmt } from '$lib/utils/format';

	let { stocks, onSelect, selectedTicker }: {
		stocks: StockRow[];
		onSelect: (ticker: string) => void;
		selectedTicker: string | null;
	} = $props();

	let watchlistStocks = $derived(
		stocks.filter(s => $watchlist.has(s.ticker))
	);
</script>

<div class="watchlist">
	<div class="watchlist-header">
		<div>
			<h1 class="watchlist-title">WATCHLIST</h1>
			<p class="watchlist-sub">Your tracked stocks · {watchlistStocks.length} assets</p>
		</div>
	</div>

	{#if watchlistStocks.length === 0}
		<div class="empty-state">
			<span class="material-symbols-outlined empty-icon">visibility_off</span>
			<p class="empty-text">No stocks in your watchlist yet.</p>
			<p class="empty-hint">Use the star icon in the screener to add stocks.</p>
		</div>
	{:else}
		<div class="table-container">
			<table class="data-table">
				<thead>
					<tr>
						<th></th>
						<th>Name / Ticker</th>
						<th>Price</th>
						<th class="text-right">1D % Chg</th>
						<th class="text-right">1Y % Chg</th>
						<th class="text-right">MCAP</th>
						<th class="text-right">P/E</th>
						<th class="text-right">Div Yield</th>
						<th class="text-right">ROE %</th>
					</tr>
				</thead>
				<tbody>
					{#each watchlistStocks as s}
						{@const isSelected = selectedTicker === s.ticker}
						<tr class:selected={isSelected} onclick={() => onSelect(s.ticker)}>
							<td class="td-star">
								<button class="star-btn" onclick={(e) => { e.stopPropagation(); watchlist.toggle(s.ticker); }}>
									<span class="material-symbols-outlined star-icon" style="font-variation-settings: 'FILL' 1; color: #feb127;">
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
							<td class="mono text-right">{s.div_yield != null ? s.div_yield.toFixed(2) + '%' : '—'}</td>
							<td class="mono text-right" class:text-cyan={s.roe != null}>{s.roe != null ? s.roe.toFixed(1) + '%' : '—'}</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{/if}
</div>

<style>
	.watchlist {
		height: 100%;
		display: flex;
		flex-direction: column;
		background: #111417;
		overflow: hidden;
	}
	.watchlist-header {
		padding: 24px 24px 16px;
	}
	.watchlist-title {
		font-family: 'Manrope', system-ui, sans-serif;
		font-size: 1.875rem;
		font-weight: 800;
		letter-spacing: -0.04em;
		color: #e1e2e7;
	}
	.watchlist-sub {
		font-family: 'JetBrains Mono', monospace;
		font-size: 10px;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		color: #64748b;
		margin-top: 4px;
	}

	.empty-state {
		flex: 1;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		gap: 12px;
	}
	.empty-icon { font-size: 48px; color: #323538; }
	.empty-text { font-size: 16px; color: #64748b; font-weight: 600; }
	.empty-hint { font-size: 13px; color: #4a5568; }

	.table-container {
		flex: 1;
		overflow: auto;
		background: #1d2023;
		border: 1px solid rgba(50, 53, 56, 0.3);
		margin: 0 24px 24px;
	}
	.data-table {
		width: 100%;
		border-collapse: collapse;
		text-align: left;
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
		white-space: nowrap;
	}
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
	.td-star { padding: 12px 8px 12px 16px; width: 40px; }
	.star-btn {
		background: none;
		border: none;
		cursor: pointer;
		padding: 0;
		display: flex;
	}
	.star-icon { font-size: 18px; }
	.name-cell { display: flex; flex-direction: column; }
	.stock-name { font-size: 13px; font-weight: 700; color: #e1e2e7; }
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

	.material-symbols-outlined {
		font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
	}

	@media (max-width: 768px) {
		.watchlist-header { padding: 16px 12px 12px; }
		.watchlist-title { font-size: 1.25rem; }
		.table-container { margin: 0; }
		.data-table { min-width: 600px; }
	}
</style>
