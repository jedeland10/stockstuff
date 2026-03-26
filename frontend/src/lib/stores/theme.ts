import { writable } from 'svelte/store';

const STORAGE_KEY = 'stonklens-theme';
type Theme = 'dark' | 'light';

function loadTheme(): Theme {
	try {
		const stored = localStorage.getItem(STORAGE_KEY);
		if (stored === 'light' || stored === 'dark') return stored;
	} catch {}
	return 'dark';
}

function createThemeStore() {
	const { subscribe, set, update } = writable<Theme>(loadTheme());

	// Apply on init
	if (typeof document !== 'undefined') {
		document.documentElement.setAttribute('data-theme', loadTheme());
	}

	return {
		subscribe,
		toggle() {
			update(current => {
				const next: Theme = current === 'dark' ? 'light' : 'dark';
				localStorage.setItem(STORAGE_KEY, next);
				document.documentElement.setAttribute('data-theme', next);
				return next;
			});
		},
	};
}

export const theme = createThemeStore();

/** Read a CSS variable value from the document root. Useful for chart libraries that need raw color strings. */
export function cssVar(name: string): string {
	return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}
