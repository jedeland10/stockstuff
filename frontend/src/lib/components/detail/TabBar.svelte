<script lang="ts">
  import { activeTab } from '$lib/stores/screener';

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'report', label: 'Report' },
    { id: 'keynumbers', label: 'Key Numbers' },
    { id: 'technical', label: 'Technical' },
  ] as const;
</script>

<div class="tab-bar">
  {#each tabs as tab}
    <button
      class="tab"
      class:active={$activeTab === tab.id}
      onclick={() => activeTab.set(tab.id)}
    >
      {tab.label}
    </button>
  {/each}
</div>

<style>
  .tab-bar {
    display: flex;
    gap: 2px;
    padding: 0 12px;
    background: var(--bg-surface);
    border-bottom: 1px solid var(--border);
    flex-shrink: 0;
  }
  .tab {
    padding: 10px 14px;
    border: none;
    background: transparent;
    color: var(--text-muted);
    font-family: var(--font-mono);
    font-size: 11px;
    font-weight: 500;
    cursor: pointer;
    border-bottom: 2px solid transparent;
    text-transform: uppercase;
    letter-spacing: 0.3px;
    transition: all 0.15s;
    position: relative;
  }
  .tab:hover {
    color: var(--text);
  }
  .tab.active {
    color: var(--accent);
    border-bottom-color: var(--accent);
  }
</style>
