import { writable, get } from 'svelte/store';
import { getScreener, getCompany, getChart } from '$lib/api/client';
import { selectedTicker, companyData, chartData, activeTab } from '$lib/stores/screener';
import type { StockRow } from '$lib/api/types';

const PAGE_SIZE = 100;

export const stocks = writable<StockRow[]>([]);
export const stockTotal = writable(0);
export const stockLoading = writable(false);
export const stockHasMore = writable(true);

let _screenerLoaded = false;
let _currentFilters = { country: null as string | null, sector: '', search: '' };
let _sortBy = 'market_cap';
let _sortDir: 'asc' | 'desc' = 'desc';

export async function loadScreener(filters?: { country: string | null; sector: string; search: string }) {
	if (filters) {
		_currentFilters = filters;
		stocks.set([]);
	}
	stockLoading.set(true);
	const current = get(stocks);
	const data = await getScreener({
		..._currentFilters,
		sort_by: _sortBy,
		sort_dir: _sortDir,
		limit: PAGE_SIZE,
		offset: filters ? 0 : current.length,
	});
	if (filters) {
		stocks.set(data.stocks);
	} else {
		stocks.update(s => [...s, ...data.stocks]);
	}
	stockTotal.set(data.total);
	stockHasMore.set((filters ? data.stocks.length : current.length + data.stocks.length) < data.total);
	stockLoading.set(false);
	_screenerLoaded = true;
}

export async function ensureAllStocksLoaded() {
	if (!_screenerLoaded) await loadScreener(_currentFilters);
	if (get(stockHasMore)) {
		stockLoading.set(true);
		let total = get(stockTotal);
		while (get(stocks).length < total) {
			const data = await getScreener({
				..._currentFilters,
				sort_by: _sortBy,
				sort_dir: _sortDir,
				limit: PAGE_SIZE,
				offset: get(stocks).length,
			});
			stocks.update(s => [...s, ...data.stocks]);
			stockTotal.set(data.total);
			total = data.total;
			if (data.stocks.length === 0) break;
		}
		stockHasMore.set(false);
		stockLoading.set(false);
	}
}

export async function loadMore() {
	if (get(stockLoading) || !get(stockHasMore)) return;
	await loadScreener();
}

export async function sortScreener(col: string, dir: 'asc' | 'desc') {
	_sortBy = col;
	_sortDir = dir;
	stocks.set([]);
	await loadScreener(_currentFilters);
}

export async function selectStock(ticker: string) {
	if (get(selectedTicker) === ticker) return;
	selectedTicker.set(ticker);
	activeTab.set('overview');
	const [cd, chart] = await Promise.all([
		getCompany(ticker),
		getChart(ticker, 'max'),
	]);
	companyData.set(cd);
	chartData.set(chart);
}

export async function exportCsv() {
	await ensureAllStocksLoaded();
	const allStocks = get(stocks);
	const fields: { key: keyof StockRow; label: string }[] = [
		{ key: 'name', label: 'Name' },
		{ key: 'ticker', label: 'Ticker' },
		{ key: 'country', label: 'Country' },
		{ key: 'sector', label: 'Sector' },
		{ key: 'industry', label: 'Industry' },
		{ key: 'price', label: 'Price' },
		{ key: 'change_pct', label: '1d Change' },
		{ key: 'perf_1y', label: '1y Change' },
		{ key: 'market_cap', label: 'Market Cap' },
		{ key: 'pe', label: 'P/E' },
		{ key: 'pb', label: 'P/B' },
		{ key: 'ps', label: 'P/S' },
		{ key: 'ev_ebitda', label: 'EV/EBITDA' },
		{ key: 'div_yield', label: 'Div Yield' },
		{ key: 'roe', label: 'ROE' },
		{ key: 'margin', label: 'Margin' },
		{ key: 'report_quarter', label: 'Report Quarter' },
	];
	const header = fields.map(f => f.label).join(',');
	const rows = allStocks.map(stock => {
		return fields.map(f => {
			const val = stock[f.key];
			if (val == null) return '';
			if (typeof val === 'string' && val.includes(',')) return `"${val}"`;
			return String(val);
		}).join(',');
	});
	const csv = [header, ...rows].join('\n');
	const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
	const url = URL.createObjectURL(blob);
	const a = document.createElement('a');
	a.href = url;
	a.download = `stonklens-${new Date().toISOString().slice(0, 10)}.csv`;
	a.click();
	URL.revokeObjectURL(url);
}

export function ensureScreenerData() {
	if (!_screenerLoaded && !get(stockLoading)) {
		loadScreener(_currentFilters);
	}
}
