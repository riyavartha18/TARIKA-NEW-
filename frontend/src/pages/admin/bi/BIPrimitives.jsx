import React from 'react';
import { TrendingUp, TrendingDown, Minus, RefreshCw, AlertCircle } from 'lucide-react';

/* -------------------------------------------------------------------------- */
/* Formatters                                                                 */
/* -------------------------------------------------------------------------- */
export const fmtINR = (v) => `₹${Math.round(Number(v) || 0).toLocaleString('en-IN')}`;
export const fmtNum = (v) => `${Math.round(Number(v) || 0).toLocaleString('en-IN')}`;

/* -------------------------------------------------------------------------- */
/* Trend badge — subtle status colour for positive / warning / critical       */
/* -------------------------------------------------------------------------- */
export function TrendBadge({ pct, positiveIsGood = true, suffix = 'vs prev.' }) {
  if (pct == null || Number.isNaN(pct)) {
    return (
      <span className="bi-trend bi-trend-flat" title="Not enough comparable history">
        <Minus size={13} /> <span>n/a</span>
      </span>
    );
  }
  const up = pct > 0;
  const flat = pct === 0;
  const good = positiveIsGood ? up : !up;
  const tone = flat ? 'flat' : good ? 'positive' : 'negative';
  const Icon = flat ? Minus : up ? TrendingUp : TrendingDown;
  return (
    <span className={`bi-trend bi-trend-${tone}`}>
      <Icon size={13} />
      <span>{`${up ? '+' : ''}${pct}%`}</span>
      {suffix && <span className="bi-trend-suffix">{suffix}</span>}
    </span>
  );
}

/* -------------------------------------------------------------------------- */
/* KPI card                                                                    */
/* -------------------------------------------------------------------------- */
export function KpiCard({ icon: Icon, title, value, sub, delta, accent = '#B8505E' }) {
  return (
    <div className="bi-kpi-card">
      <div className="bi-kpi-top">
        <div className="bi-kpi-icon" style={{ background: `${accent}14`, color: accent }}>
          {Icon && <Icon size={20} />}
        </div>
        {delta}
      </div>
      <p className="bi-kpi-title">{title}</p>
      <p className="bi-kpi-value">{value}</p>
      {sub && <p className="bi-kpi-sub">{sub}</p>}
    </div>
  );
}

/* -------------------------------------------------------------------------- */
/* Section card container                                                     */
/* -------------------------------------------------------------------------- */
export function SectionCard({ id, icon: Icon, title, subtitle, actions, children, className = '' }) {
  return (
    <section id={id} className={`bi-section-card ${className}`}>
      <div className="bi-section-head">
        <div className="bi-section-title-group">
          {Icon && <span className="bi-section-icon"><Icon size={18} /></span>}
          <div>
            <h3 className="bi-section-title">{title}</h3>
            {subtitle && <p className="bi-section-subtitle">{subtitle}</p>}
          </div>
        </div>
        {actions && <div className="bi-section-actions">{actions}</div>}
      </div>
      <div className="bi-section-body">{children}</div>
    </section>
  );
}

/* -------------------------------------------------------------------------- */
/* Status pill                                                                */
/* -------------------------------------------------------------------------- */
const TONE_MAP = {
  positive: { bg: '#ECFDF5', fg: '#047857', border: '#A7F3D0' },
  warning: { bg: '#FFFBEB', fg: '#B45309', border: '#FDE68A' },
  critical: { bg: '#FEF2F2', fg: '#B91C1C', border: '#FECACA' },
  info: { bg: '#EFF6FF', fg: '#1D4ED8', border: '#BFDBFE' },
  neutral: { bg: '#FAF7F5', fg: '#6B5E63', border: 'rgba(216,114,126,0.2)' },
};
export function StatusPill({ tone = 'neutral', children }) {
  const t = TONE_MAP[tone] || TONE_MAP.neutral;
  return (
    <span className="bi-status-pill" style={{ background: t.bg, color: t.fg, borderColor: t.border }}>
      {children}
    </span>
  );
}

/* -------------------------------------------------------------------------- */
/* Loading / empty / error states                                             */
/* -------------------------------------------------------------------------- */
export function SectionSpinner({ label = 'Loading…' }) {
  return (
    <div className="bi-state-block">
      <div className="tarika-auth-spinner bi-spinner" />
      <span>{label}</span>
    </div>
  );
}

export function SectionEmpty({ label = 'No data available for the selected period.' }) {
  return <div className="bi-state-block bi-state-empty">{label}</div>;
}

export function SectionError({ label = 'Unable to load this section.', onRetry }) {
  return (
    <div className="bi-state-block bi-state-error">
      <AlertCircle size={18} />
      <span>{label}</span>
      {onRetry && (
        <button className="bi-retry-btn" onClick={onRetry}>
          <RefreshCw size={13} /> Retry
        </button>
      )}
    </div>
  );
}
