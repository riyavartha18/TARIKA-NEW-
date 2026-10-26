import React, { useState } from 'react';
import {
  LineAreaChart,
  BarList,
  DonutChart,
  CHART_COLORS,
} from '../../../components/admin-charts/BICharts';
import {
  SectionCard,
  SectionSpinner,
  SectionEmpty,
  SectionError,
  StatusPill,
  fmtINR,
  fmtNum,
} from './BIPrimitives';
import {
  Sparkles,
  TrendingUp,
  TrendingDown,
  Minus,
  ArrowRight,
  AlertTriangle,
  CheckCircle2,
  Info,
  CalendarClock,
  Boxes,
} from 'lucide-react';

/* --- shared helpers ------------------------------------------------------- */
const shortMonth = (label = '') => {
  const parts = label.split(' ');
  const mon = parts[0] ? parts[0].slice(0, 3) : label;
  const yr = parts[1] ? `'${parts[1].slice(2, 4)}` : '';
  return `${mon} ${yr}`.trim();
};

const MiniStat = ({ label, value, tone }) => (
  <div className="bi-mini-stat">
    <span className="bi-mini-stat-label">{label}</span>
    <span className="bi-mini-stat-value" style={tone ? { color: tone } : undefined}>{value}</span>
  </div>
);

/* ==========================================================================
   1. REVENUE FORECASTING
   ========================================================================== */
export function RevenueForecastSection({ loading, error, onRetry, data }) {
  return (
    <SectionCard
      id="revenue-forecast"
      icon={TrendingUp}
      title="Revenue Forecasting"
      subtitle="Historical vs predicted revenue — monthly model"
      actions={data && !data.insufficient_data && (
        <span className="bi-note-chip">Method: {data.forecast?.method}</span>
      )}
    >
      {loading && <SectionSpinner label="Building revenue forecast…" />}
      {!loading && error && <SectionError label={error} onRetry={onRetry} />}
      {!loading && data && data.insufficient_data && (
        <div className="bi-insufficient">
          <CalendarClock size={18} />
          <div>
            <strong>Not enough history to forecast reliably</strong>
            <p>{data.message}</p>
          </div>
        </div>
      )}
      {!loading && data && !data.insufficient_data && (
        <>
          <div className="bi-forecast-stats">
            <MiniStat label="Forecast · next 7 days" value={fmtINR(data.forecast?.forecast_7_days)} tone={CHART_COLORS.forecast} />
            <MiniStat label="Forecast · next 30 days" value={fmtINR(data.forecast?.forecast_30_days)} tone={CHART_COLORS.forecast} />
            <MiniStat label="Last actual month" value={fmtINR(data.last_actual_month?.revenue)} />
          </div>
          <LineAreaChart
            data={(data.series || []).map((p) => ({
              label: shortMonth(p.label),
              actual: p.type === 'actual' ? p.revenue : null,
              forecast: p.type === 'forecast' ? p.revenue : null,
            }))}
          />
          {data.note && <p className="bi-footnote">{data.note}</p>}
        </>
      )}
    </SectionCard>
  );
}

/* ==========================================================================
   2. DEMAND FORECASTING — compact overview
   (Detailed Wishlist / Add-to-Cart / Notify-Me live in Admin Analysis.)
   ========================================================================== */
