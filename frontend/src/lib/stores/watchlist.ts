import { writable } from 'svelte/store';

const STORAGE_KEY = 'stonklens-watchlist';

function loadFromStorage(): Set<string> {
	try {
		const raw = localStorage.getItem(STORAGE_KEY);
		if (raw) return new Set(JSON.parse(raw));
	} catch {}
	return new Set();
}

function createWatchlistStore() {
	const stored = loadFromStorage();
	const { subscribe, set, update } = writable<Set<string>>(stored);

	function persist(s: Set<string>) {
		localStorage.setItem(STORAGE_KEY, JSON.stringify([...s]));
	}

	return {
		subscribe,
		toggle(ticker: string) {
			update(s => {
				const next = new Set(s);
				if (next.has(ticker)) {
					next.delete(ticker);
				} else {
					next.add(ticker);
				}
				persist(next);
				return next;
			});
		},
		has(s: Set<string>, ticker: string): boolean {
			return s.has(ticker);
		},
	};
}

export const watchlist = createWatchlistStore();
