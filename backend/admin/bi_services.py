"""
bi_services.py
--------------
Business-Intelligence aggregation layer for the Admin dashboard.

Design rules (per product requirements):
  * Reuse the EXISTING database, warehouse (fact_demand / dim_* ), and the
    already-shipped forecasting engines. Nothing here re-implements a second
    demand model.
  * Never fabricate metrics. When a value cannot be computed from real data
    (e.g. not enough history for a reliable forecast) we return an explicit
    ``insufficient_data`` flag instead of a made-up number.
  * All period comparisons are computed on real, parsed dates from the
    operational ``orders`` / ``customers`` tables.

The data warehouse stores demand at MONTHLY granularity, so revenue/demand
forecasts are produced at month level; 7-day / 30-day figures are derived from
the monthly model and are clearly labelled as derived (``granularity`` field).
"""
from __future__ import annotations

import datetime
from collections import defaultdict
from statistics import median

from django.db import connection

from catalog.serializers import resolve_product_image
from stock_to_be_ordered.services.forecasting import run_stock_forecast
from stock_to_be_ordered.services.regression import fit_ols, predict_ols
from demand_prediction.engine import DecisionTreeEngine


# ---------------------------------------------------------------------------
# Date helpers (order_date / registration_date are stored as VARCHAR)
# ---------------------------------------------------------------------------
_DATE_FORMATS = (
    '%Y-%m-%d',
    '%Y-%m-%d %H:%M:%S',
    '%Y-%m-%dT%H:%M:%S',
    '%Y/%m/%d',
    '%d/%m/%Y',
    '%m/%d/%Y',
    '%d-%m-%Y',
)


def parse_date(value):
    """Best-effort parse of a stored date string into a ``datetime.date``."""
    if not value:
        return None
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    text = str(value).strip()
    if not text:
        return None
    # Trim trailing timezone / fractional seconds often present in ISO stamps.
    head = text[:19]
    for fmt in _DATE_FORMATS:
        try:
            return datetime.datetime.strptime(head, fmt).date()
        except ValueError:
            continue
    # Last resort: the leading YYYY-MM-DD substring.
    try:
        return datetime.datetime.strptime(text[:10], '%Y-%m-%d').date()
    except ValueError:
        return None


_CANCELLED_STATUSES = {'cancelled', 'returned', 'failed', 'refunded'}


def _is_cancelled(status):
    return str(status or '').strip().lower() in _CANCELLED_STATUSES


def _pct_change(current, previous):
    """Return rounded % change, or None when there is no comparable base."""
    if previous is None:
        return None
    if previous == 0:
        return None if current == 0 else 100.0
    return round(((current - previous) / previous) * 100, 1)


# ---------------------------------------------------------------------------
# Raw data loaders
# ---------------------------------------------------------------------------
def _load_orders():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT order_id, order_date, created_at, order_status,
                   total_amount, customer_id
            FROM orders
        """)
        rows = cursor.fetchall()

    orders = []
    for r in rows:
        d = parse_date(r[1]) or parse_date(r[2])
        orders.append({
            'order_id': str(r[0]),
            'date': d,
            'status': r[3],
            'total': float(r[4] or 0),
            'customer_id': str(r[5]) if r[5] is not None else None,
        })
    return orders


def _load_order_items():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT oi.order_id, oi.product_id,
                   COALESCE(oi.quantity, 0),
                   COALESCE(oi.subtotal, COALESCE(oi.quantity, 0) * COALESCE(oi.unit_price, 0)),
                   COALESCE(p.product_name, CONCAT('Product #', oi.product_id)),
                   COALESCE(c.category_name, 'Uncategorized')
            FROM order_items oi
            LEFT JOIN products p ON oi.product_id = p.product_id
            LEFT JOIN categories c ON p.category_id = c.category_id
        """)
        rows = cursor.fetchall()

    items = []
    for r in rows:
        items.append({
            'order_id': str(r[0]) if r[0] is not None else None,
            'product_id': str(r[1]) if r[1] is not None else None,
            'quantity': int(r[2] or 0),
            'revenue': float(r[3] or 0),
            'product_name': r[4],
            'category_name': r[5],
        })
    return items


