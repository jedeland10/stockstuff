<script lang="ts">
  import { chartData } from '$lib/stores/screener';
  import { computePerformance } from '$lib/utils/technicals';
  import { fmtSignPct } from '$lib/utils/format';

  let perf = $derived.by(() => {
    const d = $chartData;
    if (!d.length) return {};
    return computePerformance(d.map(p => p.close ?? 0), d.map(p => p.date));
  });
</script>

<div class="perf-row">
  {#each Object.entries(perf) as [label, val]}
    <div class="perf-item">
      <span class="perf-label">{label}</span>
      <span class="perf-value" class:text-positive={val != null && val >= 0} class:text-negative={val != null && val < 0}>
        {fmtSignPct(val)}
      </span>
    </div>
  {/each}
</div>

<style>
  .perf-row { display: flex; gap: 2px; padding: 6px 10px; background: var(--bg-surface); border-bottom: 1px solid var(--border); overflow-x: auto; flex-shrink: 0; }
  .perf-item { display: flex; flex-direction: column; align-items: center; padding: 3px 8px; min-width: 55px; }
  .perf-label { font-family: var(--font-mono); font-size: 8px; color: var(--text-dim); text-transform: uppercase; }
  .perf-value { font-family: var(--font-mono); font-size: 11px; font-weight: 600; }
</style>
