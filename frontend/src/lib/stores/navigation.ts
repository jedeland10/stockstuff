import { writable } from 'svelte/store';

export type AppView = 'dashboard' | 'screener' | 'watchlist' | 'rankings' | 'highlights';

const VALID_VIEWS: AppView[] = ['dashboard', 'screener', 'watchlist', 'rankings', 'highlights'];

function getInitialView(): AppView {
	if (typeof window === 'undefined') return 'dashboard';
	const params = new URLSearchParams(window.location.search);
	const view = params.get('view');
	if (view && VALID_VIEWS.includes(view as AppView)) return view as AppView;
	// If there's a stock param but no view, go to screener
	if (params.get('stock')) return 'screener';
	return 'dashboard';
}

export const currentView = writable<AppView>(getInitialView());