def _load_inventory_stock():
    """Total stock per product across all warehouses."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT product_id, COALESCE(SUM(stock_quantity), 0) AS total_stock
            FROM inventory
            GROUP BY product_id
        """)
        rows = cursor.fetchall()
    return {str(r[0]): int(r[1] or 0) for r in rows}


def _load_product_master():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT p.product_id,
                   COALESCE(p.product_name, CONCAT('Product #', p.product_id)),
                   COALESCE(c.category_name, 'Uncategorized'),
                   COALESCE(p.selling_price, p.base_price, 0),
                   COALESCE(p.is_active, true)
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.category_id
        """)
        rows = cursor.fetchall()

    master = {}
    for r in rows:
        pid = str(r[0])
        master[pid] = {
            'product_id': pid,
            'product_name': r[1],
            'category_name': r[2],
            'price': float(r[3] or 0),
            'is_active': bool(r[4]),
            'image': resolve_product_image(product_id=pid, category_name=r[2]),
        }
    return master


# ---------------------------------------------------------------------------
# 1. OVERVIEW — KPIs (period comparisons), inventory health, sales performance
# ---------------------------------------------------------------------------
def build_overview(days=30):
    days = max(1, int(days or 30))
    today = datetime.date.today()
    cur_start = today - datetime.timedelta(days=days)
    prev_start = cur_start - datetime.timedelta(days=days)

    orders = _load_orders()
    order_items = _load_order_items()
    inventory = _load_inventory_stock()
    product_master = _load_product_master()

    # Orders index for item-level period filtering.
    order_date_by_id = {o['order_id']: o['date'] for o in orders}
    order_status_by_id = {o['order_id']: o['status'] for o in orders}

    def _in_window(d, start, end):
        return d is not None and start <= d <= end

    # --- Period KPIs from orders ---
    cur_rev = cur_orders = prev_rev = prev_orders = 0.0
    cur_orders = prev_orders = 0
    cur_customers = set()
    for o in orders:
        if _is_cancelled(o['status']):
            continue
        if _in_window(o['date'], cur_start, today):
            cur_rev += o['total']
            cur_orders += 1
            if o['customer_id']:
                cur_customers.add(o['customer_id'])
        elif _in_window(o['date'], prev_start, cur_start):
            prev_rev += o['total']
            prev_orders += 1

    aov = (cur_rev / cur_orders) if cur_orders else 0.0
    prev_aov = (prev_rev / prev_orders) if prev_orders else 0.0

    # --- Customers (registration-based new counts) ---
    with connection.cursor() as cursor:
        cursor.execute("SELECT customer_id, registration_date, created_at FROM customer")
        cust_rows = cursor.fetchall()
    total_customers = len(cust_rows)
    new_cur = new_prev = 0
    for cid, reg, created in cust_rows:
        d = parse_date(reg) or parse_date(created)
        if _in_window(d, cur_start, today):
            new_cur += 1
        elif _in_window(d, prev_start, cur_start):
            new_prev += 1

    # --- Product counts ---
    total_products = sum(1 for m in product_master.values() if m['is_active'])

    # --- Sales velocity (rolling 30-day window, independent of period) ---
    velocity_start = today - datetime.timedelta(days=30)
    sold_30 = defaultdict(int)
    last_sale_map = {}
    total_sold_all = defaultdict(int)
    for it in order_items:
        if _is_cancelled(order_status_by_id.get(it['order_id'], '')):
            continue
        total_sold_all[it['product_id']] += it['quantity']
        d = order_date_by_id.get(it['order_id'])
        if d is None:
            continue
        if d >= velocity_start:
            sold_30[it['product_id']] += it['quantity']
        prev_last = last_sale_map.get(it['product_id'])
        if prev_last is None or d > prev_last:
            last_sale_map[it['product_id']] = d

    def _classify(pid):
        stock = inventory.get(pid, 0)
        sold = sold_30.get(pid, 0)
        avg_daily = sold / 30.0 if sold > 0 else 0.0
        days_of_stock = round(stock / avg_daily, 1) if avg_daily > 0 else (999999 if stock > 0 else 0)
        last = last_sale_map.get(pid)
        days_since_sale = (today - last).days if last else None
        return {
            'product_id': pid,
            'product_name': product_master.get(pid, {}).get('product_name', f'Product #{pid}'),
            'category_name': product_master.get(pid, {}).get('category_name', 'Uncategorized'),
            'image': product_master.get(pid, {}).get('image'),
            'stock': stock,
            'sold_30_days': sold,
            'days_of_stock': days_of_stock,
            'days_since_last_sale': days_since_sale,
        }

    low_stock_rows = []
    out_of_stock_rows = []
    overstocked_rows = []
    fast_moving_rows = []
    for pid in product_master:
        if not product_master[pid]['is_active']:
            continue
        row = _classify(pid)
        stock = row['stock']
        sold = row['sold_30_days']
        dos = row['days_of_stock']
        if stock <= 0:
            out_of_stock_rows.append(row)
        elif stock <= 5 or dos <= 14:
            low_stock_rows.append(row)
        if sold > 0 and dos <= 30:
            fast_moving_rows.append(row)
        if stock > 0 and (sold == 0 or dos >= 180):
            overstocked_rows.append(row)

    low_stock_rows.sort(key=lambda r: r['stock'])
    out_of_stock_rows.sort(key=lambda r: r['product_name'])
    overstocked_rows.sort(key=lambda r: r['stock'], reverse=True)
    fast_moving_rows.sort(key=lambda r: r['sold_30_days'], reverse=True)

    # --- Sales performance: top products / categories within the period ---
    prod_units = defaultdict(int)
    prod_rev = defaultdict(float)
    cat_rev = defaultdict(float)
    for it in order_items:
        if _is_cancelled(order_status_by_id.get(it['order_id'], '')):
            continue
        d = order_date_by_id.get(it['order_id'])
        if not _in_window(d, cur_start, today):
            continue
        prod_units[it['product_id']] += it['quantity']
        prod_rev[it['product_id']] += it['revenue']
        cat_rev[it['category_name']] += it['revenue']

    def _product_row(pid, units, revenue):
        m = product_master.get(pid, {})
        return {
            'product_id': pid,
            'product_name': m.get('product_name') or f'Product #{pid}',
            'category_name': m.get('category_name') or 'Uncategorized',
            'image': m.get('image'),
            'units_sold': units,
            'revenue': round(revenue, 2),
        }

    top_selling = [
        _product_row(pid, u, prod_rev.get(pid, 0))
        for pid, u in sorted(prod_units.items(), key=lambda kv: kv[1], reverse=True)[:8]
    ]
    top_revenue = [
        _product_row(pid, prod_units.get(pid, 0), rev)
        for pid, rev in sorted(prod_rev.items(), key=lambda kv: kv[1], reverse=True)[:8]
    ]
    top_categories = sorted(
        ({'category_name': k, 'revenue': round(v, 2)} for k, v in cat_rev.items()),
        key=lambda c: c['revenue'], reverse=True,
    )[:6]

    # --- Daily sales trend across the selected period ---
    daily = {}
    for i in range(days):
        day = cur_start + datetime.timedelta(days=i + 1)
        daily[day.isoformat()] = {'date': day.isoformat(), 'label': day.strftime('%d %b'),
                                  'revenue': 0.0, 'orders': 0}
    for o in orders:
        if _is_cancelled(o['status']) or o['date'] is None:
            continue
        key = o['date'].isoformat()
        if key in daily:
            daily[key]['revenue'] += o['total']
            daily[key]['orders'] += 1
    daily_trend = [
        {**v, 'revenue': round(v['revenue'], 2)} for v in daily.values()
    ]

    # --- Recent orders ---
    recent = sorted(
        (o for o in orders if o['date']), key=lambda o: o['date'], reverse=True
    )[:6]
    with connection.cursor() as cursor:
        cursor.execute("SELECT customer_id, full_name, email FROM customer")
        cust_names = {str(r[0]): {'name': r[1], 'email': r[2]} for r in cursor.fetchall()}
    recent_orders = []
    for o in recent:
        c = cust_names.get(o['customer_id'] or '', {})
        recent_orders.append({
            'order_id': o['order_id'],
            'customer_name': c.get('name') or 'Registered Customer',
            'customer_email': c.get('email'),
            'order_date': o['date'].isoformat(),
            'total_amount': round(o['total'], 2),
            'order_status': o['status'] or 'Confirmed',
        })

    return {
        'period': {
            'days': days,
            'current_start': cur_start.isoformat(),
            'current_end': today.isoformat(),
            'previous_start': prev_start.isoformat(),
            'previous_end': cur_start.isoformat(),
        },
        'kpis': {
            'total_revenue': round(cur_rev, 2),
            'previous_revenue': round(prev_rev, 2),
            'revenue_growth_pct': _pct_change(cur_rev, prev_rev),
            'total_orders': cur_orders,
            'previous_orders': prev_orders,
            'orders_growth_pct': _pct_change(cur_orders, prev_orders),
            'total_products': total_products,
            'total_customers': total_customers,
            'new_customers': new_cur,
            'previous_new_customers': new_prev,
            'customers_growth_pct': _pct_change(new_cur, new_prev),
            'avg_order_value': round(aov, 2),
            'previous_avg_order_value': round(prev_aov, 2),
            'aov_growth_pct': _pct_change(aov, prev_aov),
            'low_stock_count': len(low_stock_rows) + len(out_of_stock_rows),
            'low_stock_growth_pct': None,
        },
        'inventory_health': {
            'low_stock': low_stock_rows[:10],
            'out_of_stock': out_of_stock_rows[:10],
            'overstocked': overstocked_rows[:10],
            'fast_moving': fast_moving_rows[:10],
            'counts': {
                'low_stock': len(low_stock_rows),
                'out_of_stock': len(out_of_stock_rows),
                'overstocked': len(overstocked_rows),
                'fast_moving': len(fast_moving_rows),
            },
        },
        'sales_performance': {
            'top_selling_products': top_selling,
            'top_revenue_products': top_revenue,
            'top_categories': top_categories,
            'daily_trend': daily_trend,
            'recent_orders': recent_orders,
        },
    }


# ---------------------------------------------------------------------------
# 2. REVENUE FORECAST — monthly actual series from fact_demand + OLS forecast
# ---------------------------------------------------------------------------
def _monthly_actual_revenue_series():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT dt.year, dt.month, MAX(dt.month_name),
                   COALESCE(SUM(fd.units_sold * COALESCE(dp.selling_price, 0)), 0) AS revenue,
                   COALESCE(SUM(fd.units_sold), 0) AS units
            FROM fact_demand fd
            JOIN dim_time dt ON fd.time_key = dt.time_key
            LEFT JOIN dim_product dp ON fd.product_key = dp.product_key
            WHERE dt.year IS NOT NULL AND dt.month IS NOT NULL
            GROUP BY dt.year, dt.month
            ORDER BY dt.year ASC, dt.month ASC
        """)
        rows = cursor.fetchall()

    series = []
    for r in rows:
        year, month = int(r[0]), int(r[1])
        period = f"{year:04d}-{month:02d}"
        label = r[2] or f"{year:04d}-{month:02d}"
        series.append({
            'period': period,
            'label': f"{label} {year}",
            'revenue': round(float(r[3] or 0), 2),
            'units': int(r[4] or 0),
        })
    return series


