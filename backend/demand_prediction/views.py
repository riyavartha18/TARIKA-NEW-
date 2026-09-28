from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.permissions import IsAuthenticatedUser, IsAdmin
from demand_prediction.engine import DecisionTreeEngine


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
