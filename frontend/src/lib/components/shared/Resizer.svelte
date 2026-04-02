<script lang="ts">
  function onMouseDown(e: MouseEvent) {
    e.preventDefault();
    const startX = e.clientX;
    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';

    function onMove(ev: MouseEvent) {
      const el = document.querySelector('.right-panel') as HTMLElement;
      if (el) {
        const w = window.innerWidth - ev.clientX;
        el.style.width = Math.max(400, Math.min(w, window.innerWidth - 250)) + 'px';
      }
    }
    function onUp() {
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
      document.removeEventListener('mousemove', onMove);
      document.removeEventListener('mouseup', onUp);
    }
    document.addEventListener('mousemove', onMove);
    document.addEventListener('mouseup', onUp);
  }
</script>

<div class="resizer" onmousedown={onMouseDown}></div>

<style>
  .resizer {
    position: absolute;
    left: -4px;
    top: 0;
    width: 8px;
    height: 100%;
    cursor: col-resize;
    z-index: 20;
  }
  .resizer::after {
    content: '';
    position: absolute;
    left: 3px;
    top: 0;
    width: 2px;
    height: 100%;
    background: transparent;
    transition: background 0.15s;
  }
  .resizer:hover::after {
    background: var(--accent);
  }
</style>
