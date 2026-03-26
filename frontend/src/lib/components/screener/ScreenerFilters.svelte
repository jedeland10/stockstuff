<script lang="ts">
  import { onMount } from 'svelte';
  import { getSectors } from '$lib/api/client';

  let { total, onFilter }: { total: number; onFilter: (f: { country: string|null; sector: string; search: string }) => void } = $props();

  let country = $state<string | null>(null);
  let sector = $state('');
  let search = $state('');
  let sectors = $state<string[]>([]);
  let searchTimeout: ReturnType<typeof setTimeout>;
  let searchFocused = $state(false);

  onMount(async () => { sectors = await getSectors(); });

  function emit() { onFilter({ country, sector, search }); }
  function setCountry(c: string | null) { country = c; emit(); }
  function onSearch() {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(emit, 300);
  }

  const FLAG: Record<string, string> = { SE: '\u{1F1F8}\u{1F1EA}', DK: '\u{1F1E9}\u{1F1F0}', FI: '\u{1F1EB}\u{1F1EE}', NO: '\u{1F1F3}\u{1F1F4}' };
</script>

<div class="filters">
  <div class="logo">
    <img src="/stonklens-appicon.png" alt="Stonklens" class="logo-icon" />
    <span class="logo-text">STONKLENS</span>
  </div>

  <div class="divider"></div>

  <div class="country-tabs">
    {#each [null, 'SE', 'DK', 'FI', 'NO'] as c}
      <button class="ctab" class:active={country === c} onclick={() => setCountry(c)}>
        {#if c}
          <span class="tab-flag">{FLAG[c]}</span>
        {/if}
        {c ?? 'All'}
      </button>
    {/each}
  </div>

  <select class="sector-select" bind:value={sector} onchange={emit}>
    <option value="">All Sectors</option>
    {#each sectors as s}
      <option value={s}>{s}</option>
    {/each}
  </select>

  <div class="spacer"></div>

  <div class="search-box" class:focused={searchFocused}>
    <svg class="search-icon" viewBox="0 0 16 16" fill="none">
      <circle cx="7" cy="7" r="5.5" stroke="currentColor" stroke-width="1.5"/>
      <path d="M11 11L14 14" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
    </svg>
    <input type="text" placeholder="Search stocks..." bind:value={search} oninput={onSearch}
      onfocus={() => searchFocused = true} onblur={() => searchFocused = false} />
  </div>

  <span class="count">{total} stocks</span>
</div>

<style>
  .filters {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 0 16px;
    background: var(--bg-surface);
    border-bottom: 1px solid var(--border);
    height: 52px;
    flex-shrink: 0;
  }
  .logo { display: flex; align-items: center; gap: 8px; white-space: nowrap; flex-shrink: 0; }
  .logo-icon { height: 32px; width: 32px; border-radius: 8px; }
  .logo-text {
    font-family: var(--font-mono); font-weight: 700; font-size: 14px;
    color: var(--accent); letter-spacing: 2.5px;
  }

  .divider {
    width: 1px;
    height: 24px;
    background: var(--border);
    flex-shrink: 0;
  }

  .country-tabs {
    display: flex;
    gap: 2px;
    background: var(--bg);
    border-radius: 8px;
    padding: 3px;
    border: 1px solid var(--border);
  }
  .ctab {
    padding: 5px 12px;
    border: none;
    background: transparent;
    color: var(--text-muted);
    font-family: var(--font-mono);
    font-size: 11px;
    font-weight: 500;
    cursor: pointer;
    border-radius: 6px;
    transition: all 0.15s;
    display: flex;
    align-items: center;
    gap: 4px;
  }
  .ctab:hover { color: var(--text); background: var(--bg-hover); }
  .ctab.active {
    color: var(--text);
    background: var(--bg-elevated);
    box-shadow: 0 1px 3px rgba(0,0,0,0.2);
  }
  .tab-flag { font-size: 11px; }

  .sector-select {
    background: var(--bg);
    border: 1px solid var(--border);
    color: var(--text-muted);
    padding: 6px 10px;
    border-radius: 8px;
    font-family: var(--font-ui);
    font-size: 12px;
    cursor: pointer;
    transition: border-color 0.15s;
  }
  .sector-select:hover, .sector-select:focus { border-color: var(--text-dim); color: var(--text); outline: none; }

  .spacer { flex: 1; }

  .search-box {
    display: flex;
    align-items: center;
    gap: 6px;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0 10px;
    transition: all 0.2s;
    width: 200px;
  }
  .search-box.focused {
    border-color: var(--accent);
    box-shadow: 0 0 0 2px var(--accent-dim);
    width: 240px;
  }
  .search-icon {
    width: 14px;
    height: 14px;
    color: var(--text-dim);
    flex-shrink: 0;
  }
  .search-box.focused .search-icon { color: var(--accent); }
  .search-box input {
    background: none;
    border: none;
    color: var(--text);
    padding: 6px 0;
    font-family: var(--font-mono);
    font-size: 11px;
    width: 100%;
    outline: none;
  }
  .search-box input::placeholder { color: var(--text-dim); }

  .count {
    font-family: var(--font-mono);
    font-size: 10px;
    color: var(--text-dim);
    white-space: nowrap;
    background: var(--bg);
    padding: 4px 8px;
    border-radius: 6px;
    border: 1px solid var(--border);
  }
</style>
