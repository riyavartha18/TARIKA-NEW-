import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useAuth } from '../../auth/AuthContext';
import {
  getAdminBIOverview,
  getAdminBIRevenueForecast,
  getAdminBIDemandForecast,
  getAdminBIDemandSignals,
} from '../../services/api';
import { generateInsights } from '../../utils/insights';
import '../../styles/bi-dashboard.css';
import {
  KpiCard,
  TrendBadge,
  fmtINR,
  fmtNum,
} from './bi/BIPrimitives';
import {
  RevenueForecastSection,
  DemandForecastSection,
  InventoryHealthSection,
  SalesPerformanceSection,
  InsightsPanel,
} from './bi/sections';
import {
  ShieldCheck,
  DollarSign,
  ShoppingBag,
  Package,
  Users,
  AlertTriangle,
  RefreshCw,
  AlertCircle,
  Activity,
  TrendingUp,
} from 'lucide-react';

const DATE_RANGES = [
  { days: 7, label: 'Last 7 days' },
  { days: 30, label: 'Last 30 days' },
  { days: 90, label: 'Last 90 days' },
];

export default function AdminDashboardView() {
  const { user, token } = useAuth();
  const [days, setDays] = useState(30);
  const contentRef = useRef(null);

  const [overview, setOverview] = useState(null);
  const [ovLoading, setOvLoading] = useState(true);
  const [ovError, setOvError] = useState(null);

  const [revenue, setRevenue] = useState(null);
  const [revLoading, setRevLoading] = useState(true);
  const [revError, setRevError] = useState(null);

  const [demand, setDemand] = useState(null);

  const [signals, setSignals] = useState(null);
  const [sigLoading, setSigLoading] = useState(true);
  const [sigError, setSigError] = useState(null);

  const firstName = user?.first_name?.trim();
  const lastName = user?.last_name?.trim();
  const fullName = user?.full_name?.trim() || user?.name?.trim();
  const displayName = (firstName || lastName)
    ? `${firstName || ''} ${lastName || ''}`.trim()
    : (fullName || 'Admin');

  const activeToken = token || localStorage.getItem('tarika_auth_token');

  const loadOverview = useCallback(async (d) => {
    setOvLoading(true);
    setOvError(null);
    const res = await getAdminBIOverview(activeToken, { days: d });
    if (res.success) setOverview(res.data);
    else setOvError(res.error);
    setOvLoading(false);
  }, [activeToken]);

  const loadRevenue = useCallback(async () => {
    setRevLoading(true);
    setRevError(null);
    const res = await getAdminBIRevenueForecast(activeToken, { horizon: 3 });
    if (res.success) setRevenue(res.data);
    else setRevError(res.error);
    setRevLoading(false);
  }, [activeToken]);

  const loadDemand = useCallback(async () => {
    // Forecast demand feeds the Smart Insights panel (kept separate from the
    // live demand-signal cards shown in the Demand Forecasting section).
    const res = await getAdminBIDemandForecast(activeToken);
    if (res.success) setDemand(res.data);
  }, [activeToken]);

  const loadSignals = useCallback(async () => {
    setSigLoading(true);
    setSigError(null);
    const res = await getAdminBIDemandSignals(activeToken, { months: 3 });
    if (res.success) setSignals(res.data);
    else setSigError(res.error);
    setSigLoading(false);
  }, [activeToken]);

  // Overview is re-fetched whenever the date range changes.
  useEffect(() => { loadOverview(days); }, [days, loadOverview]);
  // Forecast / demand load once per session.
  useEffect(() => {
    loadRevenue();
    loadDemand();
    loadSignals();
  }, [loadRevenue, loadDemand, loadSignals]);

  const refreshAll = () => {
    loadOverview(days);
    loadRevenue();
    loadDemand();
    loadSignals();
  };

  const handleNavigate = (sectionId) => {
    if (!sectionId) return;
    const el = document.getElementById(sectionId);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  const kpis = overview?.kpis || {};
  const inventory = overview?.inventory_health || {};
  const insights = generateInsights({
    overview,
    revenueForecast: revenue,
    demandForecast: demand,
  });

  return (
    <div ref={contentRef}>
      {/* Executive hero + controls */}
      <div className="admin-dashboard-hero">
        <ShieldCheck size={160} className="admin-dashboard-hero-bg" />
        <div className="bi-hero-row">
          <div>
            <span className="admin-hero-badge"><Activity size={13} /> Business Intelligence</span>
            <h1 className="admin-hero-title">Welcome, {displayName}</h1>
            <p className="admin-hero-desc">
              A single view of performance, forecasts, inventory health and actionable insights for TARIKA Retail.
            </p>
          </div>
          <div className="bi-hero-controls">
            <div className="bi-range-group" role="group" aria-label="Date range">
              {DATE_RANGES.map((r) => (
                <button
                  key={r.days}
                  className={`bi-range-btn ${days === r.days ? 'active' : ''}`}
                  onClick={() => setDays(r.days)}
                >
                  {r.label}
                </button>
              ))}
            </div>
            <button className="bi-refresh-btn" onClick={refreshAll} title="Refresh dashboard">
              <RefreshCw size={15} />
            </button>
          </div>
        </div>
      </div>

      {/* KPI cards */}
      {ovError && !overview ? (
        <div className="admin-card" style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <AlertCircle size={26} color="#DC2626" />
          <p style={{ color: '#6B5E63', margin: '0.6rem 0 1rem' }}>{ovError}</p>
          <button className="tarika-btn-primary" onClick={() => loadOverview(days)} style={{ margin: '0 auto' }}>
            <RefreshCw size={14} /> Retry
          </button>
        </div>
      ) : (
        <div className="bi-kpi-grid">
          <KpiCard
            icon={DollarSign}
            title="Total Revenue"
            value={fmtINR(kpis.total_revenue)}
            sub={`Previous period: ${fmtINR(kpis.previous_revenue)}`}
            delta={<TrendBadge pct={kpis.revenue_growth_pct} />}
            accent="#B8505E"
          />
          <KpiCard
            icon={ShoppingBag}
            title="Total Orders"
            value={fmtNum(kpis.total_orders)}
            sub={`Previous period: ${fmtNum(kpis.previous_orders)}`}
            delta={<TrendBadge pct={kpis.orders_growth_pct} />}
            accent="#2563EB"
          />
          <KpiCard
            icon={TrendingUp}
            title="Revenue Growth"
            value={kpis.revenue_growth_pct != null ? `${kpis.revenue_growth_pct > 0 ? '+' : ''}${kpis.revenue_growth_pct}%` : 'n/a'}
            sub={kpis.revenue_growth_pct != null ? 'vs previous period' : 'Insufficient comparable history'}
            delta={<TrendBadge pct={kpis.revenue_growth_pct} suffix="" />}
            accent="#059669"
          />
          <KpiCard
            icon={Package}
            title="Total Products"
            value={fmtNum(kpis.total_products)}
            sub="Active catalog"
            accent="#8E3642"
          />
          <KpiCard
            icon={Users}
            title="Total Customers"
            value={fmtNum(kpis.total_customers)}
            sub={`${fmtNum(kpis.new_customers)} new this period`}
            delta={<TrendBadge pct={kpis.customers_growth_pct} />}
            accent="#7C3AED"
          />
          <KpiCard
            icon={AlertTriangle}
            title="Low Stock Alerts"
            value={fmtNum(kpis.low_stock_count)}
            sub="Products at or below reorder level"
            accent="#DC2626"
          />
        </div>
      )}

      {/* Forecasting charts (middle band) */}
      <div className="bi-grid-2">
        <RevenueForecastSection loading={revLoading} error={revError} onRetry={loadRevenue} data={revenue} />
        <InsightsPanel insights={insights} onNavigate={handleNavigate} />
      </div>

      {/* Demand forecasting (live signals) */}
      <DemandForecastSection loading={sigLoading} error={sigError} onRetry={loadSignals} data={signals} />

      {/* Inventory health + Sales performance */}
      <SalesPerformanceSection
        loading={ovLoading}
        error={ovError}
        onRetry={() => loadOverview(days)}
        data={overview?.sales_performance}
      />

      {/* Inventory health */}
      <InventoryHealthSection
        loading={ovLoading}
        error={ovError}
        onRetry={() => loadOverview(days)}
        data={inventory}
      />
    </div>
  );
}
