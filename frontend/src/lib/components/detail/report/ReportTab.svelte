<script lang="ts">
  import { companyData } from '$lib/stores/screener';
  import BarChart from '$lib/components/shared/BarChart.svelte';
  import { fmtLarge } from '$lib/utils/format';
  import type { AnnualFinancial, QuarterlyFinancial } from '$lib/api/types';

  const signColor = (v: number | null) => {
    const s = getComputedStyle(document.documentElement);
    return v != null ? (v >= 0 ? s.getPropertyValue('--positive-bg').trim() : s.getPropertyValue('--negative-bg').trim()) : s.getPropertyValue('--neutral-bg').trim();
  };
  const fmtPctBar = (v: number) => (v != null ? v.toFixed(1) + '%' : '\u2014');
  const fmtEps = (v: number) => (v != null ? v.toFixed(2) : '\u2014');

  function yoyGrowth(arr: (number | null)[]): (number | null)[] {
    return arr.map((curr, i) => {
      if (i === 0) return null;
      const prev = arr[i - 1];
      if (curr == null || prev == null || prev === 0) return null;
      return ((curr - prev) / Math.abs(prev)) * 100;
    });
  }

  let annualSorted = $derived(
    ($companyData?.financials ?? []).toSorted((a, b) => a.year - b.year)
  );
  let annualLabels = $derived(annualSorted.map((f) => String(f.year)));
  let revData = $derived(annualSorted.map((f) => f.revenue));
  let opIncData = $derived(annualSorted.map((f) => f.operating_income));
  let ebitdaData = $derived(annualSorted.map((f) => f.ebitda));
  let netIncData = $derived(annualSorted.map((f) => f.net_income));
  let epsData = $derived(annualSorted.map((f) => f.eps));
  let marginData = $derived(annualSorted.map((f) => f.profit_margin));

  let revGrowth = $derived(yoyGrowth(revData));
  let opIncGrowth = $derived(yoyGrowth(opIncData));
  let earningsGrowth = $derived(yoyGrowth(netIncData));
  let marginTrend = $derived(marginData);

  let quarterlySorted = $derived(
    ($companyData?.quarterly_financials ?? []).toSorted((a, b) =>
      a.period.localeCompare(b.period)
    )
  );
  let qLabels = $derived(quarterlySorted.map((q) => q.period));
  let qRevData = $derived(quarterlySorted.map((q) => q.revenue));
  let qOpIncData = $derived(quarterlySorted.map((q) => q.operating_income));
  let qNetIncData = $derived(quarterlySorted.map((q) => q.net_income));
  let qMarginData = $derived(quarterlySorted.map((q) => q.profit_margin));
</script>

<div class="report-tab">
  {#if $companyData}
    <section>
      <h3 class="section-title">Annual Financials</h3>
      <div class="grid-3x2">
        <BarChart id="rpt-rev" title="Net Sales" labels={annualLabels} data={revData} formatFn={fmtLarge} />
        <BarChart id="rpt-opinc" title="Operating Income" labels={annualLabels} data={opIncData} formatFn={fmtLarge} />
        <BarChart id="rpt-ebitda" title="EBITDA" labels={annualLabels} data={ebitdaData} formatFn={fmtLarge} />
        <BarChart id="rpt-netinc" title="Net Income" labels={annualLabels} data={netIncData} formatFn={fmtLarge} />
        <BarChart id="rpt-eps" title="EPS" labels={annualLabels} data={epsData} formatFn={fmtEps} />
        <BarChart id="rpt-margin" title="Profit Margin" labels={annualLabels} data={marginData} formatFn={fmtPctBar} colorFn={signColor} />
      </div>
    </section>

    <section>
      <h3 class="section-title">Growth Rates</h3>
      <div class="grid-2x2">
        <BarChart id="rpt-revgr" title="Revenue Growth" labels={annualLabels} data={revGrowth} formatFn={fmtPctBar} colorFn={signColor} />
        <BarChart id="rpt-opincgr" title="Op Income Growth" labels={annualLabels} data={opIncGrowth} formatFn={fmtPctBar} colorFn={signColor} />
        <BarChart id="rpt-earngr" title="Earnings Growth" labels={annualLabels} data={earningsGrowth} formatFn={fmtPctBar} colorFn={signColor} />
        <BarChart id="rpt-margtrend" title="Margin Trend" labels={annualLabels} data={marginTrend} formatFn={fmtPctBar} colorFn={signColor} />
      </div>
    </section>

    {#if quarterlySorted.length > 0}
      <section>
        <h3 class="section-title">Quarterly</h3>
        <div class="grid-2x2">
          <BarChart id="rpt-qrev" title="Revenue (Q)" labels={qLabels} data={qRevData} formatFn={fmtLarge} />
          <BarChart id="rpt-qopinc" title="Op Income (Q)" labels={qLabels} data={qOpIncData} formatFn={fmtLarge} />
          <BarChart id="rpt-qnetinc" title="Net Income (Q)" labels={qLabels} data={qNetIncData} formatFn={fmtLarge} />
          <BarChart id="rpt-qmargin" title="Margin (Q)" labels={qLabels} data={qMarginData} formatFn={fmtPctBar} colorFn={signColor} />
        </div>
      </section>
    {/if}
  {/if}
</div>

<style>
  .report-tab {
    overflow-y: auto;
  }

  section {
    padding: 10px;
    border-bottom: 1px solid var(--border);
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

  @media (max-width: 768px) {
    .grid-3x2 { grid-template-columns: repeat(2, 1fr); }
    .grid-2x2 { grid-template-columns: 1fr; }
  }
</style>
