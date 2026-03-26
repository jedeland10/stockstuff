<script lang="ts">
  import { companyData } from '$lib/stores/screener';

  let expanded = $state(false);
</script>

{#if $companyData?.description}
<div class="desc-section">
  <button class="desc-toggle" onclick={() => expanded = !expanded}>
    <span class="desc-title">About</span>
    <svg class="chevron" class:rotated={expanded} viewBox="0 0 16 16" fill="none" width="12" height="12">
      <path d="M4 6L8 10L12 6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  </button>
  {#if expanded}
    <div class="desc-text">{$companyData.description}</div>
  {/if}
</div>
{/if}

<style>
  .desc-section {
    border-top: 1px solid var(--border);
  }
  .desc-toggle {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    padding: 10px 16px;
    background: none;
    border: none;
    cursor: pointer;
    color: var(--text-muted);
    transition: color 0.15s;
  }
  .desc-toggle:hover { color: var(--text); }
  .desc-title {
    font-family: var(--font-mono);
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.4px;
    font-weight: 600;
  }
  .chevron {
    transition: transform 0.2s;
  }
  .chevron.rotated { transform: rotate(180deg); }
  .desc-text {
    display: block;
    padding: 0 16px 14px;
    font-size: 12px;
    color: var(--text-muted);
    line-height: 1.6;
    white-space: pre-wrap;
    word-wrap: break-word;
    overflow-wrap: break-word;
  }
</style>
