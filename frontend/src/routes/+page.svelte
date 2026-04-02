<script lang="ts">
	import { onMount } from 'svelte';
	import { getScreener } from '$lib/api/client';
	import type { StockRow } from '$lib/api/types';

	interface TickerItem {
		symbol: string;
		price: string;
		change: string;
		up: boolean;
	}

	let tickers = $state<TickerItem[]>([]);

	function formatPrice(price: number): string {
		return price >= 1000 ? price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
			: price.toFixed(2);
	}

	function toTickerItem(s: StockRow): TickerItem {
		return {
			symbol: s.ticker,
			price: formatPrice(s.price ?? 0),
			change: `${(s.change_pct ?? 0) >= 0 ? '+' : ''}${(s.change_pct ?? 0).toFixed(2)}%`,
			up: (s.change_pct ?? 0) >= 0,
		};
	}

	onMount(async () => {
		document.body.classList.add('landing-body');

		try {
			const res = await getScreener({ sort_by: 'market_cap', sort_dir: 'desc', limit: 500 });
			const stocks = res.stocks.filter(s => s.price != null && s.change_pct != null);

			const gainers = [...stocks].sort((a, b) => (b.change_pct ?? 0) - (a.change_pct ?? 0)).slice(0, 8);
			const losers = [...stocks].sort((a, b) => (a.change_pct ?? 0) - (b.change_pct ?? 0)).slice(0, 8);

			// Interleave gainers and losers for visual variety
			const mixed: StockRow[] = [];
			for (let i = 0; i < Math.max(gainers.length, losers.length); i++) {
				if (i < gainers.length) mixed.push(gainers[i]);
				if (i < losers.length) mixed.push(losers[i]);
			}

			tickers = mixed.map(toTickerItem);
		} catch {
			// Fallback if API unavailable
			tickers = [
				{ symbol: 'AAPL', price: '182.41', change: '+1.2%', up: true },
				{ symbol: 'TSLA', price: '175.22', change: '-0.8%', up: false },
			];
		}

		return () => document.body.classList.remove('landing-body');
	});
</script>

<svelte:head>
	<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;700;800&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet" />
	<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet" />
</svelte:head>

