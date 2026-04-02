<script lang="ts">
	import { onMount } from 'svelte';
	import { getScreener, getLastUpdated, getSectorAverages, getMagicFormulaRanking, getFScoreRanking, type MagicFormulaEntry, type FScoreEntry, type SectorAverages } from '$lib/api/client';
	import type { StockRow } from '$lib/api/types';

	let { onSelectStock }: { onSelectStock: (ticker: string) => void } = $props();

	let stocks = $state<StockRow[]>([]);
	let topGainers = $state<StockRow[]>([]);
	let topLosers = $state<StockRow[]>([]);
	let topByMcap = $state<StockRow[]>([]);
	let sectorAvgs = $state<SectorAverages>({});
	let magicTop = $state<MagicFormulaEntry[]>([]);
	let fscoreTop = $state<FScoreEntry[]>([]);
	let lastUpdated = $state<string | null>(null);
	let totalStocks = $state(0);

	function formatMcap(val: number | null): string {
		if (val == null) return 'N/A';
		if (val >= 1e12) return `${(val / 1e12).toFixed(2)}T`;
		if (val >= 1e9) return `${(val / 1e9).toFixed(0)}B`;
		if (val >= 1e6) return `${(val / 1e6).toFixed(0)}M`;
		return val.toFixed(0);
	}

	function formatPct(val: number | null): string {
		if (val == null) return 'N/A';
		return `${val >= 0 ? '+' : ''}${val.toFixed(2)}%`;
	}

	type SectorPeriod = '1d' | '1w' | '1m' | '1y';
	type SectorSentiment = { sector: string; avgChange: number; breadth: number; count: number; label: string };

	let sectorPeriod = $state<SectorPeriod>('1d');

	function getChangeForPeriod(s: StockRow, period: SectorPeriod): number | null {
		switch (period) {
			case '1d': return s.change_pct;
			case '1w': return s.perf_1w;
			case '1m': return s.perf_1m;
			case '1y': return s.perf_1y;
		}
	}

	function computeSectorSentiment(stocks: StockRow[], period: SectorPeriod): SectorSentiment[] {
		const grouped: Record<string, { changes: number[]; total: number }> = {};
		for (const s of stocks) {
			const change = getChangeForPeriod(s, period);
			if (!s.sector || change == null) continue;
			if (!grouped[s.sector]) grouped[s.sector] = { changes: [], total: 0 };
			grouped[s.sector].changes.push(change);
			grouped[s.sector].total++;
		}
		return Object.entries(grouped)
			.filter(([, v]) => v.total >= 3)
			.map(([sector, { changes, total }]) => {
				const avgChange = changes.reduce((a, b) => a + b, 0) / changes.length;
				const advancing = changes.filter(c => c > 0).length;
				const breadth = advancing / total;
				let label: string;
				if (avgChange > 0 && breadth > 0.5) label = 'BULLISH';
				else if (avgChange < 0 && breadth < 0.5) label = 'BEARISH';
				else label = 'MIXED';
				return { sector, avgChange, breadth, count: total, label };
			})
			.sort((a, b) => Math.abs(b.avgChange) - Math.abs(a.avgChange));
	}

	onMount(async () => {
		const [screenerRes, lu, sa, mf, fs] = await Promise.all([
			getScreener({ sort_by: 'market_cap', sort_dir: 'desc', limit: 500 }),
			getLastUpdated(),
			getSectorAverages(),
			getMagicFormulaRanking(3),
			getFScoreRanking(3),
		]);

		stocks = screenerRes.stocks;
		totalStocks = screenerRes.total;
		lastUpdated = lu;
		sectorAvgs = sa;
		magicTop = mf;
		fscoreTop = fs;

		const withChange = stocks.filter(s => s.change_pct != null);
		topGainers = [...withChange].sort((a, b) => (b.change_pct ?? 0) - (a.change_pct ?? 0)).slice(0, 3);
		topLosers = [...withChange].sort((a, b) => (a.change_pct ?? 0) - (b.change_pct ?? 0)).slice(0, 3);
		topByMcap = stocks.slice(0, 5);
	});

	// Top 4 sectors by absolute change for selected period
	let topSectors = $derived.by(() => {
		return computeSectorSentiment(stocks, sectorPeriod).slice(0, 4);
	});
