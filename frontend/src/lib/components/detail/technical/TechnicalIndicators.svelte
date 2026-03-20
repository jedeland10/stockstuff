<script lang="ts">
  import { chartData } from '$lib/stores/screener';
  import { computeMA, computeRSI } from '$lib/utils/technicals';
  import { fmt, fmtSignPct } from '$lib/utils/format';

  let stats = $derived.by(() => {
    const d = $chartData;
    if (!d.length) return [];

    const closes = d.map(p => p.close ?? 0);
    const volumes = d.map(p => p.volume ?? 0);
    const last = closes[closes.length - 1];
    const ma50 = computeMA(closes, 50);
    const ma200 = computeMA(closes, 200);
    const rsi = computeRSI(closes, 14);
    const lastMA50 = ma50.filter(v => v !== null).slice(-1)[0];
    const lastMA200 = ma200.filter(v => v !== null).slice(-1)[0];
    const lastRSI = rsi.filter(v => v !== null).slice(-1)[0];

    const vsMa50 = lastMA50 ? ((last - lastMA50) / lastMA50 * 100) : null;
    const vsMa200 = lastMA200 ? ((last - lastMA200) / lastMA200 * 100) : null;

    // Volatility
    const ret20 = closes.slice(-21).map((c, i, a) => i > 0 ? (c - a[i-1]) / a[i-1] : null).filter((v): v is number => v !== null);
    const vol = ret20.length > 1 ? Math.sqrt(ret20.reduce((s, r) => s + r * r, 0) / ret20.length) * Math.sqrt(252) * 100 : null;

    const avgVol = volumes.slice(-20).reduce((s, v) => s + v, 0) / Math.min(20, volumes.length);

    return [
      { label: 'Price', value: fmt(last), color: '' },
      { label: 'MA 50', value: fmt(lastMA50), color: '' },
      { label: 'MA 200', value: fmt(lastMA200), color: '' },
      { label: 'Price/MA50', value: fmtSignPct(vsMa50), color: vsMa50 != null ? (vsMa50 >= 0 ? 'var(--positive)' : 'var(--negative)') : '' },
      { label: 'Price/MA200', value: fmtSignPct(vsMa200), color: vsMa200 != null ? (vsMa200 >= 0 ? 'var(--positive)' : 'var(--negative)') : '' },
      { label: 'RSI(14)', value: lastRSI != null ? lastRSI.toFixed(1) : '—', color: lastRSI != null ? (lastRSI > 70 ? 'var(--negative)' : lastRSI < 30 ? 'var(--positive)' : '') : '' },
      { label: 'Volatility', value: vol != null ? vol.toFixed(1) + '%' : '—', color: '' },
      { label: 'Avg Vol 20d', value: avgVol > 1e6 ? (avgVol/1e6).toFixed(1) + 'M' : Math.round(avgVol).toLocaleString(), color: '' },
      { label: 'MA50/MA200', value: lastMA50 && lastMA200 ? (lastMA50 > lastMA200 ? 'Golden' : 'Death') : '—', color: lastMA50 && lastMA200 ? (lastMA50 > lastMA200 ? 'var(--positive)' : 'var(--negative)') : '' },
    ];
  });
</script>

<div class="indicators">
  {#each stats as s}
    <div class="stat">
      <span class="stat-label">{s.label}</span>
      <span class="stat-value" style:color={s.color || 'var(--text)'}>{s.value}</span>
    </div>
  {/each}
</div>

<style>
  .indicators { padding: 10px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; border-top: 1px solid var(--border); }
  .stat { background: var(--bg-surface); border: 1px solid var(--border); border-radius: 5px; padding: 6px 8px; }
  .stat-label { font-family: var(--font-mono); font-size: 8px; color: var(--text-dim); text-transform: uppercase; display: block; }
  .stat-value { font-family: var(--font-mono); font-size: 13px; font-weight: 600; display: block; }
</style>
