<script lang="ts">
	const tickers = [
		{ symbol: 'AAPL', price: '$182.48' },
		{ symbol: 'TSLA', price: '$179.22' },
		{ symbol: 'BTC', price: '$64,182.00' },
		{ symbol: 'AAPL', price: '$182.41' },
		{ symbol: 'TSLA', price: '$179.22' },
		{ symbol: 'BTC', price: '$64,182.00' },
	];
</script>

<div class="landing">
	<!-- Nav -->
	<nav class="nav">
		<div class="nav-inner">
			<div class="nav-left">
				<a href="/" class="logo">StockLens</a>
				<a href="/" class="nav-link active">Markets</a>
				<a href="/" class="nav-link">News</a>
				<a href="/" class="nav-link">Watchlist</a>
			</div>
			<div class="nav-right">
				<a href="/" class="nav-link">Sign In</a>
				<a href="/" class="btn-primary btn-sm">Get Started</a>
			</div>
		</div>
	</nav>

	<!-- Hero -->
	<section class="hero">
		<div class="hero-inner">
			<div class="hero-text">
				<span class="badge">
					<span class="badge-dot"></span>
					LIVE MARKET FEED ACTIVE
				</span>
				<h1>
					<span class="hero-italic">See the</span><br />
					<span class="hero-italic">Market</span><br />
					<span class="hero-clear">Clearly.</span>
				</h1>
				<p class="hero-sub">
					Real-time precision and powerful visual data for the modern investor.
					Engineered for those who trade on intelligence, not intuition.
				</p>
				<div class="hero-buttons">
					<a href="/" class="btn-primary">Start Analyzing</a>
					<a href="/" class="btn-outline">View Live Demo</a>
				</div>
			</div>
			<div class="hero-visual">
				<div class="chart-card">
					<div class="chart-header">
						<span class="chart-label">VOLATILITY INDEX</span>
						<span class="chart-value">18.42 <span class="text-positive">&#9650; 21%</span></span>
					</div>
					<div class="chart-placeholder">
						<svg viewBox="0 0 400 180" class="chart-svg">
							<!-- Candlestick-style chart -->
							{#each Array(40) as _, i}
								{@const x = i * 10 + 5}
								{@const base = 90 + Math.sin(i * 0.3) * 30 + Math.cos(i * 0.7) * 20}
								{@const high = base - 10 - Math.random() * 20}
								{@const low = base + 10 + Math.random() * 20}
								{@const open = base - 5 + Math.random() * 10}
								{@const close = base - 5 + Math.random() * 10}
								{@const bullish = close < open}
								<line x1={x} y1={high} x2={x} y2={low} stroke={bullish ? '#3fb950' : '#f85149'} stroke-width="1" />
								<rect
									x={x - 3}
									y={Math.min(open, close)}
									width="6"
									height={Math.max(Math.abs(close - open), 2)}
									fill={bullish ? '#3fb950' : '#f85149'}
								/>
							{/each}
						</svg>
					</div>
				</div>
			</div>
		</div>
	</section>

	<!-- Ticker tape -->
	<div class="ticker-tape">
		<div class="ticker-track">
			{#each [...tickers, ...tickers] as t}
				<span class="ticker-item">
					<span class="ticker-dot"></span>
					<span class="ticker-symbol">{t.symbol}</span>
					<span class="ticker-price">{t.price}</span>
				</span>
			{/each}
		</div>
	</div>

	<!-- Market Sentiment -->
	<section class="section">
		<div class="section-inner">
			<span class="section-tag">INTELLIGENCE HUB</span>
			<h2 class="section-title">Market Sentiment</h2>
			<div class="sentiment-grid">
				<div class="sentiment-card">
					<div class="sentiment-card-header">
						<span class="sentiment-icon">&#x2197;</span>
						<span class="sentiment-badge">GLOBAL INDEX</span>
					</div>
					<h3>Bullish Momentum</h3>
					<p>Aggregate sentiment across top 500 equities suggests strong buy pressure in tech and energy sectors.</p>
					<div class="sentiment-bar">
						<div class="sentiment-fill" style="width: 76%; background: var(--accent);"></div>
					</div>
					<span class="sentiment-label">76% CONFIDENCE LEVEL</span>
				</div>
				<div class="sentiment-card">
					<div class="sentiment-card-header">
						<span class="sentiment-icon">&#x2194;</span>
						<span class="sentiment-badge">CRYPTO ASSETS</span>
					</div>
					<h3>Neutral Consolidation</h3>
					<p>Digital assets maintain sideways movement within Fibonacci support zones. Volatility remains low.</p>
					<div class="sentiment-bar">
						<div class="sentiment-fill" style="width: 45%; background: var(--accent);"></div>
					</div>
					<span class="sentiment-label">45% ACCUMULATION</span>
				</div>
				<div class="sentiment-card">
					<div class="sentiment-card-header">
						<span class="sentiment-icon">&#x26A0;</span>
						<span class="sentiment-badge">RISK ASSESSMENT</span>
					</div>
					<h3>Macro Headwinds</h3>
					<p>Yield curve fluctuations indicating potential short-term liquidity tightening in emerging markets.</p>
					<div class="sentiment-bar">
						<div class="sentiment-fill" style="width: 12%; background: var(--negative);"></div>
					</div>
					<span class="sentiment-label">12% BULLISH STRENGTH</span>
				</div>
			</div>
		</div>
	</section>

	<!-- Precision Tooling -->
	<section class="section tooling-section">
		<div class="section-inner tooling-grid">
			<div class="tooling-left">
				<h2>
					<span class="hero-italic">Precision</span><br />
					<span class="hero-italic accent">Tooling.</span>
				</h2>
				<p>We provide the hardware for your financial strategy. No fluff, just raw execution capabilities.</p>
				<ul class="tooling-list">
					<li><span class="check">&#10003;</span> Latency-optimized data</li>
					<li><span class="check">&#10003;</span> Institutional-grade logic</li>
				</ul>
			</div>
			<div class="tooling-right">
				<div class="feature-card">
					<div class="feature-icon">&#x2699;</div>
					<div>
						<h3>AI Alerts</h3>
						<p>Neural networks scan thousands of tickers per second to identify pattern breakouts before they hit the retail news cycle.</p>
					</div>
				</div>
				<div class="feature-card">
					<div class="feature-icon">&#x2261;</div>
					<div>
						<h3>Deep Analysis</h3>
						<p>Go beyond simple charts. Access order flow, dark pool volume, and sentiment heatmaps in a single unified interface.</p>
					</div>
				</div>
				<div class="feature-card">
					<div class="feature-icon">&#x25CE;</div>
					<div>
						<h3>Global Watchlist</h3>
						<p>Sync your tactical assets across all markets — equities, crypto, forex, and commodities — with cross-asset correlation tracking.</p>
					</div>
				</div>
			</div>
		</div>
	</section>

	<!-- CTA -->
	<section class="cta-section">
		<div class="section-inner cta-inner">
			<h2>Ready to master the void?</h2>
			<p>Join 50,000+ tactical investors using StockLens to filter the noise and capture the alpha.</p>
			<form class="cta-form" onsubmit={(e) => e.preventDefault()}>
				<input type="email" placeholder="terminal@access.io" class="cta-input" />
				<button type="submit" class="btn-primary">Request Access</button>
			</form>
		</div>
	</section>

	<!-- Footer -->
	<footer class="footer">
		<div class="footer-inner">
			<div class="footer-left">
				<span class="logo">StockLens</span>
				<span class="footer-copy">&copy; 2024 StockLens. Powered by Real-Time Data.</span>
			</div>
			<div class="footer-right">
				<a href="/">Terms</a>
				<a href="/">Privacy</a>
				<a href="/">API Docs</a>
				<a href="/">Support</a>
			</div>
		</div>
	</footer>
</div>

<style>
	.landing {
		overflow-y: auto;
		overflow-x: hidden;
		height: 100vh;
		background: var(--bg);
		color: var(--text);
		font-family: var(--font-ui);
		font-size: 15px;
		line-height: 1.6;
	}

	/* Nav */
	.nav {
		position: sticky;
		top: 0;
		z-index: 100;
		background: var(--bg);
		border-bottom: 1px solid var(--border);
	}
	.nav-inner {
		max-width: 1200px;
		margin: 0 auto;
		padding: 0 24px;
		height: 56px;
		display: flex;
		align-items: center;
		justify-content: space-between;
	}
	.nav-left, .nav-right {
		display: flex;
		align-items: center;
		gap: 24px;
	}
	.logo {
		font-weight: 700;
		font-size: 18px;
		color: var(--text);
		text-decoration: none;
		margin-right: 8px;
	}
	.nav-link {
		color: var(--text-muted);
		text-decoration: none;
		font-size: 14px;
		font-weight: 500;
		transition: color 0.15s;
	}
	.nav-link:hover, .nav-link.active {
		color: var(--text);
	}
	.nav-link.active {
		text-decoration: underline;
		text-underline-offset: 4px;
	}

	/* Buttons */
	.btn-primary {
		background: var(--accent);
		color: #000;
		padding: 10px 22px;
		border-radius: var(--radius);
		font-weight: 600;
		font-size: 14px;
		text-decoration: none;
		border: none;
		cursor: pointer;
		transition: opacity 0.15s;
		display: inline-block;
	}
	.btn-primary:hover { opacity: 0.85; }
	.btn-sm { padding: 6px 16px; font-size: 13px; }
	.btn-outline {
		border: 1px solid var(--border);
		color: var(--text);
		padding: 10px 22px;
		border-radius: var(--radius);
		font-weight: 600;
		font-size: 14px;
		text-decoration: none;
		background: transparent;
		cursor: pointer;
		transition: border-color 0.15s;
		display: inline-block;
	}
	.btn-outline:hover { border-color: var(--text-muted); }

	/* Hero */
	.hero {
		padding: 80px 24px 40px;
	}
	.hero-inner {
		max-width: 1200px;
		margin: 0 auto;
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 48px;
		align-items: center;
	}
	.badge {
		display: inline-flex;
		align-items: center;
		gap: 8px;
		background: var(--bg-surface);
		border: 1px solid var(--border);
		border-radius: 20px;
		padding: 6px 14px;
		font-size: 11px;
		font-weight: 600;
		letter-spacing: 0.05em;
		color: var(--text-muted);
		margin-bottom: 24px;
	}
	.badge-dot {
		width: 8px;
		height: 8px;
		border-radius: 50%;
		background: var(--positive);
		animation: pulse 2s infinite;
	}
	@keyframes pulse {
		0%, 100% { opacity: 1; }
		50% { opacity: 0.4; }
	}
	h1 {
		font-size: 64px;
		line-height: 1.05;
		margin-bottom: 20px;
		font-weight: 700;
	}
	.hero-italic {
		font-style: italic;
		color: var(--accent);
	}
	.hero-clear {
		font-style: normal;
		color: var(--text);
	}
	.hero-sub {
		color: var(--text-muted);
		font-size: 16px;
		max-width: 400px;
		margin-bottom: 28px;
		line-height: 1.6;
	}
	.hero-buttons {
		display: flex;
		gap: 12px;
	}

	/* Chart card */
	.chart-card {
		background: var(--bg-surface);
		border: 1px solid var(--border);
		border-radius: 12px;
		overflow: hidden;
	}
	.chart-header {
		padding: 12px 16px;
		display: flex;
		justify-content: space-between;
		align-items: center;
	}
	.chart-label {
		font-size: 10px;
		font-weight: 600;
		letter-spacing: 0.08em;
		color: var(--text-muted);
	}
	.chart-value {
		font-family: var(--font-mono);
		font-size: 14px;
		font-weight: 600;
	}
	.chart-placeholder {
		padding: 0 8px 8px;
	}
	.chart-svg {
		width: 100%;
		height: auto;
	}

	/* Ticker tape */
	.ticker-tape {
		border-top: 1px solid var(--border);
		border-bottom: 1px solid var(--border);
		padding: 12px 0;
		overflow: hidden;
		background: var(--bg-surface);
	}
	.ticker-track {
		display: flex;
		gap: 40px;
		animation: scroll 20s linear infinite;
		width: max-content;
	}
	@keyframes scroll {
		0% { transform: translateX(0); }
		100% { transform: translateX(-50%); }
	}
	.ticker-item {
		display: flex;
		align-items: center;
		gap: 8px;
		white-space: nowrap;
	}
	.ticker-dot {
		width: 6px;
		height: 6px;
		border-radius: 50%;
		background: var(--accent);
	}
	.ticker-symbol {
		font-weight: 600;
		font-size: 12px;
		color: var(--text-muted);
	}
	.ticker-price {
		font-family: var(--font-mono);
		font-size: 12px;
		color: var(--text);
	}

	/* Sections */
	.section {
		padding: 80px 24px;
	}
	.section-inner {
		max-width: 1200px;
		margin: 0 auto;
	}
	.section-tag {
		font-size: 12px;
		font-weight: 600;
		letter-spacing: 0.1em;
		color: var(--accent);
		display: block;
		margin-bottom: 8px;
	}
	.section-title {
		font-size: 32px;
		font-weight: 700;
		margin-bottom: 36px;
	}

	/* Sentiment */
	.sentiment-grid {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 20px;
	}
	.sentiment-card {
		background: var(--bg-surface);
		border: 1px solid var(--border);
		border-radius: 12px;
		padding: 24px;
	}
	.sentiment-card-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 16px;
	}
	.sentiment-icon {
		font-size: 24px;
	}
	.sentiment-badge {
		font-size: 10px;
		font-weight: 600;
		letter-spacing: 0.08em;
		color: var(--text-dim);
	}
	.sentiment-card h3 {
		font-size: 18px;
		font-weight: 700;
		margin-bottom: 8px;
	}
	.sentiment-card p {
		font-size: 13px;
		color: var(--text-muted);
		margin-bottom: 20px;
		line-height: 1.5;
	}
	.sentiment-bar {
		height: 4px;
		background: var(--bg-hover);
		border-radius: 2px;
		margin-bottom: 8px;
	}
	.sentiment-fill {
		height: 100%;
		border-radius: 2px;
	}
	.sentiment-label {
		font-size: 10px;
		font-weight: 600;
		letter-spacing: 0.08em;
		color: var(--text-dim);
	}

	/* Tooling */
	.tooling-grid {
		display: grid;
		grid-template-columns: 1fr 1.2fr;
		gap: 60px;
		align-items: start;
	}
	.tooling-left h2 {
		font-size: 48px;
		line-height: 1.1;
		margin-bottom: 16px;
	}
	.tooling-left p {
		color: var(--text-muted);
		font-size: 15px;
		margin-bottom: 20px;
	}
	.accent { color: var(--accent); }
	.tooling-list {
		list-style: none;
		display: flex;
		flex-direction: column;
		gap: 8px;
	}
	.tooling-list li {
		display: flex;
		align-items: center;
		gap: 10px;
		font-size: 14px;
		font-weight: 500;
	}
	.check {
		color: var(--accent);
		font-weight: 700;
	}

	.feature-card {
		display: flex;
		gap: 16px;
		background: var(--bg-surface);
		border: 1px solid var(--border);
		border-radius: 12px;
		padding: 24px;
		margin-bottom: 16px;
	}
	.feature-icon {
		width: 40px;
		height: 40px;
		border-radius: 10px;
		background: var(--bg-hover);
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 18px;
		flex-shrink: 0;
		color: var(--accent);
	}
	.feature-card h3 {
		font-size: 16px;
		font-weight: 700;
		margin-bottom: 6px;
	}
	.feature-card p {
		font-size: 13px;
		color: var(--text-muted);
		line-height: 1.5;
	}

	/* CTA */
	.cta-section {
		padding: 100px 24px;
		text-align: center;
	}
	.cta-inner h2 {
		font-size: 42px;
		font-weight: 700;
		margin-bottom: 12px;
	}
	.cta-inner p {
		color: var(--text-muted);
		font-size: 16px;
		margin-bottom: 32px;
	}
	.cta-form {
		display: flex;
		gap: 8px;
		justify-content: center;
	}
	.cta-input {
		background: var(--bg-surface);
		border: 1px solid var(--border);
		border-radius: var(--radius);
		padding: 10px 18px;
		color: var(--text);
		font-size: 14px;
		font-family: var(--font-ui);
		width: 280px;
		outline: none;
	}
	.cta-input::placeholder { color: var(--text-dim); }
	.cta-input:focus { border-color: var(--accent); }

	/* Footer */
	.footer {
		border-top: 1px solid var(--border);
		padding: 24px;
		background: var(--bg-surface);
	}
	.footer-inner {
		max-width: 1200px;
		margin: 0 auto;
		display: flex;
		justify-content: space-between;
		align-items: center;
	}
	.footer-left {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}
	.footer-copy {
		font-size: 12px;
		color: var(--text-dim);
	}
	.footer-right {
		display: flex;
		gap: 24px;
	}
	.footer-right a {
		color: var(--text-muted);
		text-decoration: none;
		font-size: 13px;
	}
	.footer-right a:hover { color: var(--text); }

	/* Responsive */
	@media (max-width: 768px) {
		.hero-inner {
			grid-template-columns: 1fr;
		}
		h1 { font-size: 42px; }
		.sentiment-grid {
			grid-template-columns: 1fr;
		}
		.tooling-grid {
			grid-template-columns: 1fr;
		}
		.tooling-left h2 { font-size: 36px; }
		.cta-inner h2 { font-size: 28px; }
		.cta-form {
			flex-direction: column;
			align-items: center;
		}
		.footer-inner {
			flex-direction: column;
			gap: 16px;
			text-align: center;
		}
	}
</style>
