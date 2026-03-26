<script lang="ts">
  import { onMount } from 'svelte';
  import { getSectors } from '$lib/api/client';
  import { watchlist } from '$lib/stores/watchlist';
  import { visibleColumns, ALL_COLUMNS, LOCKED_COLUMNS, PRESETS, type ColumnKey } from '$lib/stores/columns';
  import { theme } from '$lib/stores/theme';

  let { total, onFilter, watchlistActive, onToggleWatchlist, onExport }: {
    total: number;
    onFilter: (f: { country: string|null; sector: string; search: string }) => void;
    watchlistActive: boolean;
    onToggleWatchlist: () => void;
    onExport: () => void;
  } = $props();

  let country = $state<string | null>(null);
  let sector = $state('');
  let search = $state('');
  let sectors = $state<string[]>([]);
  let searchTimeout: ReturnType<typeof setTimeout>;
  let searchFocused = $state(false);
  let columnsOpen = $state(false);
  let columnsBtn: HTMLButtonElement;

  onMount(async () => {
    sectors = await getSectors();
  });

  function emit() { onFilter({ country, sector, search }); }
  function setCountry(c: string | null) { country = c; emit(); }
  function onSearch() {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(emit, 300);
  }

  function handleClickOutside(e: MouseEvent) {
    if (columnsOpen && columnsBtn && !columnsBtn.contains(e.target as Node)) {
      const dropdown = document.querySelector('.columns-dropdown');
      if (dropdown && !dropdown.contains(e.target as Node)) {
        columnsOpen = false;
      }
    }
  }

  $effect(() => {
    if (columnsOpen) {
      document.addEventListener('click', handleClickOutside, true);
      return () => document.removeEventListener('click', handleClickOutside, true);
    }
  });

  const groups = $derived.by(() => {
    const map = new Map<string, typeof ALL_COLUMNS[number][]>();
    for (const col of ALL_COLUMNS) {
      if (!map.has(col.group)) map.set(col.group, []);
      map.get(col.group)!.push(col);
    }
    return map;
  });

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

  <button class="watchlist-btn" class:active={watchlistActive} onclick={onToggleWatchlist} title="Show watchlist only">
    <svg viewBox="0 0 16 16" width="14" height="14" fill={watchlistActive ? 'var(--gold)' : 'none'} stroke={watchlistActive ? 'var(--gold)' : 'currentColor'} stroke-width="1.3">
      <path d="M8 1.5l2 4.1 4.5.6-3.3 3.2.8 4.5L8 11.6l-4 2.3.8-4.5L1.5 6.2 6 5.6z"/>
    </svg>
    <span>Watchlist</span>
    {#if $watchlist.size > 0}
      <span class="watchlist-count">{$watchlist.size}</span>
    {/if}
  </button>

  <div class="columns-wrap">
    <button class="columns-btn" class:active={columnsOpen} bind:this={columnsBtn}
      onclick={() => columnsOpen = !columnsOpen} title="Configure columns">
      <svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.4">
        <rect x="1.5" y="2" width="4" height="12" rx="1"/>
        <rect x="6.5" y="2" width="4" height="12" rx="1"/>
        <rect x="11.5" y="2" width="3" height="12" rx="1"/>
      </svg>
      <span>Columns</span>
    </button>

    {#if columnsOpen}
      <div class="columns-dropdown">
        <div class="dropdown-header">
          <span class="dropdown-title">Visible Columns</span>
        </div>

        <div class="presets-row">
          {#each Object.entries(PRESETS) as [key, preset]}
            <button class="preset-btn" onclick={() => visibleColumns.applyPreset(key)}>{preset.label}</button>
          {/each}
        </div>

        <div class="columns-list">
          {#each groups as [group, groupCols]}
            <div class="col-group">
              <span class="group-label">{group}</span>
              {#each groupCols as col}
                {@const isLocked = (LOCKED_COLUMNS as readonly string[]).includes(col.key)}
                <label class="col-item" class:locked={isLocked}>
                  <input
                    type="checkbox"
                    checked={$visibleColumns.includes(col.key)}
                    disabled={isLocked}
                    onchange={() => visibleColumns.toggle(col.key)}
                  />
                  <span class="col-name">{col.label}</span>
                  {#if isLocked}
                    <span class="lock-icon">
                      <svg viewBox="0 0 12 12" width="10" height="10" fill="none" stroke="currentColor" stroke-width="1.2">
                        <rect x="2" y="5" width="8" height="6" rx="1"/>
                        <path d="M4 5V3.5a2 2 0 014 0V5"/>
                      </svg>
                    </span>
                  {/if}
                </label>
              {/each}
            </div>
          {/each}
        </div>
      </div>
    {/if}
  </div>

  <div class="spacer"></div>

  <div class="search-box" class:focused={searchFocused}>
    <svg class="search-icon" viewBox="0 0 16 16" fill="none">
      <circle cx="7" cy="7" r="5.5" stroke="currentColor" stroke-width="1.5"/>
      <path d="M11 11L14 14" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
    </svg>
    <input type="text" placeholder="Search stocks..." bind:value={search} oninput={onSearch}
      onfocus={() => searchFocused = true} onblur={() => searchFocused = false} />
  </div>

  <button class="export-btn" onclick={onExport} title="Export to CSV">
    <svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round">
      <path d="M8 2v8M5 7l3 3 3-3M3 12h10"/>
    </svg>
    <span>CSV</span>
  </button>

  <button class="theme-btn" onclick={() => theme.toggle()} title={$theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}>
    {#if $theme === 'dark'}
      <svg viewBox="0 0 16 16" width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.3">
        <circle cx="8" cy="8" r="3.5"/>
        <path d="M8 1.5v1.5M8 13v1.5M1.5 8H3M13 8h1.5M3.4 3.4l1.1 1.1M11.5 11.5l1.1 1.1M3.4 12.6l1.1-1.1M11.5 4.5l1.1-1.1"/>
      </svg>
    {:else}
      <svg viewBox="0 0 16 16" width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.3">
        <path d="M13.5 9.2A5.5 5.5 0 016.8 2.5 6 6 0 1013.5 9.2z"/>
      </svg>
    {/if}
  </button>

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

  .watchlist-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px 12px;
    border: 1px solid var(--border);
    border-radius: 8px;
    background: var(--bg);
    color: var(--text-muted);
    font-family: var(--font-mono);
    font-size: 11px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.15s;
    white-space: nowrap;
  }
  .watchlist-btn:hover {
    border-color: var(--text-dim);
    color: var(--text);
  }
  .watchlist-btn.active {
    border-color: var(--gold);
    background: rgba(210, 153, 34, 0.08);
    color: var(--gold);
  }
  .watchlist-count {
    background: var(--bg-hover);
    padding: 0 5px;
    border-radius: 4px;
    font-size: 10px;
    line-height: 1.6;
  }
  .watchlist-btn.active .watchlist-count {
    background: rgba(210, 153, 34, 0.15);
  }

  .columns-wrap {
    position: relative;
  }
  .columns-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px 12px;
    border: 1px solid var(--border);
    border-radius: 8px;
    background: var(--bg);
    color: var(--text-muted);
    font-family: var(--font-mono);
    font-size: 11px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.15s;
    white-space: nowrap;
  }
  .columns-btn:hover {
    border-color: var(--text-dim);
    color: var(--text);
  }
  .columns-btn.active {
    border-color: var(--accent);
    color: var(--accent);
  }

  .columns-dropdown {
    position: absolute;
    top: calc(100% + 8px);
    left: 0;
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
    z-index: 100;
    width: 260px;
    animation: dropdown-in 0.15s ease-out;
  }

  @keyframes dropdown-in {
    from { opacity: 0; transform: translateY(-4px); }
    to { opacity: 1; transform: translateY(0); }
  }

  .dropdown-header {
    padding: 10px 14px 6px;
  }
  .dropdown-title {
    font-family: var(--font-mono);
    font-size: 10px;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.4px;
  }

  .presets-row {
    display: flex;
    gap: 4px;
    padding: 4px 14px 8px;
    flex-wrap: wrap;
    border-bottom: 1px solid var(--border);
  }
  .preset-btn {
    padding: 3px 8px;
    border: 1px solid var(--border);
    border-radius: 5px;
    background: var(--bg);
    color: var(--text-dim);
    font-family: var(--font-mono);
    font-size: 9px;
    cursor: pointer;
    transition: all 0.12s;
  }
  .preset-btn:hover {
    border-color: var(--accent);
    color: var(--accent);
    background: var(--accent-dim);
  }

  .columns-list {
    padding: 8px 0;
    max-height: 320px;
    overflow-y: auto;
  }
  .col-group {
    padding: 0 14px;
  }
  .col-group + .col-group {
    margin-top: 6px;
    padding-top: 6px;
    border-top: 1px solid rgba(48, 54, 61, 0.4);
  }
  .group-label {
    display: block;
    font-family: var(--font-mono);
    font-size: 9px;
    color: var(--text-dim);
    text-transform: uppercase;
    letter-spacing: 0.3px;
    margin-bottom: 4px;
    padding-left: 2px;
  }
  .col-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 4px 4px;
    border-radius: 5px;
    cursor: pointer;
    transition: background 0.1s;
  }
  .col-item:hover { background: var(--bg-hover); }
  .col-item.locked {
    cursor: default;
    opacity: 0.5;
  }
  .col-item input[type="checkbox"] {
    accent-color: var(--accent);
    width: 14px;
    height: 14px;
    cursor: pointer;
    flex-shrink: 0;
  }
  .col-item.locked input { cursor: default; }
  .col-name {
    font-family: var(--font-ui);
    font-size: 12px;
    color: var(--text);
    flex: 1;
  }
  .lock-icon {
    color: var(--text-dim);
    display: flex;
  }

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

  .export-btn {
    display: flex;
    align-items: center;
    gap: 5px;
    padding: 6px 10px;
    border: 1px solid var(--border);
    border-radius: 8px;
    background: var(--bg);
    color: var(--text-muted);
    font-family: var(--font-mono);
    font-size: 10px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.15s;
    white-space: nowrap;
  }
  .export-btn:hover {
    border-color: var(--text-dim);
    color: var(--text);
  }

  .theme-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border: 1px solid var(--border);
    border-radius: 8px;
    background: var(--bg);
    color: var(--text-muted);
    cursor: pointer;
    transition: all 0.15s;
    flex-shrink: 0;
  }
  .theme-btn:hover {
    border-color: var(--text-dim);
    color: var(--text);
  }

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
