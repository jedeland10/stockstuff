<script lang="ts">
  import { companyData } from '$lib/stores/screener';
  import BarChart from '$lib/components/shared/BarChart.svelte';
  import { fmtLarge, fmtPct, fmtNum } from '$lib/utils/format';

  const signColor = (v: number | null) => {
    const s = getComputedStyle(document.documentElement);
    return v != null ? (v >= 0 ? s.getPropertyValue('--positive-bg').trim() : s.getPropertyValue('--negative-bg').trim()) : s.getPropertyValue('--neutral-bg').trim();
  };
  const fmtPctBar = (v: number) => (v != null ? v.toFixed(1) + '%' : '\u2014');

  let cd = $derived($companyData);

  let bsSorted = $derived(
    (cd?.balance_sheet ?? []).toSorted((a, b) => a.year - b.year)
  );
  let bsLabels = $derived(bsSorted.map((b) => String(b.year)));
  let totalAssets = $derived(bsSorted.map((b) => b.total_assets));
  let totalEquity = $derived(bsSorted.map((b) => b.total_equity));
  let equityRatio = $derived(
    bsSorted.map((b) =>
      b.total_equity != null && b.total_assets != null && b.total_assets !== 0
        ? (b.total_equity / b.total_assets) * 100
        : null
    )
  );
  let netDebt = $derived(bsSorted.map((b) => b.net_debt));
  let cash = $derived(bsSorted.map((b) => b.cash));
  let intangibles = $derived(bsSorted.map((b) => b.intangible_assets));

  let cfSorted = $derived(
    (cd?.cashflow ?? []).toSorted((a, b) => a.year - b.year)
  );
  let cfLabels = $derived(cfSorted.map((c) => String(c.year)));
  let opCf = $derived(cfSorted.map((c) => c.operating_cf));
  let capex = $derived(cfSorted.map((c) => c.capex));
  let freeCf = $derived(cfSorted.map((c) => c.free_cf));

  let finSorted = $derived(
    (cd?.financials ?? []).toSorted((a, b) => a.year - b.year)
  );
  let earningsFcfRatio = $derived(
    cfSorted.map((c) => {
      const fin = finSorted.find((f) => f.year === c.year);
      if (fin?.net_income != null && c.free_cf != null && c.free_cf !== 0) {
        return (fin.net_income / c.free_cf) * 100;
      }
      return null;
    })
  );

  function metricStr(v: number | null | undefined, fn: (v: number | null | undefined) => string): string {
    return fn(v);
  }
</script>

<div class="keynumbers-tab">
  {#if cd}
    <section class="metrics-row">
      <div class="km">
        <span class="km-label">Net Sales</span>
        <span class="km-value">{fmtLarge(cd.revenue)}</span>
      </div>
      <div class="km">
        <span class="km-label">P/E</span>
        <span class="km-value">{fmtNum(cd.pe)}</span>
      </div>
      <div class="km">
        <span class="km-label">P/B</span>
        <span class="km-value">{fmtNum(cd.pb)}</span>
      </div>
      <div class="km">
        <span class="km-label">EV/EBITDA</span>
        <span class="km-value">{fmtNum(cd.ev_ebitda)}</span>
      </div>
      <div class="km">
        <span class="km-label">Div Yield</span>
        <span class="km-value">{fmtPct(cd.div_yield)}</span>
      </div>
      <div class="km">
        <span class="km-label">ROE</span>
        <span class="km-value">{fmtPct(cd.roe)}</span>
      </div>
      <div class="km">
        <span class="km-label">Margin</span>
        <span class="km-value">{fmtPct(cd.margin)}</span>
      </div>
      <div class="km">
        <span class="km-label">MCap</span>
        <span class="km-value">{fmtLarge(cd.market_cap)}</span>
      </div>
    </section>

    <section>
      <h3 class="section-title">Balance Sheet</h3>
      <div class="grid-3x2">
        <BarChart id="kn-assets" title="Total Assets" labels={bsLabels} data={totalAssets} formatFn={fmtLarge} />
        <BarChart id="kn-equity" title="Total Equity" labels={bsLabels} data={totalEquity} formatFn={fmtLarge} />
        <BarChart id="kn-eqratio" title="Equity Ratio" labels={bsLabels} data={equityRatio} formatFn={fmtPctBar} colorFn={signColor} />
        <BarChart id="kn-netdebt" title="Net Debt" labels={bsLabels} data={netDebt} formatFn={fmtLarge} />
        <BarChart id="kn-cash" title="Cash" labels={bsLabels} data={cash} formatFn={fmtLarge} />
        <BarChart id="kn-intangibles" title="Intangible Assets" labels={bsLabels} data={intangibles} formatFn={fmtLarge} />
      </div>
    </section>

    <section>
      <h3 class="section-title">Cash Flow</h3>
      <div class="grid-2x2">
        <BarChart id="kn-opcf" title="Operating CF" labels={cfLabels} data={opCf} formatFn={fmtLarge} />
        <BarChart id="kn-capex" title="Capex" labels={cfLabels} data={capex} formatFn={fmtLarge} />
        <BarChart id="kn-freecf" title="Free Cash Flow" labels={cfLabels} data={freeCf} formatFn={fmtLarge} />
        <BarChart id="kn-earnfcf" title="Earnings/FCF" labels={cfLabels} data={earningsFcfRatio} formatFn={fmtPctBar} colorFn={signColor} />
      </div>
    </section>
  {/if}
</div>

<style>
  .keynumbers-tab {
    overflow-y: auto;
  }

  section {
    padding: 10px;
    border-bottom: 1px solid var(--border);
  }

  .metrics-row {
    display: flex;
    gap: 2px;
    background: var(--bg-surface);
    border-bottom: 1px solid var(--border);
    overflow-x: auto;
  }

  .km {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 4px 10px;
    flex-shrink: 0;
  }

  .km-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 8px;
    color: var(--text-dim);
    text-transform: uppercase;
  }

  .km-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    font-weight: 600;
    color: var(--accent, #00bcd4);
  }

  .section-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    text-transform: uppercase;
    color: var(--text-dim);
    margin: 0 0 6px 0;
  }

  .grid-3x2 {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    grid-auto-rows: 150px;
    gap: 6px;
  }

  .grid-2x2 {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    grid-auto-rows: 150px;
    gap: 6px;
  }
</style>
