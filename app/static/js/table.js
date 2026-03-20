/* ── AG Grid configuration — compact Börsdata-style ── */

const FLAG_MAP = {
  SE: '🇸🇪', DK: '🇩🇰', FI: '🇫🇮', NO: '🇳🇴',
};

function numFmt(dec) {
  return (p) => p.value != null ? Number(p.value).toFixed(dec) : '—';
}

function pctCell(p) {
  if (p.value == null) return '<span style="color:var(--text-dim)">—</span>';
  const v = Number(p.value).toFixed(1);
  const cls = p.value >= 0 ? 'text-positive' : 'text-negative';
  return `<span class="${cls}">${p.value >= 0 ? '+' : ''}${v}%</span>`;
}

function mcapFmt(p) {
  if (p.value == null) return '—';
  const v = p.value;
  if (v >= 1e12) return (v / 1e12).toFixed(1) + 'T';
  if (v >= 1e9) return (v / 1e9).toFixed(1) + 'B';
  if (v >= 1e6) return (v / 1e6).toFixed(0) + 'M';
  return v.toLocaleString();
}

function nameCell(p) {
  if (!p.data) return '';
  const f = FLAG_MAP[p.data.country] || '';
  return `<span style="display:inline-flex;align-items:center;gap:2px">${f ? '<span style="font-size:8px">' + f + '</span>' : ''}<span style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${p.value || ''}</span></span>`;
}

const COLUMN_DEFS = [
  { field: 'name', headerName: 'Name', width: 150, pinned: 'left', cellRenderer: nameCell },
  { field: 'ticker', headerName: 'Ticker', width: 82, pinned: 'left', cellStyle: { color: 'var(--accent)', fontWeight: '600' } },
  { field: 'change_pct', headerName: '1d', width: 54, type: 'numericColumn', cellRenderer: pctCell },
  { field: 'perf_1y', headerName: '1y', width: 54, type: 'numericColumn', cellRenderer: pctCell },
  { field: 'div_yield', headerName: 'Div', width: 42, type: 'numericColumn', valueFormatter: (p) => p.value != null ? p.value.toFixed(1) : '—' },
  { field: 'pe', headerName: 'P/E', width: 44, type: 'numericColumn', valueFormatter: numFmt(1) },
  { field: 'ps', headerName: 'P/S', width: 40, type: 'numericColumn', valueFormatter: numFmt(1) },
  { field: 'pb', headerName: 'P/B', width: 40, type: 'numericColumn', valueFormatter: numFmt(1) },
  { field: 'price', headerName: 'Price', width: 58, type: 'numericColumn', valueFormatter: numFmt(0) },
  { field: 'report_quarter', headerName: 'Report', width: 62, cellStyle: { color: 'var(--text-muted)' } },
  { field: 'sector', headerName: 'Sector', width: 100 },
  { field: 'ev_ebitda', headerName: 'EV/EB', width: 48, type: 'numericColumn', valueFormatter: numFmt(1) },
  { field: 'roe', headerName: 'ROE', width: 44, type: 'numericColumn', valueFormatter: (p) => p.value != null ? p.value.toFixed(0) + '%' : '—' },
  { field: 'margin', headerName: 'Mrgn', width: 44, type: 'numericColumn', valueFormatter: (p) => p.value != null ? p.value.toFixed(0) + '%' : '—' },
  { field: 'market_cap', headerName: 'MCap', width: 60, type: 'numericColumn', valueFormatter: mcapFmt },
  { field: 'industry', headerName: 'Industry', width: 110 },
  { field: 'country', headerName: 'Cty', width: 36 },
];

const GRID_OPTIONS = {
  columnDefs: COLUMN_DEFS,
  rowData: [],
  defaultColDef: {
    sortable: true,
    resizable: true,
    suppressMovable: true,
  },
  animateRows: true,
  rowSelection: 'single',
  suppressCellFocus: true,
  overlayNoRowsTemplate: '<div class="empty-state"><div class="icon">◆</div><div>No stocks found</div></div>',
  overlayLoadingTemplate: '<div class="empty-state loading-pulse">Loading...</div>',
};

let gridApi = null;

function initGrid(onRowSelected) {
  const el = document.getElementById('stock-grid');
  GRID_OPTIONS.onRowClicked = (event) => {
    if (event.data && onRowSelected) {
      onRowSelected(event.data.ticker);
    }
  };
  gridApi = agGrid.createGrid(el, GRID_OPTIONS);
  return gridApi;
}

function updateGridData(data) {
  if (gridApi) {
    gridApi.setGridOption('rowData', data);
  }
}

function selectGridRow(ticker) {
  if (!gridApi) return;
  gridApi.forEachNode((node) => {
    if (node.data && node.data.ticker === ticker) {
      node.setSelected(true, true);
    }
  });
}