export function DemandOverviewSection({ loading, error, onRetry, data, onOpenAnalysis }) {
  const trend = data?.demand_trend || {};
  const summary = data?.summary || {};

  const chartData = (trend.series || []).map((m) => ({
    label: shortMonth(m.label), actual: m.units, forecast: null,
  }));
  if (trend.predicted_next_month_units != null) {
    chartData.push({ label: 'Forecast', actual: null, forecast: trend.predicted_next_month_units });
  }

  const dirMeta = trend.direction === 'increasing'
    ? { tone: 'positive', Icon: TrendingUp, label: 'Increasing' }
    : trend.direction === 'decreasing'
      ? { tone: 'critical', Icon: TrendingDown, label: 'Decreasing' }
      : { tone: 'info', Icon: Minus, label: 'Stable' };

  const highDemand = (data?.high_demand_products || []).slice(0, 4);
  const restock = data?.restock_recommendations || [];
  const restockTotal = restock.reduce((s, p) => s + (p.need_to_order || 0), 0);
  const TrendIcon = dirMeta.Icon;

  return (
    <SectionCard
      id="demand-forecast"
      icon={Boxes}
      title="Demand Forecasting"
      subtitle={data && !data.insufficient_data ? `Snapshot · forecast month: ${data.forecast_month_label}` : 'Snapshot of expected demand'}
      actions={(
        <button className="bi-link-btn" onClick={onOpenAnalysis}>
          View Detailed Analysis <ArrowRight size={14} />
        </button>
      )}
    >
      {loading && <SectionSpinner label="Loading demand snapshot…" />}
      {!loading && error && <SectionError label={error} onRetry={onRetry} />}
      {!loading && data && data.insufficient_data && (
        <div className="bi-insufficient">
          <CalendarClock size={18} />
          <div>
            <strong>Demand forecast unavailable</strong>
            <p>{data.message}</p>
          </div>
        </div>
      )}
      {!loading && data && !data.insufficient_data && (
        <>
          <div className="bi-demand-summary">
            <div>
              <span className="bi-demand-big">{fmtNum(summary.total_predicted_units_next_month)}<span className="bi-demand-unit"> units</span></span>
              <span className="bi-demand-caption">Expected next-month demand · {data.forecast_month_label} · <strong>predicted</strong></span>
            </div>
            <div className="bi-demand-trend">
              <span className={`bi-trend-chip bi-trend-chip-${dirMeta.tone}`}>
                <TrendIcon size={15} /> Demand {dirMeta.label.toLowerCase()}
                {trend.change_pct != null && ` (${trend.change_pct > 0 ? '+' : ''}${trend.change_pct}%)`}
              </span>
              <span className="bi-demand-caption">
                {summary.high_demand_count || 0} high · {summary.low_demand_count || 0} low demand products
              </span>
            </div>
          </div>

          <div className="bi-two-col" style={{ marginTop: '1.15rem' }}>
            <div>
              <p className="bi-sub-head">Demand trend <span className="bi-tag-predicted">actual + predicted</span></p>
              {chartData.length > 1 ? (
                <LineAreaChart data={chartData} height={180} formatValue={(v) => `${fmtNum(v)} u`} />
              ) : <SectionEmpty label="Not enough demand history to chart a trend." />}
              {trend.note && <p className="bi-footnote">{trend.note}</p>}
            </div>
            <div>
              <p className="bi-sub-head">High-demand products <span className="bi-tag-predicted">predicted</span></p>
              {highDemand.length ? (
                <BarList
                  data={highDemand.map((p) => ({
                    label: p.product_name,
                    value: p.predicted_units_next_month,
                    sub: `${p.predicted_demand} · stock ${p.current_stock}`,
                  }))}
                  formatValue={(v) => `${v} u`}
                  color={CHART_COLORS.positive}
                  emptyText="No high-demand products."
                />
              ) : <SectionEmpty label="No high-demand products forecast." />}
            </div>
          </div>

          {restock.length > 0 ? (
            <div className="bi-alert bi-alert-warning">
              <AlertTriangle size={17} />
              <div>
                <strong>Stock recommendation</strong>
                <p>
                  {summary.restock_count || restock.length} high-demand product(s) may need restocking (≈ {fmtNum(restockTotal)} units). Top: {restock.slice(0, 3).map((p) => `${p.product_name} (+${p.need_to_order})`).join(', ')}.
                </p>
              </div>
            </div>
          ) : (
            <div className="bi-alert bi-alert-ok">
              <CheckCircle2 size={17} />
              <div>
                <strong>Stock levels cover forecast demand</strong>
                <p>No restocking alert for the current forecast.</p>
              </div>
            </div>
          )}
        </>
      )}
    </SectionCard>
  );
}

/* ==========================================================================
   3. INVENTORY HEALTH
   ========================================================================== */
