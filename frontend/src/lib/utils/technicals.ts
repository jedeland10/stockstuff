export function computeMA(data: number[], period: number): (number | null)[] {
	const result: (number | null)[] = [];
	for (let i = 0; i < data.length; i++) {
		if (i < period - 1) {
			result.push(null);
		} else {
			let sum = 0;
			for (let j = 0; j < period; j++) sum += data[i - j];
			result.push(sum / period);
		}
	}
	return result;
}

export function computeRSI(closes: number[], period = 14): (number | null)[] {
	const result = new Array(closes.length).fill(null);
	if (closes.length < period + 1) return result;

	let avgGain = 0, avgLoss = 0;
	for (let i = 1; i <= period; i++) {
		const c = closes[i] - closes[i - 1];
		if (c >= 0) avgGain += c; else avgLoss += Math.abs(c);
	}
	avgGain /= period;
	avgLoss /= period;
	result[period] = avgLoss === 0 ? 100 : 100 - 100 / (1 + avgGain / avgLoss);

	for (let i = period + 1; i < closes.length; i++) {
		const c = closes[i] - closes[i - 1];
		avgGain = (avgGain * (period - 1) + (c >= 0 ? c : 0)) / period;
		avgLoss = (avgLoss * (period - 1) + (c < 0 ? Math.abs(c) : 0)) / period;
		result[i] = avgLoss === 0 ? 100 : 100 - 100 / (1 + avgGain / avgLoss);
	}
	return result;
}

export function computePerformance(closes: number[], dates: string[]): Record<string, number | null> {
	if (!closes.length) return {};
	const last = closes[closes.length - 1];
	const periods: Record<string, number> = { '1d': 1, '1w': 5, '1m': 21, '3m': 63, '6m': 126, '1y': 252 };
	const result: Record<string, number | null> = {};

	for (const [label, days] of Object.entries(periods)) {
		if (closes.length > days) {
			const ref = closes[closes.length - 1 - days];
			result[label] = ((last - ref) / ref) * 100;
		} else {
			result[label] = null;
		}
	}

	// YTD
	const year = new Date().getFullYear().toString();
	const ytdIdx = dates.findIndex(d => d.startsWith(year));
	if (ytdIdx >= 0) {
		result['YTD'] = ((last - closes[ytdIdx]) / closes[ytdIdx]) * 100;
	} else {
		result['YTD'] = null;
	}

	return result;
}
