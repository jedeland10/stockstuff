<script lang="ts">
  import '../app.css';
  import favicon from '$lib/assets/favicon.svg';
  // Import theme store to ensure data-theme attribute is set on mount
  import '$lib/stores/theme';

  let { children } = $props();
</script>

<svelte:head>
  <link rel="icon" href={favicon} />
</svelte:head>

{@render children()}