def _next_month(year, month):
    if month == 12:
        return year + 1, 1
    return year, month + 1


_MONTH_NAMES = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December',
]


def _days_in_month(year, month):
    if month == 12:
        return 31
    return (datetime.date(year, month + 1, 1) - datetime.date(year, month, 1)).days


def build_revenue_forecast(horizon_months=3):
    horizon_months = max(1, int(horizon_months or 3))
    actual = _monthly_actual_revenue_series()

    MIN_MONTHS = 4  # matches stock_to_be_ordered.feature_builder.MIN_HISTORY_MONTHS

    if len(actual) < MIN_MONTHS:
        return {
            'insufficient_data': True,
            'message': (
                'Revenue forecasting needs at least 4 months of historical '
                'revenue. Only {n} month(s) are available in the data warehouse, '
                'so a reliable forecast cannot be produced.'
            ).format(n=len(actual)),
            'available_months': len(actual),
            'granularity': 'monthly',
            'series': [{**p, 'type': 'actual'} for p in actual],
            'forecast': None,
        }

    # Build OLS features on the aggregate monthly revenue series.
    revenues = [p['revenue'] for p in actual]
    month_nums = [int(p['period'][5:7]) for p in actual]

    X, Y = [], []
    for i in range(1, len(revenues)):
        prev1 = revenues[i - 1]
        prev2 = sum(revenues[max(0, i - 2):i]) / len(revenues[max(0, i - 2):i])
        prev3 = sum(revenues[max(0, i - 3):i]) / len(revenues[max(0, i - 3):i])
        X.append([prev1, prev2, prev3, float(month_nums[i - 1])])
        Y.append(revenues[i])

    coeffs = fit_ols(X, Y)
    series_chart = [{**p, 'type': 'actual'} for p in actual]
    forecast_points = []

    if coeffs:
        window = list(revenues)
        wmonths = list(month_nums)
        last_year, last_month = int(actual[-1]['period'][:4]), int(actual[-1]['period'][5:7])
        for _ in range(horizon_months):
            fy, fm = _next_month(last_year, last_month) if not forecast_points else _next_month(
                int(forecast_points[-1]['period'][:4]), int(forecast_points[-1]['period'][5:7])
            )
            prev1 = window[-1]
            prev2 = sum(window[-2:]) / len(window[-2:])
            prev3 = sum(window[-3:]) / len(window[-3:])
            feat = [prev1, prev2, prev3, float(wmonths[-1])]
            pred = max(0.0, predict_ols(coeffs, feat))
            period = f"{fy:04d}-{fm:02d}"
            point = {
                'period': period,
                'label': f"{_MONTH_NAMES[fm - 1]} {fy}",
                'revenue': round(float(pred), 2),
                'type': 'forecast',
            }
            forecast_points.append(point)
            series_chart.append(point)
            window.append(pred)
            wmonths.append(fm)

    next_month_point = forecast_points[0] if forecast_points else None
    forecast_30 = next_month_point['revenue'] if next_month_point else None
    forecast_7 = None
    if next_month_point:
        fy, fm = int(next_month_point['period'][:4]), int(next_month_point['period'][5:7])
        forecast_7 = round(next_month_point['revenue'] * 7 / _days_in_month(fy, fm), 2)

    last_actual = revenues[-1]
    expected_growth_pct = _pct_change(next_month_point['revenue'], last_actual) if next_month_point else None

    return {
        'insufficient_data': False,
        'message': None,
        'available_months': len(actual),
        'granularity': 'monthly',
        'note': (
            'Historical revenue is aggregated monthly from the data warehouse '
            '(fact_demand.units_sold × dim_product.selling_price). 7-day / 30-day '
            'figures are derived from the next-month forecast by linear proration.'
        ),
        'series': series_chart,
        'last_actual_month': actual[-1],
        'forecast': {
            'method': 'OLS Multiple Linear Regression (month-over-month)',
            'next_month': next_month_point,
            'forecast_7_days': forecast_7,
            'forecast_30_days': forecast_30,
            'expected_growth_pct': expected_growth_pct,
            'points': forecast_points,
        },
    }


