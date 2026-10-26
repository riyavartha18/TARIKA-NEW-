import React, { useState, useMemo, useRef } from 'react';

/* ==========================================================================
   TARIKA ADMIN BI — DEPENDENCY-FREE SVG CHARTS
   Lightweight, responsive chart primitives (no charting library added to the
   project). Every chart scales to its container via viewBox and includes
   legends, tooltips and readable axis labels.
   ========================================================================== */

export const CHART_COLORS = {
  actual: '#B8505E',
  forecast: '#7C3AED',
  positive: '#059669',
  warning: '#D97706',
  critical: '#DC2626',
  info: '#2563EB',
  grid: 'rgba(216, 114, 126, 0.15)',
  axis: '#9E8F94',
};

const DONUT_PALETTE = ['#B8505E', '#D8727E', '#8E3642', '#2563EB', '#059669', '#D97706', '#7C3AED', '#9E8F94'];

const fmtCompact = (val) => {
  const n = Number(val || 0);
  if (Math.abs(n) >= 1e7) return `${(n / 1e7).toFixed(2)}Cr`;
  if (Math.abs(n) >= 1e5) return `${(n / 1e5).toFixed(2)}L`;
  if (Math.abs(n) >= 1e3) return `${(n / 1e3).toFixed(1)}k`;
  return `${Math.round(n)}`;
};

/* --------------------------------------------------------------------------
   Line / Area chart with actual + forecast series (forecast drawn dashed).
   data: [{ label, actual, forecast }]  — forecast may be null on actual points
   -------------------------------------------------------------------------- */
