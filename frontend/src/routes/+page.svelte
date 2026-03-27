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
				<a class="nav-link nav-link--active" href="/">Markets</a>
				<a class="nav-link" href="/">News</a>
				<a class="nav-link" href="/">Watchlist</a>
			</div>
		</div>
		<div class="nav-right">
			<button class="nav-signin">Sign In</button>
			<a href="/dashboard" class="nav-cta">Get Started</a>
		</div>
	</nav>

	<main class="landing-main">
		<!-- Hero Section -->
		<section class="hero">
			<div class="hero-grid">
				<div class="hero-text">
					<div class="hero-badge">
						<span class="badge-dot"></span>
						<span class="badge-label">Live Market Feed Active</span>
					</div>
					<h1 class="hero-title">
						See the Market <br /><span class="hero-title-white">Clearly.</span>
					</h1>
					<p class="hero-subtitle">
						Real-time precision and powerful visual data for the modern investor. Engineered for those who trade on intelligence, not intuition.
					</p>
					<div class="hero-buttons">
						<a href="/dashboard" class="btn-primary-green">Start Analyzing</a>
						<button class="btn-outline">View Live Demo</button>
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
							<span class="chart-label">VOLATILITY INDEX</span>
							<span class="chart-value">18.42 <span class="chart-change">&#9650; 2.1%</span></span>
						</div>
					</div>
				</div>
			</div>
		</section>

		<!-- Market Sentiment -->
		<section class="sentiment-section">
			<div class="section-container">
				<div class="section-header">
					<div>
						<span class="section-tag">Intelligence Hub</span>
						<h2 class="section-title">Market Sentiment</h2>
					</div>
					<div class="section-dots">
						<div class="dot dot--active"></div>
						<div class="dot"></div>
					</div>
				</div>
				<div class="sentiment-grid">
					<div class="sentiment-card sentiment-card--glass">
						<div class="sentiment-top">
							<span class="material-symbols-outlined sentiment-icon sentiment-icon--green">trending_up</span>
							<span class="sentiment-badge">GLOBAL INDEX</span>
						</div>
						<h3 class="sentiment-title">Bullish Momentum</h3>
						<p class="sentiment-desc">Aggregate sentiment across top 500 equities suggests strong buy pressure in tech and energy sectors.</p>
						<div class="sentiment-bar"><div class="sentiment-fill sentiment-fill--green" style="width: 78%"></div></div>
						<span class="sentiment-label sentiment-label--green">78% CONFIDENCE LEVEL</span>
					</div>
					<div class="sentiment-card sentiment-card--solid">
						<div class="sentiment-hover-bg"></div>
						<div class="sentiment-card-inner">
							<div class="sentiment-top">
								<span class="material-symbols-outlined sentiment-icon sentiment-icon--cyan">query_stats</span>
								<span class="sentiment-badge">CRYPTO ASSETS</span>
							</div>
							<h3 class="sentiment-title">Neutral Consolidation</h3>
							<p class="sentiment-desc">Digital assets maintain sideways movement within Fibonacci support zones. Volatility remains low.</p>
							<div class="sentiment-bar sentiment-bar--dark"><div class="sentiment-fill sentiment-fill--cyan" style="width: 45%"></div></div>
							<span class="sentiment-label sentiment-label--cyan">45% ACCUMULATION</span>
						</div>
					</div>
					<div class="sentiment-card sentiment-card--glass">
						<div class="sentiment-top">
							<span class="material-symbols-outlined sentiment-icon sentiment-icon--red">warning</span>
							<span class="sentiment-badge">RISK ASSESSMENT</span>
						</div>
						<h3 class="sentiment-title">Macro Headwinds</h3>
						<p class="sentiment-desc">Yield curve fluctuations indicating potential short-term liquidity tightening in emerging markets.</p>
						<div class="sentiment-bar"><div class="sentiment-fill sentiment-fill--red" style="width: 12%"></div></div>
						<span class="sentiment-label sentiment-label--red">12% BULLISH STRENGTH</span>
					</div>
				</div>
			</div>
		</section>

		<!-- Features Section -->
		<section class="features-section">
			<div class="section-container features-grid">
				<div class="features-left">
					<h2 class="features-heading">Precision <br /><span class="features-heading-accent">Tooling.</span></h2>
					<p class="features-desc">We provide the hardware for your financial strategy. No fluff, just raw execution capabilities.</p>
					<div class="features-checks">
						<div class="feature-check">
							<span class="material-symbols-outlined feature-check-icon">check_circle</span>
							<span class="feature-check-text">Latency-optimized data</span>
						</div>
						<div class="feature-check">
							<span class="material-symbols-outlined feature-check-icon">check_circle</span>
							<span class="feature-check-text">Institutional-grade logic</span>
						</div>
					</div>
				</div>
				<div class="features-right">
					<div class="feature-card feature-card--cyan">
						<div class="feature-icon-wrap feature-icon-wrap--cyan">
							<span class="material-symbols-outlined feature-icon-glyph feature-icon-glyph--cyan">psychology</span>
						</div>
						<div>
							<h4 class="feature-card-title">AI Alerts</h4>
							<p class="feature-card-desc">Neural networks scan thousands of tickers per second to identify pattern breakouts before they hit the retail news cycle.</p>
						</div>
					</div>
					<div class="feature-card feature-card--green">
						<div class="feature-icon-wrap feature-icon-wrap--green">
							<span class="material-symbols-outlined feature-icon-glyph feature-icon-glyph--green">analytics</span>
						</div>
						<div>
							<h4 class="feature-card-title">Deep Analysis</h4>
							<p class="feature-card-desc">Go beyond simple charts. Access order flow, dark pool volume, and sentiment heatmaps in a single unified interface.</p>
						</div>
					</div>
					<div class="feature-card feature-card--gold">
						<div class="feature-icon-wrap feature-icon-wrap--gold">
							<span class="material-symbols-outlined feature-icon-glyph feature-icon-glyph--gold">public</span>
						</div>
						<div>
							<h4 class="feature-card-title">Global Watchlist</h4>
							<p class="feature-card-desc">Sync your tactical assets across all markets—equities, crypto, forex, and commodities—with cross-asset correlation tracking.</p>
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
					<h2 class="cta-title">Ready to master the void?</h2>
					<p class="cta-desc">Join 50,000+ tactical investors using StockLens to filter the noise and capture the alpha.</p>
					<form class="cta-form" onsubmit={(e) => e.preventDefault()}>
						<input type="email" placeholder="terminal@access.io" class="cta-input" />
						<button type="submit" class="cta-btn">Request Access</button>
					</form>
				</div>
			</div>
		</section>
	</main>

	<!-- Footer -->
	<footer class="landing-footer">
		<div class="footer-left">
			<span class="nav-logo">StockLens</span>
			<p class="footer-copy">&copy; 2024 StockLens. Powered by Real-Time Data.</p>
		</div>
		<div class="footer-links">
			<a href="/">Terms</a>
			<a href="/">Privacy</a>
			<a href="/">API Docs</a>
			<a href="/">Support</a>
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
	.nav-signin,
	.btn-primary-green,
	.btn-outline,
	.cta-btn,
	.feature-check-text,
	:global(.landing-root .nav-link) {
		font-family: 'Manrope', system-ui, sans-serif;
	}

	.badge-label,
	.chart-label,
	.chart-value,
	.section-tag,
	.sentiment-badge,
	.sentiment-label,
	.cta-input,
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
	.nav-signin {
		padding: 8px 20px;
		background: none;
		border: none;
		color: var(--cyan-soft);
		font-weight: 700;
		cursor: pointer;
		transition: background 0.2s;
	}
	.nav-signin:hover { background: rgba(164, 230, 255, 0.05); }
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
	.section-dots { display: flex; gap: 8px; }
	.dot { height: 4px; width: 48px; background: var(--surface-highest); }
	.dot--active { background: var(--cyan-soft); }

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
	.sentiment-bar {
		width: 100%;
		height: 4px;
		background: var(--surface);
	}
	.sentiment-bar--dark { background: var(--surface-highest); }
	.sentiment-fill { height: 100%; }
	.sentiment-fill--green { background: var(--green); }
	.sentiment-fill--cyan { background: var(--cyan-soft); }
	.sentiment-fill--red { background: var(--red); }
	.sentiment-label {
		display: block;
		margin-top: 8px;
		font-size: 10px;
	}
	.sentiment-label--green { color: var(--green-soft); }
	.sentiment-label--cyan { color: var(--cyan-soft); }
	.sentiment-label--red { color: var(--red); }

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
	.cta-form {
		display: inline-flex;
		padding: 4px;
		background: var(--surface-highest);
	}
	.cta-input {
		background: transparent;
		border: none;
		outline: none;
		color: #fff;
		padding: 12px 24px;
		width: 256px;
		font-size: 0.875rem;
	}
	.cta-input::placeholder { color: var(--muted); }
	.cta-btn {
		padding: 12px 32px;
		background: var(--cyan-soft);
		color: var(--on-primary);
		font-family: 'Manrope', system-ui, sans-serif;
		font-weight: 700;
		font-size: 0.875rem;
		border: none;
		cursor: pointer;
		transition: transform 0.1s;
	}
	.cta-btn:active { transform: scale(0.95); }

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
