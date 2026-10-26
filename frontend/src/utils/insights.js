/* ==========================================================================
   Smart Business Insights — derived ENTIRELY from real dashboard payloads.
   Every insight carries: severity, title, reason, action and a target section
   id the dashboard can scroll to. Nothing here is a canned message: entries
   are only emitted when the underlying data actually supports them.
   ========================================================================== */

const inr = (n) => `₹${Math.round(Number(n) || 0).toLocaleString('en-IN')}`;

export function generateInsights({ overview, revenueForecast, demandForecast, slowMoving }) {
  const insights = [];
  const kpis = overview?.kpis || {};

  // 1. Revenue movement vs previous period.
  if (kpis.revenue_growth_pct != null) {
    if (kpis.revenue_growth_pct <= -5) {
      insights.push({
        severity: 'critical',
        title: `Revenue down ${Math.abs(kpis.revenue_growth_pct)}% vs previous period`,
        reason: `Confirmed revenue fell from ${inr(kpis.previous_revenue)} to ${inr(kpis.total_revenue)}.`,
        action: 'Review pricing, promotions and top-category performance.',
        target: 'revenue-forecast',
      });
    } else if (kpis.revenue_growth_pct >= 5) {
      insights.push({
        severity: 'positive',
        title: `Revenue up ${kpis.revenue_growth_pct}% vs previous period`,
        reason: `Revenue grew from ${inr(kpis.previous_revenue)} to ${inr(kpis.total_revenue)}.`,
        action: 'Sustain momentum on best-selling products.',
        target: 'sales-performance',
      });
    }
  }

  // 2. Products at risk of running out (low stock + short cover).
  const runOut = (overview?.inventory_health?.low_stock || []).filter(
    (r) => r.days_of_stock != null && r.days_of_stock <= 14,
  );
  if (runOut.length) {
    insights.push({
      severity: 'warning',
      title: `${runOut.length} product${runOut.length > 1 ? 's may' : ' may'} run out of stock soon`,
      reason: `Top risk: ${runOut[0].product_name} (${runOut[0].stock} left, ~${runOut[0].days_of_stock} days of cover).`,
      action: 'Trigger restock for the fastest-depleting items.',
      target: 'inventory-health',
    });
  }

  // 3. Overstock / high stock but low sales.
  const stagnant = slowMoving?.summary?.stagnant_count || 0;
  const tiedUp = slowMoving?.summary?.stagnant_inventory_value || 0;
  if (stagnant > 0) {
    insights.push({
      severity: 'warning',
      title: `${stagnant} product line${stagnant > 1 ? 's have' : ' has'} high stock but low sales`,
      reason: `${inr(tiedUp)} of inventory value is tied up in slow-moving, overstocked or non-moving items.`,
      action: 'Consider promotions, markdowns or reduced future purchases.',
      target: 'slow-moving',
    });
  }

  // 4. Non-moving inventory.
  const nonMoving = slowMoving?.summary?.non_moving || 0;
  if (nonMoving > 0) {
    insights.push({
      severity: 'critical',
      title: `${nonMoving} non-moving product line${nonMoving > 1 ? 's' : ''}`,
      reason: 'No units sold in the analysis window for these items.',
      action: 'Clear via discount, bundle or supplier return.',
      target: 'slow-moving',
    });
  }

  // 5. Rising demand forecast for specific products.
  const highDemand = demandForecast?.high_demand_products || [];
  if (highDemand.length) {
    const top = highDemand[0];
    insights.push({
      severity: 'positive',
      title: `Demand is increasing for ${top.product_name}`,
      reason: `Forecast projects ${top.predicted_units_next_month} units next month (High demand).`,
      action: 'Ensure sufficient stock and plan merchandising.',
      target: 'demand-forecast',
    });
  }

  // 6. Restock needed to meet forecast demand.
  const restockCount = demandForecast?.summary?.restock_count || 0;
  if (restockCount > 0) {
    const top = (demandForecast?.restock_recommendations || [])[0];
    insights.push({
      severity: 'warning',
      title: `${restockCount} product${restockCount > 1 ? 's need' : ' needs'} restocking`,
      reason: top ? `${top.product_name} is projected ${top.need_to_order} units short of forecast demand.` : 'Forecast demand exceeds current stock.',
      action: 'Raise purchase orders for recommended quantities.',
      target: 'demand-forecast',
    });
  }

  // 7. Forward revenue expectation.
  const rf = revenueForecast?.forecast;
  if (rf && rf.expected_growth_pct != null && !revenueForecast?.insufficient_data) {
    if (rf.expected_growth_pct >= 3) {
      insights.push({
        severity: 'positive',
        title: `Revenue forecast shows ~${rf.expected_growth_pct}% growth next month`,
        reason: 'The regression model projects revenue above the latest actual month.',
        action: 'Plan inventory and staffing to meet expected growth.',
        target: 'revenue-forecast',
      });
    } else if (rf.expected_growth_pct <= -3) {
      insights.push({
        severity: 'warning',
        title: `Revenue forecast projects a ~${Math.abs(rf.expected_growth_pct)}% decline next month`,
        reason: 'The regression model projects revenue below the latest actual month.',
        action: 'Investigate demand softness and plan corrective campaigns.',
        target: 'revenue-forecast',
      });
    }
  }

  // 8. Best performing category.
  const topCat = (overview?.sales_performance?.top_categories || [])[0];
  if (topCat && topCat.revenue > 0) {
    insights.push({
      severity: 'info',
      title: `${topCat.category_name} is the best-performing category`,
      reason: `It contributed ${inr(topCat.revenue)} of revenue in the selected period.`,
      action: 'Deepen assortment and visibility in this category.',
      target: 'sales-performance',
    });
  }

  // 9. Out of stock.
  const outOfStock = overview?.inventory_health?.counts?.out_of_stock || 0;
  if (outOfStock > 0) {
    insights.push({
      severity: 'critical',
      title: `${outOfStock} product${outOfStock > 1 ? 's are' : ' is'} out of stock`,
      reason: 'These active products currently have no sellable inventory.',
      action: 'Prioritise replenishment to avoid lost sales.',
      target: 'inventory-health',
    });
  }

  const order = { critical: 0, warning: 1, positive: 2, info: 3 };
  insights.sort((a, b) => (order[a.severity] ?? 9) - (order[b.severity] ?? 9));
  return insights.slice(0, 8);
}
