from django.urls import path
from demand_prediction.views import DemandPredictionAnalyticsView

app_name = 'demand_prediction'

urlpatterns = [
    path('analytics/', DemandPredictionAnalyticsView.as_view(), name='analytics'),
]
