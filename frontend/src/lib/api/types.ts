export interface StockRow {
	ticker: string;
	name: string | null;
	country: string | null;
	sector: string | null;
	price: number | null;
	change_pct: number | null;
	pe: number | null;
	pb: number | null;
	ps: number | null;
	ev_ebitda: number | null;
	div_yield: number | null;
	roe: number | null;
	margin: number | null;
	market_cap: number | null;
	perf_1y: number | null;
	report_quarter: string | null;
	industry: string | null;
}

export interface ScreenerResponse {
	stocks: StockRow[];
	total: number;
}

export interface PricePoint {
	date: string;
	open: number | null;
	high: number | null;
	low: number | null;
	close: number | null;
	volume: number | null;
}

export interface AnnualFinancial {
	year: number;
	revenue: number | null;
	operating_income: number | null;
	ebitda: number | null;
	net_income: number | null;
	eps: number | null;
	profit_margin: number | null;
}

export interface QuarterlyFinancial {
	period: string;
	revenue: number | null;
	operating_income: number | null;
	ebitda: number | null;
	net_income: number | null;
	eps: number | null;
	profit_margin: number | null;
}

export interface BalanceSheetEntry {
	year: number;
	total_assets: number | null;
	total_debt: number | null;
	net_debt: number | null;
	cash: number | null;
	total_equity: number | null;
	intangible_assets: number | null;
}

export interface CashflowEntry {
	year: number;
	operating_cf: number | null;
	capex: number | null;
	free_cf: number | null;
}

export interface CompanyDetail {
	ticker: string;
	name: string | null;
	exchange: string | null;
	country: string | null;
	sector: string | null;
	industry: string | null;
	market_cap: number | null;
	description: string | null;
	price: number | null;
	change_pct: number | null;
	pe: number | null;
	pb: number | null;
	ps: number | null;
	ev_ebitda: number | null;
	div_yield: number | null;
	roe: number | null;
	margin: number | null;
	eps: number | null;
	revenue: number | null;
	revenue_growth: number | null;
	financials: AnnualFinancial[];
	quarterly_financials: QuarterlyFinancial[];
	balance_sheet: BalanceSheetEntry[];
	cashflow: CashflowEntry[];
}
