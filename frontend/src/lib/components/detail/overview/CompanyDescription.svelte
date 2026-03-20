<script lang="ts">
  import { companyData } from '$lib/stores/screener';
</script>

{#if $companyData?.description}
<div class="desc">{$companyData.description}</div>
{/if}

<style>
  .desc {
    padding: 10px 14px;
    font-size: 12px;
    color: var(--text-muted);
    line-height: 1.5;
    border-top: 1px solid var(--border);
  }
</style>