export function LineAreaChart({
  data = [],
  height = 280,
  formatValue = (v) => `₹${fmtCompact(v)}`,
  showLegend = true,
}) {
  const [hoverIndex, setHoverIndex] = useState(null);
  const svgRef = useRef(null);

  const { points, ticks, minVal, maxVal } = useMemo(() => {
    const values = [];
    data.forEach((d) => {
      if (d.actual != null) values.push(Number(d.actual));
      if (d.forecast != null) values.push(Number(d.forecast));
    });
    const rawMin = values.length ? Math.min(...values) : 0;
    const rawMax = values.length ? Math.max(...values) : 1;
    // Anchor area baseline at 0 for honest proportions.
    const minVal = 0;
    const maxVal = rawMax === rawMin ? rawMax + 1 : rawMax;
    const ticks = [0, 0.25, 0.5, 0.75, 1].map((t) => minVal + (maxVal - minVal) * t);
    const points = data.map((d, i) => ({ ...d, i }));
    return { points, ticks, minVal, maxVal };
  }, [data]);

  const W = 640;
  const H = height;
  const padL = 52;
  const padR = 18;
  const padT = 18;
  const padB = 34;
  const innerW = W - padL - padR;
  const innerH = H - padT - padB;

  const xFor = (i) => (points.length <= 1 ? padL + innerW / 2 : padL + (innerW * i) / (points.length - 1));
  const yFor = (v) => padT + innerH - ((Number(v) - minVal) / (maxVal - minVal)) * innerH;

  const buildPath = (getKey, connectFn) => {
    let path = '';
    let started = false;
    points.forEach((p, i) => {
      const raw = connectFn ? connectFn(p, i) : p[getKey];
      if (raw == null) return;
      const cmd = started ? 'L' : 'M';
      path += `${cmd}${xFor(i).toFixed(1)},${yFor(raw).toFixed(1)} `;
      started = true;
    });
    return path.trim();
  };

  // Actual line: solid up to the last actual point.
  const actualPath = buildPath('actual');
  // Forecast line: starts at the last actual point so the two meet seamlessly.
  const lastActualIndex = points.reduce((acc, p, i) => (p.actual != null ? i : acc), -1);
  const forecastPath = (() => {
    let path = '';
    let started = false;
    if (lastActualIndex >= 0) {
      path = `M${xFor(lastActualIndex).toFixed(1)},${yFor(points[lastActualIndex].actual).toFixed(1)} `;
      started = true;
    }
    points.forEach((p, i) => {
      if (p.forecast == null) return;
      const cmd = started ? 'L' : 'M';
      path += `${cmd}${xFor(i).toFixed(1)},${yFor(p.forecast).toFixed(1)} `;
      started = true;
    });
    return path.trim();
  })();

  const areaPath = (() => {
    if (!actualPath || lastActualIndex < 0) return '';
    const firstX = xFor(0);
    const lastX = xFor(lastActualIndex);
    const baseY = yFor(minVal);
    return `${actualPath} L${lastX.toFixed(1)},${baseY.toFixed(1)} L${firstX.toFixed(1)},${baseY.toFixed(1)} Z`;
  })();

  const handleMove = (evt) => {
    if (!svgRef.current || points.length === 0) return;
    const rect = svgRef.current.getBoundingClientRect();
    const relX = ((evt.clientX - rect.left) / rect.width) * W;
    let idx = Math.round(((relX - padL) / innerW) * (points.length - 1));
    idx = Math.max(0, Math.min(points.length - 1, idx));
    setHoverIndex(idx);
  };

  const hovered = hoverIndex != null ? points[hoverIndex] : null;

  return (
    <div className="bi-chart">
      {showLegend && (
        <div className="bi-chart-legend">
          <span className="bi-legend-item"><i style={{ background: CHART_COLORS.actual }} /> Actual</span>
          <span className="bi-legend-item"><i className="bi-legend-dashed" style={{ borderColor: CHART_COLORS.forecast }} /> Forecast</span>
        </div>
      )}
      <div className="bi-linechart-wrap" style={{ position: 'relative' }}>
        <svg
          ref={svgRef}
          viewBox={`0 0 ${W} ${H}`}
          preserveAspectRatio="none"
          className="bi-linechart-svg"
          width="100%"
          height={H}
          onMouseMove={handleMove}
          onMouseLeave={() => setHoverIndex(null)}
        >
          <defs>
            <linearGradient id="biAreaGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={CHART_COLORS.actual} stopOpacity="0.28" />
              <stop offset="100%" stopColor={CHART_COLORS.actual} stopOpacity="0.02" />
            </linearGradient>
          </defs>

          {/* Horizontal grid + Y axis labels */}
          {ticks.map((t, i) => {
            const y = yFor(t);
            return (
              <g key={i}>
                <line x1={padL} y1={y} x2={W - padR} y2={y} stroke={CHART_COLORS.grid} strokeWidth="1" />
                <text x={padL - 8} y={y + 3} textAnchor="end" className="bi-axis-text">{fmtCompact(t)}</text>
              </g>
            );
          })}

          {areaPath && <path d={areaPath} fill="url(#biAreaGrad)" />}
          {actualPath && <path d={actualPath} fill="none" stroke={CHART_COLORS.actual} strokeWidth="2.5" strokeLinejoin="round" strokeLinecap="round" />}
          {forecastPath && <path d={forecastPath} fill="none" stroke={CHART_COLORS.forecast} strokeWidth="2.5" strokeDasharray="6 5" strokeLinejoin="round" strokeLinecap="round" />}

          {/* Hover guide + dots */}
          {hovered && (
            <g>
              <line x1={xFor(hovered.i)} y1={padT} x2={xFor(hovered.i)} y2={H - padB} stroke={CHART_COLORS.axis} strokeWidth="1" strokeDasharray="3 3" />
              {hovered.actual != null && <circle cx={xFor(hovered.i)} cy={yFor(hovered.actual)} r="4" fill={CHART_COLORS.actual} />}
              {hovered.forecast != null && <circle cx={xFor(hovered.i)} cy={yFor(hovered.forecast)} r="4" fill={CHART_COLORS.forecast} />}
            </g>
          )}

          {/* X axis labels (thin out when crowded) */}
          {points.map((p) => {
            const step = Math.ceil(points.length / 8);
            if (p.i % step !== 0 && p.i !== points.length - 1) return null;
            return (
              <text key={`x${p.i}`} x={xFor(p.i)} y={H - 12} textAnchor="middle" className="bi-axis-text">{p.label}</text>
            );
          })}
        </svg>

        {hovered && (
          <div
            className="bi-tooltip"
            style={{
              left: `${(xFor(hovered.i) / W) * 100}%`,
              top: 8,
            }}
          >
            <div className="bi-tooltip-title">{hovered.label}</div>
            {hovered.actual != null && (
              <div className="bi-tooltip-row"><i style={{ background: CHART_COLORS.actual }} /> Actual: {formatValue(hovered.actual)}</div>
            )}
            {hovered.forecast != null && (
              <div className="bi-tooltip-row"><i style={{ background: CHART_COLORS.forecast }} /> Forecast: {formatValue(hovered.forecast)}</div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

/* --------------------------------------------------------------------------
   Donut chart. data: [{ label, value, color? }]
   -------------------------------------------------------------------------- */
export function DonutChart({ data = [], size = 180, thickness = 26, centerLabel, centerValue, formatValue = (v) => fmtCompact(v) }) {
  const [hoverIndex, setHoverIndex] = useState(null);
  const total = data.reduce((s, d) => s + Number(d.value || 0), 0);
  const radius = (size - thickness) / 2;
  const circ = 2 * Math.PI * radius;
  let offset = 0;

  return (
    <div className="bi-donut-wrap">
      <svg viewBox={`0 0 ${size} ${size}`} width={size} height={size} className="bi-donut-svg">
        <g transform={`rotate(-90 ${size / 2} ${size / 2})`}>
          <circle cx={size / 2} cy={size / 2} r={radius} fill="none" stroke={CHART_COLORS.grid} strokeWidth={thickness} />
          {total > 0 && data.map((d, i) => {
            const frac = Number(d.value || 0) / total;
            const len = frac * circ;
            const color = d.color || DONUT_PALETTE[i % DONUT_PALETTE.length];
            const seg = (
              <circle
                key={i}
                cx={size / 2}
                cy={size / 2}
                r={radius}
                fill="none"
                stroke={color}
                strokeWidth={hoverIndex === i ? thickness + 4 : thickness}
                strokeDasharray={`${len} ${circ - len}`}
                strokeDashoffset={-offset}
                onMouseEnter={() => setHoverIndex(i)}
                onMouseLeave={() => setHoverIndex(null)}
                style={{ transition: 'stroke-width 0.15s ease', cursor: 'pointer' }}
              />
            );
            offset += len;
            return seg;
          })}
        </g>
        <text x={size / 2} y={size / 2 - 4} textAnchor="middle" className="bi-donut-center-value">
          {hoverIndex != null ? formatValue(data[hoverIndex].value) : (centerValue ?? total)}
        </text>
        <text x={size / 2} y={size / 2 + 14} textAnchor="middle" className="bi-donut-center-label">
          {hoverIndex != null ? data[hoverIndex].label : (centerLabel ?? 'Total')}
        </text>
      </svg>
      <div className="bi-donut-legend">
        {data.map((d, i) => (
          <div
            key={i}
            className="bi-legend-row"
            onMouseEnter={() => setHoverIndex(i)}
            onMouseLeave={() => setHoverIndex(null)}
          >
            <span className="bi-legend-dot" style={{ background: d.color || DONUT_PALETTE[i % DONUT_PALETTE.length] }} />
            <span className="bi-legend-label">{d.label}</span>
            <span className="bi-legend-value">{d.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

/* --------------------------------------------------------------------------
   Horizontal bar list. data: [{ label, value, image?, sub? }]
   -------------------------------------------------------------------------- */
export function BarList({ data = [], formatValue = (v) => fmtCompact(v), color = CHART_COLORS.actual, emptyText = 'No data available' }) {
  const max = Math.max(...data.map((d) => Number(d.value || 0)), 1);
  if (!data.length) return <p className="bi-empty-note">{emptyText}</p>;
  return (
    <div className="bi-barlist">
      {data.map((d, i) => (
        <div key={i} className="bi-barlist-row">
          {d.image ? (
            <img className="bi-barlist-img" src={d.image} alt="" onError={(e) => { e.currentTarget.style.visibility = 'hidden'; }} />
          ) : (
            <span className="bi-barlist-rank">{i + 1}</span>
          )}
          <div className="bi-barlist-body">
            <div className="bi-barlist-top">
              <span className="bi-barlist-label" title={d.label}>{d.label}</span>
              <span className="bi-barlist-value">{formatValue(d.value)}</span>
            </div>
            <div className="bi-barlist-track">
              <div className="bi-barlist-fill" style={{ width: `${(Number(d.value || 0) / max) * 100}%`, background: d.color || color }} />
            </div>
            {d.sub && <span className="bi-barlist-sub">{d.sub}</span>}
          </div>
        </div>
      ))}
    </div>
  );
}

export { fmtCompact };
