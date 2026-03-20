import { writable } from 'svelte/store';
import type { StockRow, CompanyDetail, PricePoint } from '$lib/api/types';

export const selectedTicker = writable<string | null>(null);
export const companyData = writable<CompanyDetail | null>(null);
export const chartData = writable<PricePoint[]>([]);
export const activeTab = writable<'overview' | 'report' | 'keynumbers' | 'technical'>('overview');
export const rightPanelWidth = writable(680);
