import React, { useState, useMemo } from 'react';
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
  KpiCard,
  fmtINR,
  fmtNum,
} from './BIPrimitives';
import {
  Sparkles,
  TrendingUp,
  ArrowRight,
  AlertTriangle,
  CheckCircle2,
  Info,
  CalendarClock,
  Boxes,
  Heart,
  BellRing,
  ShoppingCart,
  Activity,
  Search,
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
   2. DEMAND FORECASTING
   ========================================================================== */
/* --- sortable table header + id helpers ----------------------------------- */
const shortId = (id = '') => (id.length > 8 ? `${id.slice(0, 8)}…` : id);

function SortableTh({ label, col, sortKey, sortDir, onSort, numeric = false }) {
  const active = sortKey === col;
  return (
    <th
      className={`bi-th-sort ${active ? 'active' : ''}`}
      onClick={() => onSort(col)}
      title={`Sort by ${label}`}
    >
      <span>{label}</span>
      <span className="bi-sort-arrow">{active ? (sortDir === 'asc' ? '▲' : '▼') : (numeric ? '' : '')}</span>
    </th>
  );
}

export function DemandForecastSection({ loading, error, onRetry, data }) {
  const [search, setSearch] = useState('');
  const [sortKey, setSortKey] = useState('total_signals');
  const [sortDir, setSortDir] = useState('desc');

  const totals = data?.totals || {};

  const products = useMemo(() => {
    const rows = (data?.products || []).slice();
    const q = search.trim().toLowerCase();
    const filtered = q
      ? rows.filter((p) =>
          (p.product_name || '').toLowerCase().includes(q) ||
          (p.product_id || '').toLowerCase().includes(q))
      : rows;
    filtered.sort((a, b) => {
      const av = a[sortKey];
      const bv = b[sortKey];
      let cmp;
      if (typeof av === 'string') cmp = av.localeCompare(bv);
      else cmp = (Number(av) || 0) - (Number(bv) || 0);
      return sortDir === 'asc' ? cmp : -cmp;
    });
    return filtered;
  }, [data, search, sortKey, sortDir]);

  const toggleSort = (col) => {
    if (col === sortKey) {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortKey(col);
      setSortDir(col === 'product_name' ? 'asc' : 'desc');
    }
  };

  const statusTone = (s) => (
    s === 'High Interest' ? 'positive'
      : s === 'Moderate Interest' ? 'info'
        : s === 'Low Interest' ? 'warning' : 'neutral'
  );

  return (
    <SectionCard
      id="demand-forecast"
      icon={Boxes}
      title="Demand Forecasting"
      subtitle="Live customer-interest signals from fact_demand"
      actions={data && !data.insufficient_data && data.window && (
        <span className="bi-note-chip">{data.window.description}</span>
      )}
    >
      {loading && <SectionSpinner label="Loading live demand signals…" />}
      {!loading && error && <SectionError label={error} onRetry={onRetry} />}
      {!loading && data && data.insufficient_data && (
        <div className="bi-insufficient">
          <CalendarClock size={18} />
          <div>
            <strong>Live demand signals unavailable</strong>
            <p>{data.message}</p>
          </div>
        </div>
      )}
      {!loading && data && !data.insufficient_data && (
        <>
          <div className="bi-signal-cards">
            <KpiCard icon={Heart} title="Wishlist Count" value={fmtNum(totals.wishlist)} accent="#B8505E" />
            <KpiCard icon={BellRing} title="Notify Me Count" value={fmtNum(totals.notify_me)} accent="#7C3AED" />
            <KpiCard icon={ShoppingCart} title="Add to Cart Count" value={fmtNum(totals.add_to_cart)} accent="#2563EB" />
            <KpiCard
              icon={Activity}
              title="Total Demand Signals"
              value={fmtNum(totals.total_signals)}
              sub={`${fmtNum(totals.products)} products`}
              accent="#059669"
            />
          </div>

          {data.metric_definition && <p className="bi-footnote">{data.metric_definition}</p>}

          <div className="bi-table-controls">
            <div className="bi-search">
              <Search size={15} />
              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search product name or ID…"
              />
            </div>
            <span className="bi-count">Showing {Math.min(products.length, 60)} of {products.length}</span>
          </div>

          {products.length === 0 ? (
            <SectionEmpty label="No products match your search." />
          ) : (
            <div className="admin-table-wrapper">
              <table className="admin-table bi-table bi-sortable">
                <thead>
                  <tr>
                    <SortableTh label="Product" col="product_name" sortKey={sortKey} sortDir={sortDir} onSort={toggleSort} />
                    <th>Product ID</th>
                    <SortableTh label="Wishlist" col="wishlist" numeric sortKey={sortKey} sortDir={sortDir} onSort={toggleSort} />
                    <SortableTh label="Notify Me" col="notify_me" numeric sortKey={sortKey} sortDir={sortDir} onSort={toggleSort} />
                    <SortableTh label="Add to Cart" col="add_to_cart" numeric sortKey={sortKey} sortDir={sortDir} onSort={toggleSort} />
                    <SortableTh label="Total Signals" col="total_signals" numeric sortKey={sortKey} sortDir={sortDir} onSort={toggleSort} />
                    <th>Demand Status</th>
                  </tr>
                </thead>
                <tbody>
                  {products.slice(0, 60).map((p) => (
                    <tr key={p.product_id}>
                      <td>
                        <div className="bi-cell-name">{p.product_name}</div>
                        <div className="bi-cell-cat">{p.category_name}</div>
                      </td>
                      <td className="bi-cell-mono bi-cell-dim" title={p.product_id}>{shortId(p.product_id)}</td>
                      <td>{p.wishlist}</td>
                      <td>{p.notify_me}</td>
                      <td>{p.add_to_cart}</td>
                      <td className="bi-cell-strong">{p.total_signals}</td>
                      <td><StatusPill tone={statusTone(p.demand_status)}>{p.demand_status}</StatusPill></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {data.demand_status_rule && <p className="bi-footnote">{data.demand_status_rule}</p>}
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
