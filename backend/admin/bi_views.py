"""
bi_views.py
-----------
Admin-only Business-Intelligence endpoints powering the redesigned dashboard.

Routes (all require the ADMIN role):
    GET /api/admin/bi/overview/?days=30
    GET /api/admin/bi/revenue-forecast/?horizon=3
    GET /api/admin/bi/demand-forecast/

They reuse ``admin.bi_services`` and the existing forecasting engines. The
legacy ``/api/admin/dashboard/`` endpoint is left untouched so nothing that
currently consumes it breaks.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from accounts.permissions import IsAuthenticatedUser, IsAdmin
from admin.bi_services import (
    build_overview,
    build_revenue_forecast,
    build_demand_forecast,
    build_demand_signals,
)


class AdminBIOverviewView(APIView):
    """KPI cards (with period-over-period growth), inventory health and sales
    performance for the selected date range."""
    permission_classes = [IsAuthenticatedUser, IsAdmin]

    def get(self, request):
        try:
            days = int(request.query_params.get('days') or 30)
        except (TypeError, ValueError):
            days = 30
        data = build_overview(days=days)
        return Response(data, status=status.HTTP_200_OK)


class AdminBIRevenueForecastView(APIView):
    """Historical monthly revenue (actual) plus an OLS forecast of the next
    months, with derived 7 / 30-day figures."""
    permission_classes = [IsAuthenticatedUser, IsAdmin]

    def get(self, request):
        try:
            horizon = int(request.query_params.get('horizon') or 3)
        except (TypeError, ValueError):
            horizon = 3
        data = build_revenue_forecast(horizon_months=horizon)
        # ``insufficient_data`` is a valid 200 response — the UI shows the
        # explanatory message instead of a fabricated chart.
        return Response(data, status=status.HTTP_200_OK)


class AdminBIDemandForecastView(APIView):
    """Product-wise demand forecast, high/low demand movers and restock
    recommendations (reuses the OLS stock forecast + Decision-Tree tiers)."""
    permission_classes = [IsAuthenticatedUser, IsAdmin]

    def get(self, request):
        data = build_demand_forecast()
        return Response(data, status=status.HTTP_200_OK)


class AdminBIDemandSignalsView(APIView):
    """Live customer-interest demand signals (wishlist / notify-me / add-to-cart)
    aggregated directly from the fact_demand table in Supabase.

    GET /api/admin/bi/demand-signals/?months=3
    """
    permission_classes = [IsAuthenticatedUser, IsAdmin]

    def get(self, request):
        try:
            months = int(request.query_params.get('months') or 3)
        except (TypeError, ValueError):
            months = 3
        data = build_demand_signals(months=months)
        return Response(data, status=status.HTTP_200_OK)
