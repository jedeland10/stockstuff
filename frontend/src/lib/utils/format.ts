export function fmt(v: number | null | undefined, decimals = 2): string {
	if (v == null) return '—';
	return Number(v).toFixed(decimals);
}

export function fmtPct(v: number | null | undefined): string {
	if (v == null) return '—';
	return Number(v).toFixed(1) + '%';
}

export function fmtSignPct(v: number | null | undefined): string {
	if (v == null) return '—';
	const n = Number(v);
	return (n >= 0 ? '+' : '') + n.toFixed(1) + '%';
}

export function fmtLarge(v: number | null | undefined): string {
	if (v == null) return '—';
	const n = Number(v);
	if (Math.abs(n) >= 1e12) return (n / 1e12).toFixed(1) + 'T';
	if (Math.abs(n) >= 1e9) return (n / 1e9).toFixed(1) + 'B';
	if (Math.abs(n) >= 1e6) return (n / 1e6).toFixed(0) + 'M';
	return n.toLocaleString();
}

export function fmtNum(v: number | null | undefined): string {
	if (v == null) return '—';
	return Number(v).toFixed(2);
}
