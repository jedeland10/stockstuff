/* ── Alpine.js app state ── */

document.addEventListener('alpine:init', () => {
  Alpine.data('screenerApp', () => ({
    stocks: [],
    total: 0,
    sectors: [],
    selectedTicker: null,
    companyData: null,
    chartPeriod: '1y',
    techPeriod: '1y',
    activeTab: 'overview',
    rightPanelWidth: 680,
    loading: false,
    tableExpanded: false,
    _chartData: null,
    filters: { country: null, sector: '', search: '' },

    async init() {
      await this.fetchSectors();
      await this.fetchScreener();
      this.$nextTick(() => {
        initGrid((ticker) => this.selectStock(ticker));
        updateGridData(this.stocks);
      });
    },

    // Formatters
    fmt(v) { return v != null ? Number(v).toFixed(2) : '—'; },
    fmtPct(v) { return v != null ? Number(v).toFixed(1) + '%' : '—'; },
    fmtLarge(v) {
      if (v == null) return '—';
      if (v >= 1e12) return (v / 1e12).toFixed(1) + 'T';
      if (v >= 1e9) return (v / 1e9).toFixed(1) + 'B';
      if (v >= 1e6) return (v / 1e6).toFixed(0) + 'M';
      return v.toLocaleString();
    },

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
      } catch (e) { console.error('Screener fetch failed:', e); }
    },

    async fetchSectors() {
      try { this.sectors = await (await fetch('/api/meta/sectors')).json(); }
      catch (e) { console.error(e); }
    },

    setCountry(code) { this.filters.country = code; this.fetchScreener(); },

    async selectStock(ticker) {
      if (this.selectedTicker === ticker) return;
      destroyPriceChart();
      destroyTechChart();
      this.selectedTicker = ticker;
      this.companyData = null;
      this.activeTab = 'overview';
      this._chartData = null;
      selectGridRow(ticker);

      try {
        const [companyRes, chartRes] = await Promise.all([
          fetch(`/api/company/${encodeURIComponent(ticker)}`),
          fetch(`/api/chart/${encodeURIComponent(ticker)}?period=${this.chartPeriod}`),
        ]);
        this.companyData = await companyRes.json();
        this._chartData = await chartRes.json();
        this.$nextTick(() => setTimeout(() => this.renderCurrentTab(), 150));
      } catch (e) { console.error('Company fetch failed:', e); }
    },

    switchTab(tab) {
      this.activeTab = tab;
      this.$nextTick(() => setTimeout(() => this.renderCurrentTab(), 100));
    },

    renderCurrentTab() {
      const cd = this.companyData;
      if (!cd) return;

      if (this.activeTab === 'overview') {
        initPriceChart('price-chart');
        if (this._chartData) updatePriceChart(this._chartData);
        if (cd.financials && cd.financials.length) renderFinancials(cd.financials, cd);
      } else if (this.activeTab === 'report') {
        renderReportTab(cd);
      } else if (this.activeTab === 'keynumbers') {
        renderKeyNumbersTab(cd);
      } else if (this.activeTab === 'technical') {
        fetch(`/api/chart/${encodeURIComponent(this.selectedTicker)}?period=${this.techPeriod}`)
          .then(r => r.json())
          .then(data => {
            renderTechChart(data, this.selectedTicker);
            renderTechIndicators(data);
            renderPerfRow(data);
          });
      }
    },

    async setChartPeriod(period) {
      this.chartPeriod = period;
      if (!this.selectedTicker) return;
      try {
        const res = await fetch(`/api/chart/${encodeURIComponent(this.selectedTicker)}?period=${period}`);
        this._chartData = await res.json();
        initPriceChart('price-chart');
        updatePriceChart(this._chartData);
      } catch (e) { console.error(e); }
    },

    async setTechPeriod(period) {
      this.techPeriod = period;
      if (!this.selectedTicker) return;
      try {
        const res = await fetch(`/api/chart/${encodeURIComponent(this.selectedTicker)}?period=${period}`);
        const data = await res.json();
        renderTechChart(data, this.selectedTicker);
        renderTechIndicators(data);
        renderPerfRow(data);
      } catch (e) { console.error(e); }
    },

    closeDetail() {
      destroyPriceChart();
      destroyTechChart();
      this.selectedTicker = null;
      this.companyData = null;
      this._chartData = null;
    },

    startResize(e) {
      e.preventDefault();
      const self = this;
      document.body.classList.add('resizing');

      function onMove(ev) {
        const w = window.innerWidth - ev.clientX;
        self.rightPanelWidth = Math.max(400, Math.min(w, window.innerWidth - 250));
      }
      function onUp() {
        document.body.classList.remove('resizing');
        document.removeEventListener('mousemove', onMove);
        document.removeEventListener('mouseup', onUp);
      }
      document.addEventListener('mousemove', onMove);
      document.addEventListener('mouseup', onUp);
    },
  }));
});
