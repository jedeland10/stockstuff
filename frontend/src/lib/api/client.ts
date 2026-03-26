import type { ScreenerResponse, CompanyDetail, PricePoint } from './types';

const BASE = '/api';

export async function getScreener(params: {
	country?: string | null;
	sector?: string;
	search?: string;
	sort_by?: string;
	sort_dir?: string;
	limit?: number;
	offset?: number;
}): Promise<ScreenerResponse> {
	const q = new URLSearchParams();
	if (params.country) q.set('country', params.country);
	if (params.sector) q.set('sector', params.sector);
	if (params.search) q.set('search', params.search);
	if (params.sort_by) q.set('sort_by', params.sort_by);
	if (params.sort_dir) q.set('sort_dir', params.sort_dir);
	q.set('limit', String(params.limit ?? 500));
	if (params.offset) q.set('offset', String(params.offset));
	const res = await fetch(`${BASE}/screener?${q}`);
	return res.json();
}

export async function getCompany(ticker: string): Promise<CompanyDetail> {
	const res = await fetch(`${BASE}/company/${encodeURIComponent(ticker)}`);
	return res.json();
}

export async function getChart(ticker: string, period = '1y'): Promise<PricePoint[]> {
	const res = await fetch(`${BASE}/chart/${encodeURIComponent(ticker)}?period=${period}`);
	return res.json();
}

export async function getSectors(): Promise<string[]> {
	const res = await fetch(`${BASE}/meta/sectors`);
	return res.json();
}

export async function getCountries(): Promise<string[]> {
	const res = await fetch(`${BASE}/meta/countries`);
	return res.json();
}

export interface StockScores {
	ticker: string;
	graham_number: number | null;
	f_score: number | null;
	magic_rank: number | null;
	magic_total: number;
}

export async function getScores(ticker: string): Promise<StockScores> {
	const res = await fetch(`${BASE}/scores/${encodeURIComponent(ticker)}`);
	return res.json();
}

export interface MagicFormulaEntry {
	ticker: string;
	name: string;
	country: string;
	sector: string;
	pe: number | null;
	price: number | null;
	earnings_yield: number | null;
	return_on_capital: number | null;
	magic_rank: number;
}

export interface FScoreEntry {
	ticker: string;
	name: string;
	country: string;
	sector: string;
	pe: number | null;
	price: number | null;
	f_score: number;
	profitability: number;
	leverage: number;
	efficiency: number;
}

export async function getMagicFormulaRanking(limit = 200): Promise<MagicFormulaEntry[]> {
	const res = await fetch(`${BASE}/scores/magic-formula/ranking?limit=${limit}`);
	return res.json();
}

export async function getFScoreRanking(limit = 200): Promise<FScoreEntry[]> {
	const res = await fetch(`${BASE}/scores/f-score/ranking?limit=${limit}`);
	return res.json();
}
