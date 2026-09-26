from django.urls import path
from delivery.views import (
    DeliveryPartnerMyDeliveriesView,
    DeliveryPartnerDetailView,
    DeliveryPartnerStatusUpdateView,
    DeliveryPartnerDashboardView,
    DeliveryPartnersListView,
)

app_name = 'delivery'

urlpatterns = [
    path('my-deliveries/', DeliveryPartnerMyDeliveriesView.as_view(), name='my-deliveries'),
    path('deliveries/<str:delivery_id>/', DeliveryPartnerDetailView.as_view(), name='delivery-detail'),
    path('deliveries/<str:delivery_id>/status/', DeliveryPartnerStatusUpdateView.as_view(), name='delivery-status-update'),
    path('dashboard/', DeliveryPartnerDashboardView.as_view(), name='dashboard'),
    path('partners/', DeliveryPartnersListView.as_view(), name='partners-list'),
]
