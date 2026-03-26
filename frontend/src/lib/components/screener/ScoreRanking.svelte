<script lang="ts">
  import { getMagicFormulaRanking, getFScoreRanking, type MagicFormulaEntry, type FScoreEntry } from '$lib/api/client';

  let { onSelect }: { onSelect: (ticker: string) => void } = $props();

  let activeRanking = $state<'magic' | 'fscore'>('magic');
  let magicData = $state<MagicFormulaEntry[]>([]);
  let fscoreData = $state<FScoreEntry[]>([]);
  let loading = $state(false);
  let fscoreSortBy = $state<'f_score' | 'profitability' | 'leverage' | 'efficiency'>('f_score');

  const FLAG: Record<string, string> = { SE: '\u{1F1F8}\u{1F1EA}', DK: '\u{1F1E9}\u{1F1F0}', FI: '\u{1F1EB}\u{1F1EE}', NO: '\u{1F1F3}\u{1F1F4}' };

  async function loadMagic() {
    if (magicData.length) return;
    loading = true;
    magicData = await getMagicFormulaRanking(200);
    loading = false;
  }

  async function loadFScore() {
    if (fscoreData.length) return;
    loading = true;
    fscoreData = await getFScoreRanking(200);
    loading = false;
  }

  async function switchTab(tab: 'magic' | 'fscore') {
    activeRanking = tab;
    if (tab === 'magic') await loadMagic();
    else await loadFScore();
  }

  let sortedFscoreData = $derived(
    [...fscoreData].sort((a, b) => b[fscoreSortBy] - a[fscoreSortBy])
  );

  // Load initial data
  $effect(() => { loadMagic(); });

  function fmtPct(v: number | null): string {
    if (v == null) return '\u2014';
    return (v * 100).toFixed(1) + '%';
  }

  function fmtNum(v: number | null): string {
    if (v == null) return '\u2014';
    return v.toFixed(1);
  }

  function scoreColor(score: number): string {
    if (score >= 7) return 'var(--positive)';
    if (score <= 3) return 'var(--negative)';
    return 'var(--gold)';
  }

  function scoreBg(score: number): string {
    if (score >= 7) return 'rgba(63, 185, 80, 0.1)';
    if (score <= 3) return 'rgba(248, 81, 73, 0.1)';
    return 'rgba(210, 153, 34, 0.1)';
  }

  function scoreLabel(score: number): string {
    if (score >= 7) return 'Strong';
    if (score <= 3) return 'Weak';
    return 'Neutral';
  }

  function subScoreColor(score: number, max: number): string {
    const ratio = score / max;
    if (ratio >= 0.75) return 'var(--positive)';
    if (ratio <= 0.33) return 'var(--negative)';
    return 'var(--gold)';
  }

  const fscoreSortOptions = [
    { key: 'f_score' as const, label: 'Overall', max: 9 },
    { key: 'profitability' as const, label: 'Profitability', max: 4 },
    { key: 'leverage' as const, label: 'Leverage', max: 3 },
    { key: 'efficiency' as const, label: 'Efficiency', max: 2 },
  ];
</script>

