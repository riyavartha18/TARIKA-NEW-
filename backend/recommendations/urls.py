from django.urls import path
from .views import ProductRecommendationView, SmartBudgetStylistView

app_name = 'recommendations'

urlpatterns = [
    path('stylist/', SmartBudgetStylistView.as_view(), name='smart-budget-stylist'),
    path('<str:product_id>/', ProductRecommendationView.as_view(), name='product-recommendations'),
]

