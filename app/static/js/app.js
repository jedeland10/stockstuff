/* ── Alpine.js app state ── */

document.addEventListener('alpine:init', () => {
  Alpine.data('screenerApp', () => ({
    // State
    stocks: [],
    total: 0,
    sectors: [],
    selectedTicker: null,
    companyData: null,
    chartPeriod: '1y',
    loading: false,
    tableExpanded: false,
    filters: {
      country: null,
      sector: '',
      search: '',
    },

    // Init
    async init() {
      await this.fetchSectors();
      await this.fetchScreener();

      // Init AG Grid
      this.$nextTick(() => {
        initGrid((ticker) => this.selectStock(ticker));
        updateGridData(this.stocks);
      });
    },

    // Formatters
    fmt(v) {
      if (v == null) return '—';
      return Number(v).toFixed(2);
    },

    fmtPct(v) {
      if (v == null) return '—';
      return Number(v).toFixed(1) + '%';
    },

    fmtLarge(v) {
      if (v == null) return '—';
      if (v >= 1e12) return (v / 1e12).toFixed(1) + 'T';
      if (v >= 1e9) return (v / 1e9).toFixed(1) + 'B';
      if (v >= 1e6) return (v / 1e6).toFixed(0) + 'M';
      return v.toLocaleString();
    },

    // Data fetching
    async fetchScreener() {
      const params = new URLSearchParams();
      if (this.filters.country) params.set('country', this.filters.country);
      if (this.filters.sector) params.set('sector', this.filters.sector);
      if (this.filters.search) params.set('search', this.filters.search);
      params.set('limit', '500');

      try {
        const res = await fetch('/api/screener?' + params);
        const data = await res.json();
        this.stocks = data.stocks;
        this.total = data.total;
        updateGridData(this.stocks);
      } catch (e) {
        console.error('Failed to fetch screener:', e);
      }
    },

    async fetchSectors() {
      try {
        const res = await fetch('/api/meta/sectors');
        this.sectors = await res.json();
      } catch (e) {
        console.error('Failed to fetch sectors:', e);
      }
    },

    // Actions
    setCountry(code) {
      this.filters.country = code;
      this.fetchScreener();
    },

    async selectStock(ticker) {
      if (this.selectedTicker === ticker) return;

      // Destroy old charts before Alpine re-renders the template
      destroyPriceChart();

      this.selectedTicker = ticker;
      this.companyData = null;
      selectGridRow(ticker);

      // Fetch company detail + chart in parallel
      try {
        const [companyRes, chartRes] = await Promise.all([
          fetch(`/api/company/${encodeURIComponent(ticker)}`),
          fetch(`/api/chart/${encodeURIComponent(ticker)}?period=${this.chartPeriod}`),
        ]);

        this.companyData = await companyRes.json();
        const chartData = await chartRes.json();

        // Wait for DOM, then render
        this.$nextTick(() => {
          setTimeout(() => {
            initPriceChart('price-chart');
            updatePriceChart(chartData);

            if (this.companyData && this.companyData.financials && this.companyData.financials.length) {
              renderFinancials(this.companyData.financials, this.companyData);
              renderRatioCharts(this.companyData.financials, this.companyData);
            }
          }, 80);
        });
      } catch (e) {
        console.error('Failed to fetch company:', e);
      }
    },

    async setChartPeriod(period) {
      this.chartPeriod = period;
      if (!this.selectedTicker) return;
      try {
        const res = await fetch(`/api/chart/${encodeURIComponent(this.selectedTicker)}?period=${period}`);
        const data = await res.json();
        // Re-init in case container was resized
        initPriceChart('price-chart');
        updatePriceChart(data);
      } catch (e) {
        console.error('Failed to fetch chart:', e);
      }
    },

    closeDetail() {
      destroyPriceChart();
      this.selectedTicker = null;
      this.companyData = null;
    },
  }));
});