# ---------------------------------------------------------------------------
# 3. DEMAND FORECAST — reuse Decision-Tree tiers + OLS stock forecast
# ---------------------------------------------------------------------------
def build_demand_forecast():
    stock_result = run_stock_forecast()

    # Demand tiers (optional enrichment; never blocks quantity forecast).
    tier_map = {}
    tier_meta = {}
    try:
        dt = DecisionTreeEngine.run_pipeline()
        if dt.get('success'):
            for p in dt.get('product_predictions', []):
                tier_map[p.get('product_key')] = p.get('predicted_demand')
            tier_meta = dt.get('metadata', {})
    except Exception:
        tier_map = {}

    if not stock_result.get('success'):
        return {
            'insufficient_data': True,
            'message': stock_result.get('error')
            or 'Demand forecasting needs historical demand data that is not yet available.',
            'granularity': 'monthly',
            'products': [],
        }

    forecast_month = stock_result.get('forecast_month')
    forecast_month_label = stock_result.get('forecast_month_label')
    fy, fm = (int(forecast_month[:4]), int(forecast_month[5:7])) if forecast_month else (None, None)
    dim = _days_in_month(fy, fm) if fy else 30

    products_out = []
    total_next_month_units = 0
    for p in stock_result.get('products', []):
        predicted_units = int(p.get('predicted_demand') or 0)
        current_stock = int(p.get('current_stock') or 0)
        need_to_order = int(p.get('need_to_order') or 0)
        tier = tier_map.get(p.get('product_key'), 'Unrated')
        total_next_month_units += predicted_units

        products_out.append({
            'product_key': p.get('product_key'),
            'product_id': p.get('product_id'),
            'product_name': p.get('product_name'),
            'category_name': p.get('category_name'),
            'predicted_demand': tier,
            'predicted_units_next_month': predicted_units,
            'current_stock': current_stock,
            'need_to_order': need_to_order,
        })

    high_demand = sorted(
        [p for p in products_out if (p['predicted_demand'] or '').lower() == 'high'],
        key=lambda p: p['predicted_units_next_month'], reverse=True,
    )
    low_demand = sorted(
        [p for p in products_out if (p['predicted_demand'] or '').lower() == 'low'],
        key=lambda p: p['predicted_units_next_month'],
    )
    restock = sorted(
        (p for p in products_out if p['need_to_order'] > 0),
        key=lambda p: p['need_to_order'], reverse=True,
    )

    # Demand TREND indicator. The trend is measured from ACTUAL observed demand
    # (monthly units_sold in fact_demand) using a smoothed basis (average of the
    # 3 most recent COMPLETED months vs the 3 before them). The latest calendar
    # month is excluded when it is clearly a partial month (volume far below the
    # typical median) so it cannot falsely look like a collapse/spike. The
    # PREDICTED next-month demand is reported separately and never mixed into
    # the actual-trend calculation. Direction thresholds: +/-5%.
    demand_trend = {
        'direction': 'stable',
        'change_pct': None,
        'basis': '3-month average of completed months vs the prior 3 months (observed demand)',
        'latest_complete_month': None,
        'latest_actual_units': None,
        'excluded_partial_month': None,
        'predicted_next_month_units': total_next_month_units,
        'series': [],
        'note': None,
    }
    try:
        monthly = _monthly_actual_revenue_series()  # {period,label,revenue,units}
        if monthly:
            units_all = [int(m['units'] or 0) for m in monthly]
            labels_all = [m['label'] for m in monthly]
            med = median(units_all) if units_all else 0

            trend_units = units_all
            trend_labels = labels_all
            if len(units_all) >= 2 and med > 0 and units_all[-1] < 0.25 * med:
                # Trailing month looks like an in-progress month -> exclude it.
                demand_trend['excluded_partial_month'] = labels_all[-1]
                trend_units = units_all[:-1]
                trend_labels = labels_all[:-1]

            n = len(trend_units)
            if n >= 1:
                demand_trend['latest_actual_units'] = trend_units[-1]
                demand_trend['latest_complete_month'] = trend_labels[-1]
            recent = trend_units[-3:] if n >= 3 else trend_units
            prior = trend_units[-6:-3] if n >= 6 else (trend_units[:-3] if n > 3 else [])
            recent_avg = (sum(recent) / len(recent)) if recent else 0
            prior_avg = (sum(prior) / len(prior)) if prior else 0

            if prior_avg > 0:
                change = round((recent_avg - prior_avg) / prior_avg * 100, 1)
                demand_trend['change_pct'] = change
                if change > 5:
                    demand_trend['direction'] = 'increasing'
                elif change < -5:
                    demand_trend['direction'] = 'decreasing'
                else:
                    demand_trend['direction'] = 'stable'

            start = max(0, n - 6)
            demand_trend['series'] = [
                {'label': trend_labels[i], 'units': trend_units[i]} for i in range(start, n)
            ]
            demand_trend['note'] = (
                f"Observed demand trend across completed months"
                f"{(' (latest partial month ' + demand_trend['excluded_partial_month'] + ' excluded)') if demand_trend['excluded_partial_month'] else ''}"
                f"{(' through ' + demand_trend['latest_complete_month']) if demand_trend['latest_complete_month'] else ''}."
            )
        else:
            demand_trend['note'] = 'No actual demand history available to establish a trend.'
    except Exception:
        demand_trend['note'] = 'Demand trend could not be computed from the available data.'

    return {
        'insufficient_data': False,
        'message': None,
        'granularity': 'monthly',
        'forecast_month': forecast_month,
        'forecast_month_label': forecast_month_label,
        'demand_trend': demand_trend,
        'summary': {
            'total_products_forecasted': len(products_out),
            'high_demand_count': len(high_demand),
            'low_demand_count': len(low_demand),
            'restock_count': len(restock),
            'total_predicted_units_next_month': total_next_month_units,
            'expected_units_7_days': round(total_next_month_units * 7 / dim, 1),
            'expected_units_30_days': total_next_month_units,
            'model_accuracy_pct': tier_meta.get('accuracy_percentage'),
        },
        'high_demand_products': high_demand[:10],
        'low_demand_products': low_demand[:10],
        'restock_recommendations': restock[:15],
        'products': products_out,
    }


