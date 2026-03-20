<script lang="ts">
  import { onMount } from 'svelte';
  import { getSectors } from '$lib/api/client';

  let { total, onFilter }: { total: number; onFilter: (f: { country: string|null; sector: string; search: string }) => void } = $props();

  let country = $state<string | null>(null);
  let sector = $state('');
  let search = $state('');
  let sectors = $state<string[]>([]);
  let searchTimeout: ReturnType<typeof setTimeout>;

  onMount(async () => { sectors = await getSectors(); });

  function emit() { onFilter({ country, sector, search }); }
  function setCountry(c: string | null) { country = c; emit(); }
  function onSearch() {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(emit, 300);
  }
</script>

<div class="filters">
  <div class="logo">
    <img src="/stonklens-appicon.png" alt="Stonklens" class="logo-icon" />
    <span class="logo-text">STONKLENS</span>
  </div>

  <div class="country-tabs">
    {#each [null, 'SE', 'DK', 'FI', 'NO'] as c}
      <button class="ctab" class:active={country === c} onclick={() => setCountry(c)}>
        {c ?? 'ALL'}
      </button>
    {/each}
  </div>

  <select class="sector-select" bind:value={sector} onchange={emit}>
    <option value="">All Sectors</option>
    {#each sectors as s}
      <option value={s}>{s}</option>
    {/each}
  </select>

  <div class="search-box">
    <input type="text" placeholder="Search..." bind:value={search} oninput={onSearch} />
  </div>

  <span class="count">{total} stocks</span>
</div>

<style>
  .filters { display: flex; align-items: center; gap: 14px; padding: 8px 14px; background: var(--bg-surface); border-bottom: 1px solid var(--border); height: 56px; }
  .logo { display: flex; align-items: center; gap: 8px; white-space: nowrap; flex-shrink: 0; }
  .logo-icon { height: 36px; width: 36px; border-radius: 6px; }
  .logo-text { font-family: var(--font-mono); font-weight: 600; font-size: 15px; color: var(--accent); letter-spacing: 3px; }
  .country-tabs { display: flex; gap: 1px; background: var(--bg); border-radius: 5px; padding: 2px; }
  .ctab {
    padding: 4px 11px; border: none; background: transparent; color: var(--text-muted);
    font-family: var(--font-mono); font-size: 10px; cursor: pointer; border-radius: 3px;
  }
  .ctab:hover { color: var(--text); background: var(--bg-hover); }
  .ctab.active { color: var(--accent); background: var(--bg-elevated); }
  .sector-select {
    background: var(--bg); border: 1px solid var(--border); color: var(--text);
    padding: 4px 8px; border-radius: 5px; font-family: var(--font-ui); font-size: 11px; cursor: pointer;
  }
  .search-box { margin-left: auto; }
  .search-box input {
    background: var(--bg); border: 1px solid var(--border); color: var(--text);
    padding: 4px 10px; border-radius: 5px; font-family: var(--font-mono); font-size: 10px; width: 160px;
  }
  .search-box input:focus { outline: none; border-color: var(--accent); }
  .count { font-family: var(--font-mono); font-size: 10px; color: var(--text-dim); white-space: nowrap; }
</style>