<div class="ranking-container">
  <div class="ranking-header">
    <div class="ranking-tabs">
      <button class="rtab" class:active={activeRanking === 'magic'} onclick={() => switchTab('magic')}>
        <span class="rtab-icon">&#9733;</span>
        Magic Formula
      </button>
      <button class="rtab" class:active={activeRanking === 'fscore'} onclick={() => switchTab('fscore')}>
        <span class="rtab-icon">&#9650;</span>
        Piotroski F-Score
      </button>
    </div>
    <div class="ranking-info">
      {#if activeRanking === 'magic'}
        <p class="ranking-desc">Developed by Joel Greenblatt, the <strong>Magic Formula</strong> finds undervalued companies with high returns. It ranks all stocks on two metrics, then combines the ranks — lower combined rank = better.</p>
        <div class="metric-explainers">
          <div class="metric-card">
            <span class="metric-name">Earnings Yield</span>
            <span class="metric-detail">Operating Income / Enterprise Value — how cheap the stock is relative to its earnings. Higher = better value.</span>
          </div>
          <div class="metric-card">
            <span class="metric-name">Return on Capital</span>
            <span class="metric-detail">Operating Income / (Net Fixed Assets + Working Capital) — how efficiently the company uses its capital. Higher = better business.</span>
          </div>
        </div>
      {:else}
        <p class="ranking-desc">Developed by Joseph Piotroski, the <strong>F-Score</strong> evaluates financial strength using 9 binary tests across three areas. Each passed test = 1 point. Score of 7-9 is strong, 0-3 is weak.</p>
        <div class="metric-explainers three-col">
          <div class="metric-card">
            <span class="metric-name">Profitability (4 pts)</span>
            <span class="metric-detail">Positive net income, positive operating cash flow, improving ROA, and cash flow exceeding net income.</span>
          </div>
          <div class="metric-card">
            <span class="metric-name">Leverage (3 pts)</span>
            <span class="metric-detail">Decreasing long-term debt, improving current ratio, and no share dilution.</span>
          </div>
          <div class="metric-card">
            <span class="metric-name">Efficiency (2 pts)</span>
            <span class="metric-detail">Improving gross margin and improving asset turnover ratio.</span>
          </div>
        </div>
      {/if}
    </div>
  </div>

  {#if loading}
    <div class="loading">Loading rankings...</div>
  {:else if activeRanking === 'magic'}
    <div class="ranking-table-wrap">
      <table>
        <thead>
          <tr>
            <th class="rank-col">#</th>
            <th class="name-col">Company</th>
            <th>Ticker</th>
            <th>Sector</th>
            <th class="num-col">Earnings Yield</th>
            <th class="num-col">Return on Capital</th>
            <th class="num-col">P/E</th>
            <th class="num-col">Price</th>
          </tr>
        </thead>
        <tbody>
          {#each magicData as stock, i (stock.ticker)}
            <tr onclick={() => onSelect(stock.ticker)}>
              <td class="rank-cell">
                {#if i < 3}
                  <span class="medal" class:gold={i === 0} class:silver={i === 1} class:bronze={i === 2}>{i + 1}</span>
                {:else}
                  {i + 1}
                {/if}
              </td>
              <td class="name-cell">
                <span class="flag">{FLAG[stock.country] ?? ''}</span>
                <span class="name-text">{stock.name}</span>
              </td>
              <td class="ticker-cell">{stock.ticker}</td>
              <td class="sector-cell">{stock.sector ?? '\u2014'}</td>
              <td class="num-col highlight-col">{fmtPct(stock.earnings_yield)}</td>
              <td class="num-col highlight-col">{fmtPct(stock.return_on_capital)}</td>
              <td class="num-col">{fmtNum(stock.pe)}</td>
              <td class="num-col">{stock.price != null ? stock.price.toFixed(2) : '\u2014'}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>

  {:else}
    <div class="fscore-sort-bar">
      <span class="sort-label">Sort by:</span>
      {#each fscoreSortOptions as opt}
        <button class="sort-btn" class:active={fscoreSortBy === opt.key} onclick={() => fscoreSortBy = opt.key}>
          {opt.label}
        </button>
      {/each}
    </div>
    <div class="ranking-table-wrap">
      <table>
        <thead>
          <tr>
            <th class="rank-col">#</th>
            <th class="name-col">Company</th>
            <th>Ticker</th>
            <th>Sector</th>
            <th class="num-col">Total</th>
            <th class="num-col">Profit</th>
            <th class="num-col">Lever</th>
            <th class="num-col">Effic</th>
            <th class="num-col">Rating</th>
            <th class="num-col">P/E</th>
            <th class="num-col">Price</th>
          </tr>
        </thead>
        <tbody>
          {#each sortedFscoreData as stock, i (stock.ticker)}
            <tr onclick={() => onSelect(stock.ticker)}>
              <td class="rank-cell">
                {#if i < 3}
                  <span class="medal" class:gold={i === 0} class:silver={i === 1} class:bronze={i === 2}>{i + 1}</span>
                {:else}
                  {i + 1}
                {/if}
              </td>
              <td class="name-cell">
                <span class="flag">{FLAG[stock.country] ?? ''}</span>
                <span class="name-text">{stock.name}</span>
              </td>
              <td class="ticker-cell">{stock.ticker}</td>
              <td class="sector-cell">{stock.sector ?? '\u2014'}</td>
              <td class="num-col">
                <div class="score-bar-wrap">
                  <div class="score-bar" style="width:{(stock.f_score / 9) * 100}%;background:{scoreColor(stock.f_score)}"></div>
                  <span class="score-num">{stock.f_score}/9</span>
                </div>
              </td>
              <td class="num-col">
                <span class="sub-score" style="color:{subScoreColor(stock.profitability, 4)}">{stock.profitability}/4</span>
              </td>
              <td class="num-col">
                <span class="sub-score" style="color:{subScoreColor(stock.leverage, 3)}">{stock.leverage}/3</span>
              </td>
              <td class="num-col">
                <span class="sub-score" style="color:{subScoreColor(stock.efficiency, 2)}">{stock.efficiency}/2</span>
              </td>
              <td class="num-col">
                <span class="rating-badge" style="color:{scoreColor(stock.f_score)};background:{scoreBg(stock.f_score)}">
                  {scoreLabel(stock.f_score)}
                </span>
              </td>
              <td class="num-col">{fmtNum(stock.pe)}</td>
              <td class="num-col">{stock.price != null ? stock.price.toFixed(2) : '\u2014'}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}
</div>

<style>
  .ranking-container {
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow: hidden;
  }

  .ranking-header {
    padding: 14px 16px 10px;
    background: var(--bg-surface);
    border-bottom: 1px solid var(--border);
    flex-shrink: 0;
  }
  .ranking-tabs {
    display: flex;
    gap: 4px;
    margin-bottom: 8px;
  }
  .rtab {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 16px;
    border: 1px solid var(--border);
    border-radius: 8px;
    background: var(--bg);
    color: var(--text-muted);
    font-family: var(--font-mono);
    font-size: 12px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.15s;
  }
  .rtab:hover { color: var(--text); border-color: var(--text-dim); }
  .rtab.active {
    color: var(--accent);
    border-color: var(--accent);
    background: var(--accent-dim);
  }
  .rtab-icon { font-size: 14px; }

  .ranking-info {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .ranking-desc {
    font-size: 12px;
    color: var(--text-muted);
    line-height: 1.5;
    margin: 0;
  }
  .ranking-desc strong {
    color: var(--text);
  }
  .metric-explainers {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 6px;
  }
  .metric-explainers.three-col {
    grid-template-columns: repeat(3, 1fr);
  }
  .metric-card {
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 8px 10px;
    display: flex;
    flex-direction: column;
    gap: 2px;
  }
  .metric-name {
    font-family: var(--font-mono);
    font-size: 10px;
    font-weight: 600;
    color: var(--accent);
    text-transform: uppercase;
    letter-spacing: 0.3px;
  }
  .metric-detail {
    font-size: 11px;
    color: var(--text-dim);
    line-height: 1.4;
  }

  .ranking-table-wrap {
    flex: 1;
    overflow: auto;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    font-family: var(--font-mono);
    font-size: 12px;
  }
  thead { position: sticky; top: 0; z-index: 5; }
  th {
    background: var(--bg-surface);
    color: var(--text-muted);
    font-weight: 600;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.3px;
    padding: 8px 10px;
    border-bottom: 2px solid var(--border);
    text-align: left;
    white-space: nowrap;
  }
  td {
    padding: 7px 10px;
    border-bottom: 1px solid rgba(48, 54, 61, 0.3);
    white-space: nowrap;
  }
  tbody tr {
    cursor: pointer;
    transition: background 0.1s;
  }
  tbody tr:hover { background: var(--bg-hover); }

  .rank-col { width: 44px; text-align: center; }
  .rank-cell { text-align: center; color: var(--text-dim); font-weight: 600; }
  .name-col { min-width: 180px; }
  .num-col { text-align: right; }
  th.num-col { text-align: right; }

  .name-cell { display: flex; align-items: center; gap: 6px; }
  .flag { font-size: 11px; }
  .name-text { overflow: hidden; text-overflow: ellipsis; max-width: 200px; }
  .ticker-cell { color: var(--accent); font-weight: 600; }
  .sector-cell { color: var(--text-muted); max-width: 140px; overflow: hidden; text-overflow: ellipsis; }
  .highlight-col { color: var(--accent); font-weight: 500; }

  .medal {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    font-size: 11px;
    font-weight: 700;
  }
  .medal.gold { background: rgba(210, 153, 34, 0.15); color: var(--gold); }
  .medal.silver { background: rgba(139, 148, 158, 0.15); color: var(--text-muted); }
  .medal.bronze { background: rgba(180, 120, 60, 0.15); color: #b4783c; }

  .score-bar-wrap {
    display: flex;
    align-items: center;
    gap: 8px;
    justify-content: flex-end;
  }
  .score-bar {
    height: 6px;
    border-radius: 3px;
    min-width: 4px;
    max-width: 80px;
  }
  .score-num { font-weight: 600; min-width: 28px; text-align: right; }

  .rating-badge {
    display: inline-block;
    font-size: 10px;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 4px;
  }

  .fscore-sort-bar {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 8px 16px;
    background: var(--bg-surface);
    border-bottom: 1px solid var(--border);
    flex-shrink: 0;
  }
  .sort-label {
    font-family: var(--font-mono);
    font-size: 10px;
    color: var(--text-dim);
    text-transform: uppercase;
    margin-right: 4px;
  }
  .sort-btn {
    padding: 4px 10px;
    border: 1px solid var(--border);
    border-radius: 6px;
    background: var(--bg);
    color: var(--text-muted);
    font-family: var(--font-mono);
    font-size: 10px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.12s;
  }
  .sort-btn:hover { border-color: var(--text-dim); color: var(--text); }
  .sort-btn.active {
    border-color: var(--accent);
    color: var(--accent);
    background: var(--accent-dim);
  }

  .sub-score {
    font-family: var(--font-mono);
    font-weight: 600;
    font-size: 12px;
  }

  .loading {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-dim);
    font-family: var(--font-mono);
    font-size: 12px;
  }

  @media (max-width: 768px) {
    .ranking-header { padding: 10px 12px 8px; }
    .ranking-tabs { flex-wrap: wrap; }
    .rtab { padding: 6px 12px; font-size: 11px; }
    .metric-explainers, .metric-explainers.three-col { grid-template-columns: 1fr; }
    .ranking-desc { font-size: 11px; }
    td { padding: 6px 6px; font-size: 11px; }
    th { padding: 6px 6px; }
    .name-text { max-width: 120px; }
    .sector-cell { display: none; }
    th:nth-child(4) { display: none; }
    .fscore-sort-bar { padding: 6px 12px; flex-wrap: wrap; }
  }
</style>
