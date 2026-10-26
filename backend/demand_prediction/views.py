import os

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.permissions import IsAuthenticatedUser, IsAdmin
from demand_prediction.engine import DecisionTreeEngine
from catalog.serializers import resolve_product_image
from django.db import connection
from datetime import datetime, timedelta


class DemandPredictionAnalyticsView(APIView):
    """
    API View for Demand Forecasting & Prediction module.
    
    Provides:
    - Executive summary & metrics
    - Entropy (Shannon Entropy calculation)
    - Information Gain for each feature (units_sold, cart_quantity, wishlist_count, discount_percentage, notify_me_count)
    - Best Split parameters (feature, threshold, Information Gain)
    - Decision Tree visual structure
    - Product-wise demand predictions (High, Medium, Low)
    """
    permission_classes = [IsAuthenticatedUser, IsAdmin]

    def get(self, request):
        try:
            results = DecisionTreeEngine.run_pipeline()

            if not results.get('success'):
                return Response({
                    'error': results.get('error', 'Failed to calculate demand predictions.')
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Optional query filters for product predictions
            search = request.query_params.get('search', '').strip().lower()
            demand_level = request.query_params.get('demand_level', '').strip().upper()
            category = request.query_params.get('category', '').strip().lower()

            predictions = results['product_predictions']

            if search:
                predictions = [
                    p for p in predictions 
                    if search in p['product_name'].lower() or search in p['category_name'].lower()
                ]

            if demand_level and demand_level != 'ALL':
                predictions = [
                    p for p in predictions 
                    if p['predicted_demand'].upper() == demand_level
                ]

            if category and category != 'all':
                predictions = [
                    p for p in predictions 
                    if category in p['category_name'].lower()
                ]

            # Return response with filtered predictions and complete analytical metrics
            response_data = {
                'metadata': results['metadata'],
                'summary': results['summary'],
                'entropy': results['entropy'],
                'information_gains': results['information_gains'],
                'best_split': results['best_split'],
                'decision_tree': results['decision_tree'],
                'product_predictions': predictions,
                'total_filtered_products': len(predictions)
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'error': f'An error occurred during demand prediction calculation: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SlowMovingInventoryView(APIView):
    """
    API View for Slow-Moving Inventory Analysis.
    
    Calculates inventory velocity for each product-warehouse combination using
    existing tables: inventory, order_items, orders, products, categories, warehouses.
    
    Classification:
    - VERY SLOW: sales_last_30_days == 0 OR days_of_stock > 180
    - SLOW: days_of_stock > 60 AND <= 180
    - NORMAL: days_of_stock <= 60
    """
    permission_classes = [IsAuthenticatedUser, IsAdmin]

    # Configurable business rules (defaults preserve the original behaviour).
    DEFAULT_SALES_WINDOW_DAYS = 30
    DEFAULT_SLOW_DAYS = 60
    DEFAULT_OVERSTOCK_DAYS = 180

    @staticmethod
    def _param_int(request, name, default):
        raw = request.query_params.get(name)
        if raw is None or str(raw).strip() == '':
            return default
        try:
            val = int(float(raw))
            return val if val > 0 else default
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _parse_date(value):
        if not value:
            return None
        text = str(value).strip()[:10]
        try:
            return datetime.strptime(text, '%Y-%m-%d').date()
        except ValueError:
            return None

    def get(self, request):
        try:
            cursor = connection.cursor()

            # --- Configurable slow-moving rules (query params / env fallback) ---
            window_days = self._param_int(
                request, 'sales_window_days',
                int(os.getenv('SLOW_MOVING_WINDOW_DAYS', self.DEFAULT_SALES_WINDOW_DAYS)),
            )
            slow_days = self._param_int(
                request, 'slow_days',
                int(os.getenv('SLOW_MOVING_SLOW_DAYS', self.DEFAULT_SLOW_DAYS)),
            )
            overstock_days = self._param_int(
                request, 'overstock_days',
                int(os.getenv('SLOW_MOVING_OVERSTOCK_DAYS', self.DEFAULT_OVERSTOCK_DAYS)),
            )

            today = datetime.now().date()
            window_start = today - timedelta(days=window_days)

            # Query: per product+warehouse -> stock, sales in window, last sale, price.
            query = """
                SELECT
                    inv.product_id,
                    COALESCE(p.product_name, CONCAT('Product #', inv.product_id)) AS product_name,
                    COALESCE(c.category_name, 'Uncategorized') AS category_name,
                    inv.warehouse_id,
                    COALESCE(w.warehouse_name, CONCAT('Warehouse #', inv.warehouse_id)) AS warehouse_name,
                    COALESCE(inv.stock_quantity, 0) AS current_stock,
                    COALESCE(sales.total_sold, 0) AS sales_last_window,
                    COALESCE(p.selling_price, p.base_price, p.cost_price, 0) AS unit_value,
                    sales_last.last_sale_date AS last_sale_date
                FROM inventory inv
                LEFT JOIN products p ON inv.product_id = p.product_id
                LEFT JOIN categories c ON p.category_id = c.category_id
                LEFT JOIN warehouses w ON inv.warehouse_id = w.warehouse_id
                LEFT JOIN (
                    SELECT
                        oi.product_id,
                        o.warehouse_id,
                        COALESCE(SUM(oi.quantity), 0) AS total_sold
                    FROM order_items oi
                    JOIN orders o ON oi.order_id = o.order_id
                    WHERE o.order_date >= %s
                      AND LOWER(COALESCE(o.order_status, '')) NOT IN ('cancelled', 'returned', 'failed')
                    GROUP BY oi.product_id, o.warehouse_id
                ) sales ON inv.product_id = sales.product_id AND inv.warehouse_id = sales.warehouse_id
                LEFT JOIN (
                    SELECT
                        oi.product_id,
                        o.warehouse_id,
                        MAX(o.order_date) AS last_sale_date
                    FROM order_items oi
                    JOIN orders o ON oi.order_id = o.order_id
                    WHERE LOWER(COALESCE(o.order_status, '')) NOT IN ('cancelled', 'returned', 'failed')
                    GROUP BY oi.product_id, o.warehouse_id
                ) sales_last ON inv.product_id = sales_last.product_id AND inv.warehouse_id = sales_last.warehouse_id
                WHERE COALESCE(inv.stock_quantity, 0) > 0
                ORDER BY inv.product_id, inv.warehouse_id
            """
            cursor.execute(query, [str(window_start)])
            rows = cursor.fetchall()

            items = []
            for row in rows:
                product_id = row[0]
                product_name = row[1]
                category_name = row[2]
                warehouse_id = row[3]
                warehouse_name = row[4]
                current_stock = int(row[5] or 0)
                sales_last_window = int(row[6] or 0)
                unit_value = float(row[7] or 0)
                last_sale_date = self._parse_date(row[8])

                avg_daily_sales = round(sales_last_window / float(window_days), 2) if sales_last_window > 0 else 0.0

                if avg_daily_sales > 0:
                    days_of_stock = round(current_stock / avg_daily_sales, 1)
                else:
                    days_of_stock = None  # No sales -> effectively infinite cover

                # --- Backward-compatible movement_status ---
                if sales_last_window == 0 or (days_of_stock is not None and days_of_stock > overstock_days):
                    movement_status = 'VERY SLOW'
                elif days_of_stock is not None and days_of_stock > slow_days:
                    movement_status = 'SLOW'
                else:
                    movement_status = 'NORMAL'

                # --- Clear BI labels: Non-Moving / Slow Moving / Overstocked / Healthy ---
                if sales_last_window == 0:
                    category_label = 'Non-Moving'
                    suggested_action = 'Run clearance / markdown, or return stock to vendor'
                elif days_of_stock is not None and days_of_stock > overstock_days:
                    category_label = 'Overstocked'
                    suggested_action = 'Pause reorders and promote to burn excess stock'
                elif days_of_stock is not None and days_of_stock > slow_days:
                    category_label = 'Slow Moving'
                    suggested_action = 'Targeted promotion, bundle or discount'
                else:
                    category_label = 'Healthy'
                    suggested_action = 'No action required'

                recommended_action = suggested_action
                display_days = days_of_stock if days_of_stock is not None else 999999
                days_since_last_sale = (today - last_sale_date).days if last_sale_date else None

                items.append({
                    'product_id': product_id,
                    'product_name': product_name,
                    'category_name': category_name,
                    'warehouse_id': warehouse_id,
                    'warehouse_name': warehouse_name,
                    'image': resolve_product_image(product_id=product_id, category_name=category_name),
                    'current_stock': current_stock,
                    'sales_last_30_days': sales_last_window,
                    'sales_last_window': sales_last_window,
                    'avg_daily_sales': avg_daily_sales,
                    'days_of_stock': display_days,
                    'movement_status': movement_status,
                    'category_label': category_label,
                    'inventory_value': round(current_stock * unit_value, 2),
                    'last_sale_date': last_sale_date.isoformat() if last_sale_date else None,
                    'days_since_last_sale': days_since_last_sale,
                    'recommended_action': recommended_action,
                    'suggested_action': suggested_action,
                })

            # Apply optional query filters
            search = request.query_params.get('search', '').strip().lower()
            movement_filter = request.query_params.get('movement_status', '').strip().upper()
            label_filter = request.query_params.get('category_label', '').strip().lower()
            warehouse_filter = request.query_params.get('warehouse_id', '').strip()

            filtered = items

            if search:
                filtered = [
                    i for i in filtered
                    if search in i['product_name'].lower() or search in i['category_name'].lower()
                ]

            if movement_filter and movement_filter != 'ALL':
                filtered = [
                    i for i in filtered
                    if i['movement_status'] == movement_filter
                ]

            if label_filter and label_filter != 'all':
                filtered = [
                    i for i in filtered
                    if i['category_label'].lower() == label_filter
                ]

            if warehouse_filter and warehouse_filter.lower() != 'all':
                filtered = [
                    i for i in filtered
                    if str(i['warehouse_id']) == warehouse_filter
                ]

            # Build summary counts from FULL (unfiltered) data
            very_slow_count = sum(1 for i in items if i['movement_status'] == 'VERY SLOW')
            slow_count = sum(1 for i in items if i['movement_status'] == 'SLOW')
            normal_count = sum(1 for i in items if i['movement_status'] == 'NORMAL')

            non_moving = [i for i in items if i['category_label'] == 'Non-Moving']
            slow_moving = [i for i in items if i['category_label'] == 'Slow Moving']
            overstocked = [i for i in items if i['category_label'] == 'Overstocked']
            stagnant = non_moving + slow_moving + overstocked
            tied_up_value = round(sum(i['inventory_value'] for i in stagnant), 2)

            # Get unique warehouses for filter dropdown
            warehouses_list = sorted(list(set(
                (i['warehouse_id'], i['warehouse_name']) for i in items
            )), key=lambda x: x[1])

            response_data = {
                'summary': {
                    'total_inventory': len(items),
                    'very_slow': very_slow_count,
                    'slow': slow_count,
                    'normal': normal_count,
                    'non_moving': len(non_moving),
                    'slow_moving': len(slow_moving),
                    'overstocked': len(overstocked),
                    'stagnant_count': len(stagnant),
                    'stagnant_inventory_value': tied_up_value,
                },
                'thresholds': {
                    'sales_window_days': window_days,
                    'slow_days': slow_days,
                    'overstock_days': overstock_days,
                },
                'warehouses': [
                    {'warehouse_id': wid, 'warehouse_name': wname}
                    for wid, wname in warehouses_list
                ],
                'items': filtered,
                'total_filtered': len(filtered),
                'analysis_date': str(today),
                'sales_window_start': str(window_start),
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'error': f'An error occurred during slow-moving inventory analysis: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