function HealthList({ title, rows, tone, unitLabel = 'stock' }) {
  return (
    <div className="bi-health-col">
      <p className="bi-sub-head" style={{ color: tone }}>{title}</p>
      {(!rows || rows.length === 0) ? (
        <p className="bi-empty-note">None</p>
      ) : (
        <ul className="bi-health-list">
          {rows.map((r, i) => (
            <li key={`${r.product_id}-${i}`}>
              <span className="bi-health-name" title={r.product_name}>{r.product_name}</span>
              <span className="bi-health-meta">
                {r.stock} {unitLabel}
                {r.days_of_stock != null && r.days_of_stock < 999999 ? ` · ${r.days_of_stock}d cover` : ''}
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export function InventoryHealthSection({ loading, error, onRetry, data }) {
  const counts = data?.counts || {};
  return (
    <SectionCard
      id="inventory-health"
      icon={Boxes}
      title="Inventory Health"
      subtitle="Stock availability across the catalog"
    >
      {loading && <SectionSpinner label="Checking inventory health…" />}
      {!loading && error && <SectionError label={error} onRetry={onRetry} />}
      {!loading && data && (
        <>
          <div className="bi-health-top">
            <DonutChart
              data={[
                { label: 'Low Stock', value: counts.low_stock || 0, color: CHART_COLORS.warning },
                { label: 'Out of Stock', value: counts.out_of_stock || 0, color: CHART_COLORS.critical },
                { label: 'Overstocked', value: counts.overstocked || 0, color: '#C084FC' },
                { label: 'Fast Moving', value: counts.fast_moving || 0, color: CHART_COLORS.positive },
              ]}
              centerLabel="Tracked"
              centerValue={(counts.low_stock || 0) + (counts.out_of_stock || 0) + (counts.overstocked || 0) + (counts.fast_moving || 0)}
            />
            <div className="bi-health-summary">
              <StatusPill tone="warning">{counts.low_stock || 0} low stock</StatusPill>
              <StatusPill tone="critical">{counts.out_of_stock || 0} out of stock</StatusPill>
              <StatusPill tone="warning">{counts.overstocked || 0} overstocked</StatusPill>
              <StatusPill tone="positive">{counts.fast_moving || 0} fast moving</StatusPill>
            </div>
          </div>
          <div className="bi-health-grid">
            <HealthList title="Low Stock" rows={data.low_stock} tone={CHART_COLORS.warning} />
            <HealthList title="Out of Stock" rows={data.out_of_stock} tone={CHART_COLORS.critical} unitLabel="" />
            <HealthList title="Overstocked" rows={data.overstocked} tone={CHART_COLORS.warning} />
            <HealthList title="Fast Moving" rows={data.fast_moving} tone={CHART_COLORS.positive} unitLabel="sold 30d" />
          </div>
        </>
      )}
    </SectionCard>
  );
}

/* ==========================================================================
   5. SALES PERFORMANCE
   ========================================================================== */
export function SalesPerformanceSection({ loading, error, onRetry, data }) {
  const [tab, setTab] = useState('units');
  if (loading) {
    return <SectionCard id="sales-performance" icon={Sparkles} title="Sales Performance"><SectionSpinner label="Aggregating sales…" /></SectionCard>;
  }
  if (error) {
    return <SectionCard id="sales-performance" icon={Sparkles} title="Sales Performance"><SectionError label={error} onRetry={onRetry} /></SectionCard>;
  }
  const sp = data || {};
  const selling = (sp.top_selling_products || []).map((p) => ({ label: p.product_name, value: p.units_sold, image: p.image, sub: fmtINR(p.revenue) }));
  const byRevenue = (sp.top_revenue_products || []).map((p) => ({ label: p.product_name, value: p.revenue, image: p.image, sub: `${p.units_sold} units` }));
  const cats = (sp.top_categories || []).map((c) => ({ label: c.category_name, value: c.revenue }));

  return (
    <SectionCard
      id="sales-performance"
      icon={Sparkles}
      title="Sales Performance"
      subtitle="Top products and best-performing categories"
      actions={
        <div className="bi-tabs">
          <button className={tab === 'units' ? 'bi-tab active' : 'bi-tab'} onClick={() => setTab('units')}>Top Sellers</button>
          <button className={tab === 'revenue' ? 'bi-tab active' : 'bi-tab'} onClick={() => setTab('revenue')}>Top Revenue</button>
        </div>
      }
    >
      <div className="bi-grid-sales two">
        <div className="bi-col">
          <p className="bi-sub-head">{tab === 'units' ? 'Top-selling products (units)' : 'Highest-revenue products'}</p>
          <BarList
            data={tab === 'units' ? selling : byRevenue}
            formatValue={tab === 'units' ? (v) => `${v} u` : (v) => fmtINR(v)}
            emptyText="No product sales in this period."
          />
        </div>
        <div className="bi-col">
          <p className="bi-sub-head">Best-performing categories</p>
          {cats.length ? (
            <BarList data={cats} formatValue={(v) => fmtINR(v)} color={CHART_COLORS.info} emptyText="No category sales." />
          ) : <SectionEmpty label="No category sales." />}
        </div>
      </div>
    </SectionCard>
  );
}

/* ==========================================================================
   6. SMART BUSINESS INSIGHTS
   ========================================================================== */
const SEVERITY_META = {
  critical: { icon: AlertTriangle, color: CHART_COLORS.critical, tone: 'critical' },
  warning: { icon: AlertTriangle, color: CHART_COLORS.warning, tone: 'warning' },
  positive: { icon: CheckCircle2, color: CHART_COLORS.positive, tone: 'positive' },
  info: { icon: Info, color: CHART_COLORS.info, tone: 'info' },
};

export function InsightsPanel({ insights = [], onNavigate }) {
  return (
    <SectionCard
      id="insights"
      icon={Sparkles}
      title="Smart Business Insights"
      subtitle="Generated from your live data"
    >
      {insights.length === 0 ? (
        <SectionEmpty label="No significant insights right now — metrics are stable." />
      ) : (
        <div className="bi-insights">
          {insights.map((ins, i) => {
            const meta = SEVERITY_META[ins.severity] || SEVERITY_META.info;
            const Icon = meta.icon;
            return (
              <button key={i} className="bi-insight" onClick={() => onNavigate?.(ins.target)}>
                <span className="bi-insight-icon" style={{ background: `${meta.color}14`, color: meta.color }}>
                  <Icon size={16} />
                </span>
                <span className="bi-insight-body">
                  <span className="bi-insight-title">{ins.title}</span>
                  <span className="bi-insight-reason">{ins.reason}</span>
                  <span className="bi-insight-action">{ins.action}</span>
                </span>
                <span className="bi-insight-link"><ArrowRight size={15} /></span>
              </button>
            );
          })}
        </div>
      )}
    </SectionCard>
  );
}