# ---------------------------------------------------------------------------
# 4. DEMAND SIGNALS — live wishlist / notify-me / add-to-cart from fact_demand
# ---------------------------------------------------------------------------
# These are OBSERVED customer-interest signals pulled directly from the live
# fact_demand table in Supabase. They are kept strictly separate from actual
# sales (units_sold) / confirmed orders. "total_signals" is the sum of the
# three observed counts and is NOT a statistical forecast — it is labelled as
# an observed demand-signal volume. Demand status is a relative tercile ranking
# of that observed signal volume across the current window (see below).
#
# fact_demand columns used (verified against the live schema):
#   wishlist_count, notify_me_count, cart_quantity  (+ units_sold, unused here)
# joined on product_key -> dim_product and time_key -> dim_time.
def build_demand_signals(months=3):
    try:
        months = max(1, int(months or 3))
    except (TypeError, ValueError):
        months = 3
    months = min(months, 12)  # window guard for a monthly warehouse

    with connection.cursor() as cursor:
        # The most recent `months` month(s) present in the warehouse.
        cursor.execute("""
            SELECT time_key, month_name, year, month_start
            FROM dim_time
            ORDER BY month_start DESC
            LIMIT %s
        """, [months])
        window_rows = cursor.fetchall()

        if not window_rows:
            return {
                'insufficient_data': True,
                'message': 'No time periods are available in the demand warehouse (dim_time).',
                'window': None,
                'totals': {'wishlist': 0, 'notify_me': 0, 'add_to_cart': 0,
                           'total_signals': 0, 'products': 0},
                'products': [],
            }

        latest = window_rows[0]  # dim_time row for the most recent month
        time_keys = [r[0] for r in window_rows]
        placeholders = ','.join(['%s'] * len(time_keys))

        cursor.execute(f"""
            SELECT
                dp.product_id,
                COALESCE(dp.product_name, CONCAT('Product #', dp.product_id)) AS product_name,
                COALESCE(dc.category_name, 'Uncategorized') AS category_name,
                COALESCE(SUM(fd.wishlist_count), 0)  AS wishlist,
                COALESCE(SUM(fd.notify_me_count), 0) AS notify_me,
                COALESCE(SUM(fd.cart_quantity), 0)   AS add_to_cart
            FROM fact_demand fd
            JOIN dim_product dp ON fd.product_key = dp.product_key
            LEFT JOIN dim_category dc ON fd.category_key = dc.category_key
            WHERE fd.time_key IN ({placeholders})
            GROUP BY dp.product_id, dp.product_name, dc.category_name
            ORDER BY dp.product_id
        """, time_keys)
        rows = cursor.fetchall()

    products = []
    tot_w = tot_n = tot_c = 0
    for r in rows:
        wishlist = int(r[3] or 0)
        notify_me = int(r[4] or 0)
        add_to_cart = int(r[5] or 0)
        total = wishlist + notify_me + add_to_cart
        tot_w += wishlist
        tot_n += notify_me
        tot_c += add_to_cart
        products.append({
            'product_id': str(r[0]),
            'product_name': r[1],
            'category_name': r[2],
            'wishlist': wishlist,
            'notify_me': notify_me,
            'add_to_cart': add_to_cart,
            'total_signals': total,
        })

    # Relative demand-status ranking: products already sorted by total_signals
    # descending. Among products that HAVE signals, the top third are 'High
    # Interest', the middle third 'Moderate Interest', the bottom third 'Low
    # Interest'; products with zero observed signals are 'No Signals'. This is a
    # relative ranking of observed interest, not an absolute threshold.
    positives = [p for p in products if p['total_signals'] > 0]
    n_pos = len(positives)
    for i, p in enumerate(positives):
        frac = (i / n_pos) if n_pos else 1.0
        if frac < 1 / 3:
            p['demand_status'] = 'High Interest'
        elif frac < 2 / 3:
            p['demand_status'] = 'Moderate Interest'
        else:
            p['demand_status'] = 'Low Interest'
    for p in products:
        if p['total_signals'] <= 0:
            p['demand_status'] = 'No Signals'

    products.sort(key=lambda p: p['total_signals'], reverse=True)

    earliest = window_rows[-1]

    def _label(row):
        # row = (time_key, month_name, year, month_start)
        return f"{row[1]} {row[2]}" if row[1] else str(row[3])

    if len(window_rows) > 1:
        window_label = f"{_label(earliest)} – {_label(latest)}"
        period_note = f"Last {len(window_rows)} months"
    else:
        window_label = _label(latest)
        period_note = "Latest month"

    return {
        'insufficient_data': False,
        'message': None,
        'window': {
            'months': len(window_rows),
            'label': window_label,
            'description': f"{period_note}: {window_label}",
        },
        'metric_definition': (
            'Wishlist, Notify-Me and Add-to-Cart counts are observed customer-'
            'interest signals aggregated from live fact_demand for the selected '
            'window. Total Demand Signals is their sum (an observed interest '
            'volume, NOT a statistically modelled sales forecast) and is kept '
            'separate from confirmed sales/orders.'
        ),
        'demand_status_rule': (
            'Relative ranking of Total Demand Signals among products that have at '
            'least one signal in the window: High Interest (top third), Moderate '
            'Interest (middle third), Low Interest (bottom third). Products with '
            'no observed signals are marked No Signals.'
        ),
        'totals': {
            'wishlist': tot_w,
            'notify_me': tot_n,
            'add_to_cart': tot_c,
            'total_signals': tot_w + tot_n + tot_c,
            'products': len(products),
        },
        'products': products,
    }
