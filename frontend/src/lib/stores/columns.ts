import { writable } from 'svelte/store';

const STORAGE_KEY = 'stonklens-columns';

/** Columns that are always shown and cannot be toggled off */
export const LOCKED_COLUMNS = ['name', 'ticker'] as const;

/** All available column definitions */
export const ALL_COLUMNS = [
	{ key: 'name', label: 'Name', group: 'Core' },
	{ key: 'ticker', label: 'Ticker', group: 'Core' },
	{ key: 'change_pct', label: '1d Change', group: 'Performance' },
	{ key: 'perf_1w', label: '1w Change', group: 'Performance' },
	{ key: 'perf_1m', label: '1m Change', group: 'Performance' },
	{ key: 'perf_1y', label: '1y Change', group: 'Performance' },
	{ key: 'price', label: 'Price', group: 'Core' },
	{ key: 'market_cap', label: 'Market Cap', group: 'Core' },
	{ key: 'div_yield', label: 'Div Yield', group: 'Valuation' },
	{ key: 'pe', label: 'P/E', group: 'Valuation' },
	{ key: 'ps', label: 'P/S', group: 'Valuation' },
	{ key: 'pb', label: 'P/B', group: 'Valuation' },
	{ key: 'ev_ebitda', label: 'EV/EBITDA', group: 'Valuation' },
	{ key: 'roe', label: 'ROE', group: 'Quality' },
	{ key: 'margin', label: 'Margin', group: 'Quality' },
	{ key: 'report_quarter', label: 'Report', group: 'Info' },
	{ key: 'sector', label: 'Sector', group: 'Info' },
] as const;

export type ColumnKey = (typeof ALL_COLUMNS)[number]['key'];

const DEFAULT_VISIBLE: ColumnKey[] = [
	'name', 'ticker', 'change_pct', 'perf_1w', 'perf_1m', 'perf_1y', 'div_yield',
	'pe', 'ps', 'pb', 'price', 'report_quarter', 'sector',
	'ev_ebitda', 'roe', 'margin', 'market_cap',
];

export const PRESETS: Record<string, { label: string; columns: ColumnKey[] }> = {
	all: {
		label: 'All Columns',
		columns: ALL_COLUMNS.map(c => c.key),
	},
	valuation: {
		label: 'Valuation',
		columns: ['name', 'ticker', 'price', 'pe', 'pb', 'ps', 'ev_ebitda', 'div_yield', 'market_cap'],
	},
	performance: {
		label: 'Performance',
		columns: ['name', 'ticker', 'price', 'change_pct', 'perf_1w', 'perf_1m', 'perf_1y', 'roe', 'margin', 'market_cap'],
	},
	compact: {
		label: 'Compact',
		columns: ['name', 'ticker', 'price', 'change_pct', 'pe', 'div_yield', 'market_cap'],
	},
};

function loadFromStorage(): ColumnKey[] {
	try {
		const raw = localStorage.getItem(STORAGE_KEY);
		if (raw) {
			const parsed = JSON.parse(raw) as string[];
			// Validate keys
			const validKeys = new Set(ALL_COLUMNS.map(c => c.key));
			const filtered = parsed.filter(k => validKeys.has(k as ColumnKey)) as ColumnKey[];
			if (filtered.length > 0) return filtered;
		}
	} catch {}
	return DEFAULT_VISIBLE;
}

function createColumnsStore() {
	const { subscribe, set, update } = writable<ColumnKey[]>(loadFromStorage());

	function persist(cols: ColumnKey[]) {
		localStorage.setItem(STORAGE_KEY, JSON.stringify(cols));
	}

	return {
		subscribe,
		toggle(key: ColumnKey) {
			if ((LOCKED_COLUMNS as readonly string[]).includes(key)) return;
			update(cols => {
				const next = cols.includes(key)
					? cols.filter(c => c !== key)
					: [...cols, key];
				persist(next);
				return next;
			});
		},
		applyPreset(presetKey: string) {
			const preset = PRESETS[presetKey];
			if (!preset) return;
			persist(preset.columns);
			set(preset.columns);
		},
		reset() {
			persist(DEFAULT_VISIBLE);
			set(DEFAULT_VISIBLE);
		},
	};
}

export const visibleColumns = createColumnsStore();