<div class="landing-root">
	<!-- Nav -->
	<nav class="landing-nav">
		<div class="nav-left">
			<span class="nav-logo">StockLens</span>
			<div class="nav-links">
				<a class="nav-link" href="/screener">Screener</a>
				<a class="nav-link" href="/rankings">Rankings</a>
				<a class="nav-link" href="/watchlist">Watchlist</a>
			</div>
		</div>
		<div class="nav-right">
			<a href="/dashboard" class="nav-cta">Open Dashboard</a>
		</div>
	</nav>

	<main class="landing-main">
		<!-- Hero Section -->
		<section class="hero">
			<div class="hero-grid">
				<div class="hero-text">
					<div class="hero-badge">
						<span class="badge-dot"></span>
						<span class="badge-label">Tracking {tickers.length}+ Nordic Stocks</span>
					</div>
					<h1 class="hero-title">
						Nordic Stock <br /><span class="hero-title-white">Intelligence.</span>
					</h1>
					<p class="hero-subtitle">
						Screen, score, and track stocks across Sweden, Denmark, Finland, and Norway. Fundamentals, price history, and proven scoring models — all in one place.
					</p>
					<div class="hero-buttons">
						<a href="/dashboard" class="btn-primary-green">Open Dashboard</a>
						<a href="/screener" class="btn-outline">Browse Screener</a>
					</div>
				</div>
				<div class="hero-visual">
					<div class="hero-glow"></div>
					<div class="chart-card">
						<svg viewBox="0 0 400 180" class="chart-svg">
							{#each Array(40) as _, i}
								{@const x = i * 10 + 5}
								{@const base = 90 + Math.sin(i * 0.3) * 30 + Math.cos(i * 0.7) * 20}
								{@const high = base - 10 - Math.random() * 20}
								{@const low = base + 10 + Math.random() * 20}
								{@const open = base - 5 + Math.random() * 10}
								{@const close = base - 5 + Math.random() * 10}
								{@const bullish = close < open}
								<line x1={x} y1={high} x2={x} y2={low} stroke={bullish ? '#01f5a0' : '#f85149'} stroke-width="1" />
								<rect
									x={x - 3}
									y={Math.min(open, close)}
									width="6"
									height={Math.max(Math.abs(close - open), 2)}
									fill={bullish ? '#01f5a0' : '#f85149'}
								/>
							{/each}
						</svg>
						<div class="chart-overlay">
							<span class="chart-label">NORDIC MARKETS</span>
							<span class="chart-value">SE · DK · FI · NO</span>
						</div>
					</div>
				</div>
			</div>
		</section>

		<!-- What's Included -->
		<section class="sentiment-section">
			<div class="section-container">
				<div class="section-header">
					<div>
						<span class="section-tag">What You Get</span>
						<h2 class="section-title">Built for Nordic Markets</h2>
					</div>
				</div>
				<div class="sentiment-grid">
					<div class="sentiment-card sentiment-card--glass">
						<div class="sentiment-top">
							<span class="material-symbols-outlined sentiment-icon sentiment-icon--green">filter_list</span>
							<span class="sentiment-badge">SCREENER</span>
						</div>
						<h3 class="sentiment-title">Stock Screener</h3>
						<p class="sentiment-desc">Filter and sort Nordic stocks by country, sector, valuation, and performance. Track 1-day, 1-week, 1-month, and 1-year returns side by side.</p>
					</div>
					<div class="sentiment-card sentiment-card--solid">
						<div class="sentiment-hover-bg"></div>
						<div class="sentiment-card-inner">
							<div class="sentiment-top">
								<span class="material-symbols-outlined sentiment-icon sentiment-icon--cyan">leaderboard</span>
								<span class="sentiment-badge">SCORING</span>
							</div>
							<h3 class="sentiment-title">Investment Scores</h3>
							<p class="sentiment-desc">Rank stocks using Piotroski F-Score, Magic Formula, and Graham Number. Quantitative scoring models used by value investors worldwide.</p>
						</div>
					</div>
					<div class="sentiment-card sentiment-card--glass">
						<div class="sentiment-top">
							<span class="material-symbols-outlined sentiment-icon sentiment-icon--red">candlestick_chart</span>
							<span class="sentiment-badge">CHARTS & DATA</span>
						</div>
						<h3 class="sentiment-title">Fundamentals & Charts</h3>
						<p class="sentiment-desc">Up to 10 years of price history with candlestick charts, moving averages, and annual financials including revenue, EPS, margins, and balance sheet data.</p>
					</div>
				</div>
			</div>
		</section>

		<!-- Features Section -->
		<section class="features-section">
			<div class="section-container features-grid">
				<div class="features-left">
					<h2 class="features-heading">How It <br /><span class="features-heading-accent">Works.</span></h2>
					<p class="features-desc">Data is fetched from public financial APIs, stored in PostgreSQL, and refreshed throughout the trading day.</p>
					<div class="features-checks">
						<div class="feature-check">
							<span class="material-symbols-outlined feature-check-icon">check_circle</span>
							<span class="feature-check-text">Updated every 3 hours during market hours</span>
						</div>
						<div class="feature-check">
							<span class="material-symbols-outlined feature-check-icon">check_circle</span>
							<span class="feature-check-text">Covers SE, DK, FI, and NO exchanges</span>
						</div>
					</div>
				</div>
				<div class="features-right">
					<div class="feature-card feature-card--cyan">
						<div class="feature-icon-wrap feature-icon-wrap--cyan">
							<span class="material-symbols-outlined feature-icon-glyph feature-icon-glyph--cyan">dashboard</span>
						</div>
						<div>
							<h4 class="feature-card-title">Dashboard</h4>
							<p class="feature-card-desc">See today's top gainers and losers, sector sentiment by period, and your portfolio-level scoring highlights at a glance.</p>
						</div>
					</div>
					<div class="feature-card feature-card--green">
						<div class="feature-icon-wrap feature-icon-wrap--green">
							<span class="material-symbols-outlined feature-icon-glyph feature-icon-glyph--green">analytics</span>
						</div>
						<div>
							<h4 class="feature-card-title">Deep Dive</h4>
							<p class="feature-card-desc">Click any stock to see detailed financials, key ratios, historical charts, and investment scores — all in a side panel without leaving the screener.</p>
						</div>
					</div>
					<div class="feature-card feature-card--gold">
						<div class="feature-icon-wrap feature-icon-wrap--gold">
							<span class="material-symbols-outlined feature-icon-glyph feature-icon-glyph--gold">visibility</span>
						</div>
						<div>
							<h4 class="feature-card-title">Watchlist</h4>
							<p class="feature-card-desc">Star stocks you're interested in and track them in a dedicated view. Your watchlist is saved locally so it's always there when you come back.</p>
						</div>
					</div>
				</div>
			</div>
		</section>

		<!-- CTA -->
		<section class="cta-section">
			<div class="cta-container">
				<div class="cta-glow"></div>
				<div class="cta-content">
					<h2 class="cta-title">Start exploring Nordic markets.</h2>
					<p class="cta-desc">No sign-up required. Open the dashboard and start screening stocks right away.</p>
					<div class="hero-buttons" style="justify-content: center;">
						<a href="/dashboard" class="btn-primary-green">Open Dashboard</a>
						<a href="/screener" class="btn-outline">Go to Screener</a>
					</div>
				</div>
			</div>
		</section>
	</main>

	<!-- Footer -->
	<footer class="landing-footer">
		<div class="footer-left">
			<span class="nav-logo">StockLens</span>
			<p class="footer-copy">&copy; 2025 StockLens. Nordic stock data updated throughout the trading day.</p>
		</div>
		<div class="footer-links">
			<a href="/dashboard">Dashboard</a>
			<a href="/screener">Screener</a>
			<a href="/rankings">Rankings</a>
			<a href="/watchlist">Watchlist</a>
		</div>
	</footer>

	<!-- Bottom Ticker -->
	<div class="ticker-bar">
		<div class="ticker-scroll">
			{#each [0, 1] as _set}
				<div class="ticker-set">
					{#each tickers as t}
						<div class="ticker-item">
							<span class="material-symbols-outlined ticker-arrow" class:ticker-arrow--up={t.up} class:ticker-arrow--down={!t.up}>
								{t.up ? 'trending_up' : 'trending_down'}
							</span>
							<span class="ticker-symbol" class:ticker-symbol--up={t.up}>{t.symbol}</span>
							<span class="ticker-price">{t.price}</span>
							<span class="ticker-change" class:ticker-change--up={t.up} class:ticker-change--down={!t.up}>{t.change}</span>
						</div>
					{/each}
				</div>
			{/each}
		</div>
	</div>
</div>

<style>
	/* ===== Global overrides for landing page ===== */
	:global(body.landing-body) {
		overflow: auto !important;
		font-size: 15px !important;
		line-height: 1.6 !important;
		background: #111417 !important;
		color: #e1e2e7 !important;
	}

	/* ===== Tokens ===== */
	.landing-root {
		--void: #111417;
		--void-deep: #0b0e11;
		--surface: #1d2023;
		--surface-high: #272a2e;
		--surface-highest: #323538;
		--cyan: #00d1ff;
		--cyan-soft: #a4e6ff;
		--green: #01f5a0;
		--green-soft: #ceffdf;
		--gold: #feb127;
		--gold-soft: #ffd59c;
		--red: #ffb4ab;
		--muted: #859399;
		--outline-v: #3c494e;
		--on-primary: #003543;
		--on-green: #002111;

		font-family: 'Inter', system-ui, sans-serif;
		background: var(--void);
		color: #e1e2e7;
		overflow-x: hidden;
	}

	/* ===== Typography helpers ===== */
	.nav-logo,
	.hero-title,
	.section-title,
	.features-heading,
	.sentiment-title,
	.feature-card-title,
	.cta-title,
	.nav-cta,
	.btn-primary-green,
	.btn-outline,
	.feature-check-text,
	:global(.landing-root .nav-link) {
		font-family: 'Manrope', system-ui, sans-serif;
	}

	.badge-label,
	.chart-label,
	.chart-value,
	.section-tag,
	.sentiment-badge,
	.ticker-symbol,
	.ticker-price {
		font-family: 'JetBrains Mono', monospace;
	}

	.material-symbols-outlined {
		font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
	}

	/* ===== Nav ===== */
	.landing-nav {
		position: fixed;
		top: 0;
		width: 100%;
		z-index: 50;
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 16px 24px;
		background: rgba(17, 20, 23, 0.8);
		backdrop-filter: blur(24px);
		border-bottom: 1px solid rgba(164, 230, 255, 0.1);
		box-shadow: 0 0 20px rgba(0, 209, 255, 0.04);
	}
	.nav-left { display: flex; align-items: center; gap: 32px; }
	.nav-right { display: flex; align-items: center; gap: 16px; }
	.nav-logo {
		font-size: 1.5rem;
		font-weight: 900;
		letter-spacing: -0.05em;
		color: var(--cyan-soft);
	}
	.nav-links { display: flex; gap: 24px; }
	.nav-link {
		font-weight: 700;
		letter-spacing: -0.02em;
		color: #94a3b8;
		text-decoration: none;
		transition: color 0.2s;
	}
	.nav-link:hover { color: #f1f5f9; }
	.nav-link--active {
		color: var(--cyan-soft);
		border-bottom: 2px solid var(--cyan-soft);
		padding-bottom: 4px;
	}
	.nav-cta {
		display: inline-block;
		padding: 8px 20px;
		background: linear-gradient(135deg, var(--cyan-soft), var(--cyan));
		color: var(--on-primary);
		font-weight: 700;
		text-decoration: none;
		transition: opacity 0.2s;
	}
	.nav-cta:hover { opacity: 0.9; }

	/* ===== Main ===== */
	.landing-main { padding-top: 80px; }

	/* ===== Hero ===== */
	.hero {
		position: relative;
		min-height: calc(100vh - 80px);
		display: flex;
		flex-direction: column;
		justify-content: center;
		padding: 0 48px;
		overflow: hidden;
		border-bottom: 1px solid rgba(255,255,255,0.05);
	}
	.hero-grid {
		max-width: 1280px;
		margin: 0 auto;
		width: 100%;
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 48px;
		align-items: center;
	}
	.hero-badge {
		display: inline-flex;
		align-items: center;
		gap: 8px;
		padding: 4px 12px;
		background: var(--surface-highest);
		margin-bottom: 24px;
	}
	.badge-dot {
		width: 8px;
		height: 8px;
		border-radius: 50%;
		background: var(--green);
		animation: pulse 2s infinite;
	}
	@keyframes pulse {
		0%, 100% { opacity: 1; }
		50% { opacity: 0.4; }
	}
	.badge-label {
		font-size: 10px;
		text-transform: uppercase;
		letter-spacing: 0.15em;
		color: var(--green-soft);
	}
	.hero-title {
		font-size: clamp(3.5rem, 6vw, 6rem);
		font-weight: 800;
		line-height: 0.9;
		letter-spacing: -0.04em;
		color: var(--cyan);
		margin-bottom: 24px;
	}
	.hero-title-white { color: #fff; }
	.hero-subtitle {
		font-size: 1.25rem;
		color: var(--muted);
		max-width: 480px;
		line-height: 1.6;
		margin-bottom: 40px;
	}
	.hero-buttons { display: flex; flex-wrap: wrap; gap: 16px; }
	.btn-primary-green {
		display: inline-block;
		padding: 16px 32px;
		background: linear-gradient(135deg, var(--green), #50ffaf);
		color: var(--on-green);
		font-weight: 700;
		font-size: 1.125rem;
		text-decoration: none;
		box-shadow: 0 0 25px rgba(1, 245, 160, 0.2);
		transition: transform 0.1s, opacity 0.2s;
	}
	.btn-primary-green:active { transform: scale(0.95); }
	.btn-outline {
		padding: 16px 32px;
		border: 1px solid var(--outline-v);
		background: none;
		color: var(--cyan-soft);
		font-weight: 700;
		font-size: 1.125rem;
		cursor: pointer;
		transition: background 0.2s, transform 0.1s;
	}
	.btn-outline:hover { background: rgba(164, 230, 255, 0.05); }
	.btn-outline:active { transform: scale(0.95); }

	/* Hero visual */
	.hero-visual {
		position: relative;
		display: flex;
		align-items: center;
		justify-content: center;
		min-height: 400px;
	}
	.hero-glow {
		position: absolute;
		inset: 0;
		background: rgba(0, 209, 255, 0.1);
		filter: blur(120px);
		border-radius: 50%;
	}
	.chart-card {
		position: relative;
		width: 100%;
		background: var(--surface-high);
		border: 1px solid rgba(255,255,255,0.1);
		padding: 16px;
		box-shadow: 0 25px 50px rgba(0,0,0,0.4);
	}
	.chart-svg { width: 100%; height: auto; display: block; }
	.chart-overlay {
		position: absolute;
		top: 16px;
		left: 16px;
		background: rgba(50, 53, 56, 0.4);
		backdrop-filter: blur(20px);
		padding: 16px;
		border-left: 2px solid var(--cyan);
	}
	.chart-label {
		display: block;
		font-size: 10px;
		color: var(--cyan);
		margin-bottom: 4px;
	}
	.chart-value {
		display: block;
		font-family: 'Manrope', system-ui, sans-serif;
		font-size: 1.5rem;
		font-weight: 700;
		color: #fff;
	}
	.chart-change {
		font-size: 0.875rem;
		color: var(--green-soft);
	}

	/* ===== Market Sentiment ===== */
	.sentiment-section {
		padding: 96px 48px;
		background: var(--void-deep);
	}
	.section-container { max-width: 1280px; margin: 0 auto; }
	.section-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-end;
		margin-bottom: 48px;
		gap: 24px;
	}
	.section-tag {
		display: block;
		font-size: 12px;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		color: var(--cyan);
		margin-bottom: 8px;
	}
	.section-title {
		font-size: 2.5rem;
		font-weight: 700;
		letter-spacing: -0.02em;
		color: #fff;
	}
	.sentiment-grid {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 0;
	}
	.sentiment-card {
		padding: 32px;
		transition: background 0.3s;
	}
	.sentiment-card--glass {
		background: rgba(50, 53, 56, 0.4);
		backdrop-filter: blur(20px);
		border-top: 1px solid rgba(255,255,255,0.1);
	}
	.sentiment-card--glass:first-child { border-right: 1px solid rgba(255,255,255,0.1); }
	.sentiment-card--glass:hover { background: var(--surface-high); }
	.sentiment-card--solid {
		position: relative;
		overflow: hidden;
		background: var(--surface);
		border-top: 1px solid rgba(255,255,255,0.05);
		border-right: 1px solid rgba(255,255,255,0.05);
	}
	.sentiment-hover-bg {
		position: absolute;
		inset: 0;
		background: rgba(0, 209, 255, 0.05);
		transform: translateY(100%);
		transition: transform 0.5s;
	}
	.sentiment-card--solid:hover .sentiment-hover-bg { transform: translateY(0); }
	.sentiment-card-inner { position: relative; z-index: 1; }
	.sentiment-top {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		margin-bottom: 48px;
	}
	.sentiment-icon { font-size: 2.25rem; }
	.sentiment-icon--green { color: var(--green); }
	.sentiment-icon--cyan { color: var(--cyan-soft); }
	.sentiment-icon--red { color: var(--red); }
	.sentiment-badge {
		font-size: 10px;
		color: var(--muted);
	}
	.sentiment-title {
		font-size: 1.5rem;
		font-weight: 700;
		margin-bottom: 8px;
		color: #fff;
	}
	.sentiment-desc {
		font-size: 0.875rem;
		color: var(--muted);
		line-height: 1.6;
		margin-bottom: 24px;
	}

	/* ===== Features ===== */
	.features-section { padding: 96px 48px; background: var(--void); }
	.features-grid {
		display: grid;
		grid-template-columns: 1fr 2fr;
		gap: 48px;
		align-items: start;
	}
	.features-left { position: sticky; top: 128px; }
	.features-heading {
		font-size: 3.25rem;
		font-weight: 900;
		letter-spacing: -0.04em;
		line-height: 1;
		margin-bottom: 32px;
		color: #fff;
	}
	.features-heading-accent { color: var(--cyan); }
	.features-desc {
		font-size: 1.125rem;
		color: var(--muted);
		line-height: 1.6;
		margin-bottom: 32px;
	}
	.features-checks { display: flex; flex-direction: column; gap: 16px; }
	.feature-check { display: flex; align-items: center; gap: 16px; color: var(--green-soft); }
	.feature-check-icon { font-variation-settings: 'FILL' 1; }
	.feature-check-text { font-weight: 700; }

	.features-right { display: flex; flex-direction: column; gap: 48px; }
	.feature-card {
		display: flex;
		flex-direction: row;
		gap: 32px;
		padding: 48px;
		background: var(--surface-high);
	}
	.feature-card--cyan { border-left: 4px solid var(--cyan); }
	.feature-card--green { border-left: 4px solid var(--green); }
	.feature-card--gold { border-left: 4px solid var(--gold); }
	.feature-icon-wrap {
		width: 64px;
		height: 64px;
		display: flex;
		align-items: center;
		justify-content: center;
		flex-shrink: 0;
	}
	.feature-icon-wrap--cyan { background: rgba(164, 230, 255, 0.1); }
	.feature-icon-wrap--green { background: rgba(206, 255, 223, 0.1); }
	.feature-icon-wrap--gold { background: rgba(255, 213, 156, 0.1); }
	.feature-icon-glyph { font-size: 2.25rem; }
	.feature-icon-glyph--cyan { color: var(--cyan-soft); }
	.feature-icon-glyph--green { color: var(--green-soft); }
	.feature-icon-glyph--gold { color: var(--gold-soft); }
	.feature-card-title {
		font-size: 1.875rem;
		font-weight: 700;
		margin-bottom: 16px;
		color: #fff;
	}
	.feature-card-desc {
		color: var(--muted);
		line-height: 1.6;
	}

	/* ===== CTA ===== */
	.cta-section { padding: 128px 24px; background: var(--void); }
	.cta-container {
		max-width: 896px;
		margin: 0 auto;
		text-align: center;
		position: relative;
	}
	.cta-glow {
		position: absolute;
		inset: 0;
		background: rgba(0, 209, 255, 0.05);
		filter: blur(48px);
		border-radius: 50%;
	}
	.cta-content { position: relative; z-index: 1; }
	.cta-title {
		font-size: clamp(2.5rem, 4vw, 3.75rem);
		font-weight: 700;
		margin-bottom: 32px;
		color: #fff;
	}
	.cta-desc {
		font-size: 1.25rem;
		color: var(--muted);
		margin-bottom: 48px;
		max-width: 640px;
		margin-left: auto;
		margin-right: auto;
	}

	/* ===== Footer ===== */
	.landing-footer {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 48px 32px;
		border-top: 1px solid rgba(255,255,255,0.05);
		background: var(--void-deep);
	}
	.footer-left { display: flex; flex-direction: column; gap: 8px; }
	.footer-copy { font-size: 0.875rem; color: #64748b; }
	.footer-links { display: flex; gap: 32px; }
	.footer-links a {
		font-size: 0.875rem;
		color: #64748b;
		text-decoration: none;
		transition: color 0.2s;
	}
	.footer-links a:hover { color: var(--green); }

	/* ===== Ticker Bar ===== */
	.ticker-bar {
		position: fixed;
		bottom: 0;
		width: 100%;
		z-index: 40;
		height: 40px;
		display: flex;
		align-items: center;
		padding: 0 16px;
		background: var(--void-deep);
		border-top: 1px solid rgba(1, 245, 160, 0.15);
		overflow: hidden;
	}
	.ticker-scroll {
		display: flex;
		width: fit-content;
		animation: ticker-slide 60s linear infinite;
	}
	@keyframes ticker-slide {
		from { transform: translateX(0); }
		to { transform: translateX(-50%); }
	}
	.ticker-set { display: flex; align-items: center; gap: 48px; padding: 0 24px; }
	.ticker-item { display: flex; align-items: center; gap: 8px; white-space: nowrap; }
	.ticker-arrow { font-size: 14px; }
	.ticker-arrow--up { color: var(--green); }
	.ticker-arrow--down { color: var(--red); }
	.ticker-symbol {
		font-size: 10px;
		text-transform: uppercase;
		letter-spacing: 0.15em;
		color: #64748b;
	}
	.ticker-symbol--up { color: var(--green); font-weight: 700; }
	.ticker-price { font-size: 10px; color: #fff; }
	.ticker-change { font-size: 10px; }
	.ticker-change--up { color: var(--green); }
	.ticker-change--down { color: var(--red); }

	/* ===== Responsive ===== */
	@media (max-width: 768px) {
		.hero { padding: 0 24px; }
		.hero-grid { grid-template-columns: 1fr; }
		.hero-visual { min-height: auto; }
		.sentiment-section { padding: 64px 24px; }
		.sentiment-grid { grid-template-columns: 1fr; }
		.sentiment-card--glass:first-child { border-right: none; }
		.sentiment-card--solid { border-right: none; }
		.features-section { padding: 64px 24px; }
		.features-grid { grid-template-columns: 1fr; }
		.features-left { position: static; }
		.feature-card { padding: 24px; flex-direction: column; gap: 16px; }
		.nav-links { display: none; }
		.landing-footer { flex-direction: column; gap: 24px; text-align: center; }
		.cta-form { flex-direction: column; }
		.cta-input { width: 100%; }
	}
</style>