</script>

<div class="dashboard">
	<!-- Header -->
	<section class="dash-header">
		<div class="header-left">
			<h2 class="header-title">Market Intelligence Hub</h2>
			<p class="header-sub">Global Macro Snapshot · Live Data Stream</p>
		</div>
		<div class="header-metrics">
			<div class="metric-card metric-card--green">
				<p class="metric-label">Total Stocks</p>
				<p class="metric-value metric-value--green">{totalStocks}</p>
			</div>
			{#if lastUpdated}
				<div class="metric-card metric-card--cyan">
					<p class="metric-label">Last Update</p>
					<p class="metric-value metric-value--cyan">{new Date(lastUpdated).toLocaleTimeString()}</p>
				</div>
			{/if}
		</div>
	</section>

	<!-- Top Movers + Index Card -->
	<section class="movers-row">
		<!-- Gainers -->
		<div class="mover-card">
			<div class="mover-header">
				<h3 class="mover-title mover-title--green">Top Gainers</h3>
				<span class="material-symbols-outlined mover-icon mover-icon--green">trending_up</span>
			</div>
			<div class="mover-list">
				{#each topGainers as s}
					<button class="mover-row" onclick={() => onSelectStock(s.ticker)}>
						<span class="mover-ticker">{s.ticker}</span>
						<span class="mover-change mover-change--green">{formatPct(s.change_pct)}</span>
					</button>
				{/each}
			</div>
		</div>
		<!-- Losers -->
		<div class="mover-card">
			<div class="mover-header">
				<h3 class="mover-title mover-title--red">Top Losers</h3>
				<span class="material-symbols-outlined mover-icon mover-icon--red">trending_down</span>
			</div>
			<div class="mover-list">
				{#each topLosers as s}
					<button class="mover-row" onclick={() => onSelectStock(s.ticker)}>
						<span class="mover-ticker">{s.ticker}</span>
						<span class="mover-change mover-change--red">{formatPct(s.change_pct)}</span>
					</button>
				{/each}
			</div>
		</div>
		<!-- Summary Card -->
		<div class="summary-card">
			<div class="summary-left">
				<p class="summary-label">Market Overview</p>
				<p class="summary-value">{totalStocks} <span class="summary-unit">tracked</span></p>
				{#if topGainers.length > 0}
					<p class="summary-sub">
						Top mover: <span class="summary-highlight">{topGainers[0]?.ticker}</span>
						<span class="summary-highlight-pct">{formatPct(topGainers[0]?.change_pct)}</span>
					</p>
				{/if}
			</div>
			<div class="summary-sparkline">
				<svg viewBox="0 0 100 40" class="sparkline-svg">
					<path d="M0 35 L10 32 L20 34 L30 28 L40 25 L50 20 L60 22 L70 15 L80 18 L90 5 L100 10" fill="none" stroke="var(--accent)" stroke-width="2" />
					<path d="M0 35 L10 32 L20 34 L30 28 L40 25 L50 20 L60 22 L70 15 L80 18 L90 5 L100 10 L100 40 L0 40 Z" fill="url(#sparkGrad)" />
					<defs>
						<linearGradient id="sparkGrad" x1="0%" y1="0%" x2="0%" y2="100%">
							<stop offset="0%" stop-color="var(--accent)" stop-opacity="0.2" />
							<stop offset="100%" stop-color="var(--accent)" stop-opacity="0" />
						</linearGradient>
					</defs>
				</svg>
			</div>
		</div>
	</section>

	<!-- Sector Matrix + Deep Analysis -->
	<section class="intel-row">
		<!-- Sector Matrix -->
		<div class="sector-matrix">
			<div class="section-bar">
				<h3 class="section-label">Sector Intelligence Matrix</h3>
				<div class="period-toggle">
					{#each (['1d', '1w', '1m', '1y'] as const) as p}
						<button class="period-btn" class:active={sectorPeriod === p} onclick={() => sectorPeriod = p}>{p.toUpperCase()}</button>
					{/each}
				</div>
			</div>
			<div class="sector-grid">
				{#each topSectors as { sector, avgChange, breadth, count, label }}
					{@const isPositive = avgChange >= 0}
					<div class="sector-cell" class:sector-cell--positive={isPositive} class:sector-cell--negative={!isPositive} class:sector-cell--mixed={label === 'MIXED'}>
						<span class="sector-name">{sector}</span>
						<div class="sector-bottom">
							<p class="sector-change" class:sector-change--positive={isPositive} class:sector-change--negative={!isPositive}>
								{formatPct(avgChange)}
							</p>
							<p class="sector-breadth">{Math.round(breadth * 100)}% advancing · {count} stocks</p>
							<p class="sector-sentiment" class:sentiment--bullish={label === 'BULLISH'} class:sentiment--bearish={label === 'BEARISH'} class:sentiment--mixed={label === 'MIXED'}>{label}</p>
						</div>
					</div>
				{/each}
			</div>
		</div>

		<!-- Deep Analysis -->
		<div class="analysis-panel">
			<h3 class="section-label">Deep Analysis Filters</h3>
			<div class="analysis-cards">
				<div class="analysis-card">
					<div class="analysis-header">
						<p class="analysis-tag analysis-tag--cyan">Piotroski F-Score</p>
						<span class="analysis-badge">ALPHA</span>
					</div>
					{#if fscoreTop.length > 0}
						<div class="analysis-value-row">
							<span class="analysis-big">{fscoreTop[0].f_score}</span>
							<span class="analysis-unit">/ 9 POINTS</span>
						</div>
						<p class="analysis-desc">Top scorer: {fscoreTop[0].name} ({fscoreTop[0].ticker})</p>
					{/if}
				</div>
				<div class="analysis-card">
					<div class="analysis-header">
						<p class="analysis-tag analysis-tag--gold">Magic Formula Ranking</p>
					</div>
					{#if magicTop.length > 0}
						<div class="analysis-value-row">
							<span class="analysis-big">Top 3</span>
						</div>
						<p class="analysis-desc">
							{magicTop.map(m => m.ticker).join(', ')}
						</p>
					{/if}
				</div>
			</div>
		</div>
	</section>

	<!-- Compact Screener Table -->
	<section class="screener-preview">
		<div class="section-bar">
			<h3 class="section-label">Global Market Screener</h3>
		</div>
		<div class="preview-table-wrap">
			<table class="preview-table">
				<thead>
					<tr>
						<th>Ticker</th>
						<th>1D %</th>
						<th>1Y %</th>
						<th>Div Yield</th>
						<th>P/E</th>
						<th>P/S</th>
						<th class="text-right">MCAP</th>
						<th class="text-right">ROE</th>
					</tr>
				</thead>
				<tbody>
					{#each topByMcap as s}
						<tr onclick={() => onSelectStock(s.ticker)}>
							<td>
								<div class="ticker-cell">
									<span class="ticker-badge">{s.ticker.split('.')[0]?.substring(0, 5)}</span>
									<div>
										<p class="ticker-name">{s.name}</p>
										<p class="ticker-exchange">{s.country}</p>
									</div>
								</div>
							</td>
							<td class:text-green={s.change_pct != null && s.change_pct >= 0} class:text-red={s.change_pct != null && s.change_pct < 0}>
								{formatPct(s.change_pct)}
							</td>
							<td class:text-green={s.perf_1y != null && s.perf_1y >= 0} class:text-red={s.perf_1y != null && s.perf_1y < 0}>
								{formatPct(s.perf_1y)}
							</td>
							<td>{s.div_yield != null ? `${s.div_yield.toFixed(2)}%` : 'N/A'}</td>
							<td>{s.pe != null ? `${s.pe.toFixed(1)}x` : 'N/A'}</td>
							<td>{s.ps != null ? `${s.ps.toFixed(1)}x` : 'N/A'}</td>
							<td class="text-right">{formatMcap(s.market_cap)}</td>
							<td class="text-right text-cyan">{s.roe != null ? `${s.roe.toFixed(1)}%` : 'N/A'}</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	</section>

	<!-- Footer -->
	<footer class="dash-footer">
		<div class="footer-left">
			<div class="footer-status">
				<span class="status-dot"></span>
				<span>Server Status: Nominal</span>
			</div>
			{#if lastUpdated}
				<span>Last Update: <strong class="footer-time">{new Date(lastUpdated).toLocaleTimeString()}</strong></span>
			{/if}
		</div>
		<span class="footer-copy">&copy; 2024 STOCKLENS ANALYTICS. PROPRIETARY DATA ENGINE.</span>
	</footer>
</div>

<style>
	.dashboard {
		height: 100%;
		overflow-y: auto;
		padding: 32px;
		display: flex;
		flex-direction: column;
		gap: 32px;
		background: var(--bg);
	}

	/* Header */
	.dash-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-end;
	}
	.header-title {
		font-family: var(--font-heading);
		font-size: 1.875rem;
		font-weight: 900;
		letter-spacing: -0.03em;
		color: var(--text);
	}
	.header-sub {
		font-family: var(--font-mono);
		font-size: 12px;
		text-transform: uppercase;
		letter-spacing: 0.15em;
		color: var(--text-faint);
		margin-top: 4px;
	}
	.header-metrics { display: flex; gap: 8px; }
	.metric-card {
		padding: 12px 16px;
		background: var(--bg-surface);
	}
	.metric-card--green { border-left: 2px solid var(--positive); }
	.metric-card--cyan { border-left: 2px solid var(--accent); }
	.metric-label {
		font-family: var(--font-mono);
		font-size: 10px;
		text-transform: uppercase;
		color: var(--text-faint);
	}
	.metric-value {
		font-family: var(--font-heading);
		font-size: 18px;
		font-weight: 700;
	}
	.metric-value--green { color: var(--positive-soft); }
	.metric-value--cyan { color: var(--accent-soft); }

	/* Movers */
	.movers-row {
		display: grid;
		grid-template-columns: 1fr 1fr 2fr;
		gap: 16px;
	}
	.mover-card {
		background: var(--bg-elevated);
		padding: 24px;
		border-top: 1px solid var(--border-subtle);
	}
	.mover-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 16px;
	}
	.mover-title {
		font-family: var(--font-mono);
		font-size: 11px;
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.15em;
	}
	.mover-title--green { color: var(--positive-soft); }
	.mover-title--red { color: var(--negative); }
	.mover-icon { font-size: 16px; }
	.mover-icon--green { color: var(--positive); }
	.mover-icon--red { color: var(--negative); }
	.mover-list { display: flex; flex-direction: column; gap: 12px; }
	.mover-row {
		display: flex;
		justify-content: space-between;
		align-items: center;
		background: none;
		border: none;
		color: inherit;
		cursor: pointer;
		padding: 4px 0;
		font-family: var(--font-mono);
		font-size: 14px;
		width: 100%;
		transition: color 0.15s;
	}
	.mover-row:hover { color: var(--accent-soft); }
	.mover-ticker { color: var(--text); }
	.mover-change { font-weight: 700; }
	.mover-change--green { color: var(--positive); }
	.mover-change--red { color: var(--negative); }

	/* Summary card */
	.summary-card {
		background: var(--bg-hover);
		padding: 24px;
		display: flex;
		align-items: center;
		justify-content: space-between;
		border-top: 2px solid var(--accent);
	}
	.summary-label {
		font-family: var(--font-mono);
		font-size: 11px;
		text-transform: uppercase;
		color: var(--text-faint);
	}
	.summary-value {
		font-family: var(--font-heading);
		font-size: 2.5rem;
		font-weight: 900;
		color: var(--text);
	}
	.summary-unit {
		font-size: 1rem;
		font-weight: 400;
		color: var(--text-faint);
		margin-left: 4px;
	}
	.summary-sub {
		font-family: var(--font-mono);
		font-size: 12px;
		color: var(--text-faint);
		margin-top: 4px;
	}
	.summary-highlight { color: var(--accent-soft); font-weight: 700; }
	.summary-highlight-pct { color: var(--positive); font-weight: 700; margin-left: 4px; }
	.summary-sparkline { width: 192px; height: 64px; }
	.sparkline-svg { width: 100%; height: 100%; }

	/* Intel row */
	.intel-row {
		display: grid;
		grid-template-columns: 2fr 1fr;
		gap: 24px;
	}
	.section-bar {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 24px;
	}
	.section-label {
		font-family: var(--font-heading);
		font-size: 14px;
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: -0.02em;
		color: var(--text);
	}

	/* Period toggle */
	.period-toggle {
		display: flex;
		gap: 2px;
	}
	.period-btn {
		padding: 4px 10px;
		border: none;
		background: transparent;
		color: var(--text-dim);
		font-family: var(--font-mono);
		font-size: 10px;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.15s;
		text-transform: uppercase;
	}
	.period-btn:hover { color: var(--text-muted); background: var(--bg-hover); }
	.period-btn.active { color: var(--accent); background: var(--accent-dim); }

	/* Sector matrix */
	.sector-matrix {
		background: var(--bg-elevated);
		padding: 24px;
		border-top: 1px solid var(--border-subtle);
	}
	.sector-grid {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: 8px;
	}
	.sector-cell {
		padding: 16px;
		height: 128px;
		display: flex;
		flex-direction: column;
		justify-content: space-between;
	}
	.sector-cell--positive {
		background: var(--positive-bg);
		border-left: 2px solid var(--positive);
	}
	.sector-cell--negative {
		background: var(--negative-bg);
		border-left: 2px solid var(--negative);
	}
	.sector-cell--mixed {
		background: var(--neutral-bg);
		border-left: 2px solid var(--gold);
	}
	.sector-name {
		font-family: var(--font-mono);
		font-size: 10px;
		text-transform: uppercase;
		color: var(--text-muted);
	}
	.sector-change {
		font-family: var(--font-heading);
		font-size: 1.25rem;
		font-weight: 700;
	}
	.sector-change--positive { color: var(--positive); }
	.sector-change--negative { color: var(--negative); }
	.sector-breadth {
		font-family: var(--font-mono);
		font-size: 9px;
		color: var(--text-muted);
		margin-top: 2px;
	}
	.sector-sentiment {
		font-family: var(--font-mono);
		font-size: 10px;
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		margin-top: 4px;
	}
	.sentiment--bullish { color: var(--positive); }
	.sentiment--bearish { color: var(--negative); }
	.sentiment--mixed { color: var(--gold); }

	/* Analysis panel */
	.analysis-panel {
		background: var(--bg-elevated);
		padding: 24px;
		border-top: 1px solid var(--accent);
	}
	.analysis-cards { display: flex; flex-direction: column; gap: 16px; margin-top: 24px; }
	.analysis-card {
		padding: 16px;
		background: var(--bg-surface);
		border: 1px solid var(--border-subtle);
	}
	.analysis-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		margin-bottom: 8px;
	}
	.analysis-tag {
		font-family: var(--font-mono);
		font-size: 11px;
		font-weight: 700;
		text-transform: uppercase;
	}
	.analysis-tag--cyan { color: var(--accent-soft); }
	.analysis-tag--gold { color: var(--gold-soft); }
	.analysis-badge {
		background: var(--accent);
		color: var(--accent-on);
		font-family: var(--font-mono);
		font-size: 10px;
		font-weight: 700;
		padding: 2px 6px;
	}
	.analysis-value-row {
		display: flex;
		align-items: flex-end;
		gap: 8px;
	}
	.analysis-big {
		font-family: var(--font-heading);
		font-size: 1.875rem;
		font-weight: 900;
		color: var(--text);
	}
	.analysis-unit {
		font-family: var(--font-mono);
		font-size: 12px;
		color: var(--text-faint);
		padding-bottom: 4px;
	}
	.analysis-desc {
		font-family: var(--font-mono);
		font-size: 10px;
		color: var(--text-faint);
		margin-top: 8px;
		line-height: 1.5;
	}

	/* Screener preview */
	.screener-preview {
		background: var(--bg-elevated);
		border-top: 1px solid var(--border-subtle);
	}
	.screener-preview .section-bar { padding: 16px 24px 0; }
	.preview-table-wrap { overflow-x: auto; }
	.preview-table {
		width: 100%;
		border-collapse: collapse;
		text-align: left;
	}
	.preview-table thead tr {
		background: var(--sidebar-bg);
		border-bottom: 1px solid var(--border-subtle);
	}
	.preview-table th {
		padding: 16px 24px;
		font-family: var(--font-mono);
		font-size: 10px;
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.15em;
		color: var(--text-faint);
	}
	.preview-table tbody tr {
		border-bottom: 1px solid var(--border-subtle);
		cursor: pointer;
		transition: background 0.15s;
	}
	.preview-table tbody tr:hover { background: var(--accent-dim); }
	.preview-table td {
		padding: 16px 24px;
		font-family: var(--font-mono);
		font-size: 12px;
		color: var(--text-secondary);
	}
	.ticker-cell {
		display: flex;
		align-items: center;
		gap: 12px;
	}
	.ticker-badge {
		width: 32px;
		height: 32px;
		background: var(--border);
		display: flex;
		align-items: center;
		justify-content: center;
		font-family: var(--font-mono);
		font-size: 9px;
		font-weight: 900;
		color: var(--text);
	}
	.ticker-name {
		font-family: var(--font-heading);
		font-size: 12px;
		font-weight: 700;
		color: var(--text);
	}
	.ticker-exchange {
		font-family: var(--font-mono);
		font-size: 10px;
		color: var(--text-faint);
	}
	.text-green { color: var(--positive); font-weight: 700; }
	.text-red { color: var(--negative); font-weight: 700; }
	.text-cyan { color: var(--accent-soft); font-weight: 700; }
	.text-right { text-align: right; }

	/* Footer */
	.dash-footer {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 24px;
		background: var(--sidebar-bg);
		border-top: 1px solid var(--border-subtle);
		margin: 0 -32px -32px;
	}
	.footer-left {
		display: flex;
		align-items: center;
		gap: 32px;
	}
	.footer-status {
		display: flex;
		align-items: center;
		gap: 8px;
		font-family: var(--font-mono);
		font-size: 10px;
		text-transform: uppercase;
		letter-spacing: 0.15em;
		color: var(--text-faint);
	}
	.status-dot {
		width: 8px;
		height: 8px;
		border-radius: 50%;
		background: var(--positive);
	}
	.footer-left > span {
		font-family: var(--font-mono);
		font-size: 10px;
		text-transform: uppercase;
		letter-spacing: 0.15em;
		color: var(--text-faint);
	}
	.footer-time { color: var(--accent-soft); }
	.footer-copy {
		font-family: var(--font-mono);
		font-size: 10px;
		color: var(--text-dim);
	}

	.material-symbols-outlined {
		font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
	}

	@media (max-width: 1024px) {
		.movers-row { grid-template-columns: 1fr 1fr; }
		.summary-card { grid-column: span 2; }
		.intel-row { grid-template-columns: 1fr; }
		.sector-grid { grid-template-columns: repeat(2, 1fr); }
	}
	@media (max-width: 768px) {
		.dashboard { padding: 16px; gap: 16px; }
		.dash-header { flex-direction: column; align-items: flex-start; gap: 12px; }
		.movers-row { grid-template-columns: 1fr; }
		.summary-card { grid-column: auto; }
		.sector-grid { grid-template-columns: 1fr 1fr; }
		.dash-footer { flex-direction: column; gap: 12px; margin: 0 -16px -16px; }
	}
</style>
