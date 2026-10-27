from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from .services import RecommendationService
from .serializers import ProductRecommendationsResponseSerializer


class ProductRecommendationView(APIView):
    """
    GET /api/recommendations/<product_id>/

    Retrieves Apriori-based 'frequently bought together' product recommendations
    for a given product_id.

    - Resolves product_id using the catalog products table.
    - Matches association rules from the product_recommendations table.
    - Returns recommended products and statistical metrics (support, confidence, lift).
    - If the product exists but has no association rules, returns an empty recommendation list.
    - If product_id does not exist, returns 404.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, product_id):
        if not product_id or not str(product_id).strip():
            return Response(
                {'detail': 'A valid product_id parameter is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        clean_product_id = str(product_id).strip()
        data = RecommendationService.get_recommendations_for_product(clean_product_id)

        if data is None:
            return Response(
                {'detail': f'Product with id "{clean_product_id}" was not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProductRecommendationsResponseSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SmartBudgetStylistView(APIView):
    """
    GET / POST /api/recommendations/stylist/

    Curates complete, stylish, budget-compliant fashion outfits from the real catalog
    across all categories:
      - Western wear (Tops, T-shirts, shirts, jeans, trousers, skirts, dresses, jumpsuits, co-ords)
      - Ethnic wear (Kurtis, sarees, lehengas, salwar suits, palazzos, dupattas, juttis, potlis)
      - Indo-Western fusion (Kurti + jeans, ethnic tops + trousers, fusion accessories)
      - Footwear, bags, and accessories

    Query / Body Parameters:
      - budget: float (e.g., 2500, default 2500)
      - occasion: str ('College', 'Casual', 'Party', 'Formal', 'Festive', 'All')
      - style: str ('Minimal', 'Chic', 'Streetwear', 'Traditional', 'Elegant', 'All')
      - fashion_direction: str ('Western', 'Ethnic', 'Indo-Western', 'Dresses & Jumpsuits', 'Surprise Me')
      - preferred_colors: list or comma-separated str (e.g., 'Pink,Beige')
      - sort_by: str ('match', 'price_asc', 'savings_desc', 'score_desc')
      - limit: int (default 6)
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        params = request.query_params
        return self._generate_looks(params)

    def post(self, request):
        params = request.data if request.data else request.query_params
        return self._generate_looks(params)

    def _generate_looks(self, params):
        from catalog.models import Product
        from catalog.serializers import get_product_image_url
        from .outfit_engine import OutfitCompatibilityEngine, get_slot_for_item

        # Parse budget
        try:
            raw_budget = params.get('budget', 2500)
            budget = float(raw_budget)
            if budget <= 0:
                budget = 2500.0
        except (ValueError, TypeError):
            budget = 2500.0

        # Parse preferences
        occasion = params.get('occasion', 'College')
        if occasion and occasion.lower() == 'all':
            occasion = None

        style = params.get('style', 'Chic')
        if style and style.lower() == 'all':
            style = None

        raw_direction = params.get('fashion_direction', 'Surprise Me')
        fashion_direction = 'Surprise Me'
        if raw_direction:
            f_clean = str(raw_direction).strip().lower()
            if 'dress' in f_clean or 'jumpsuit' in f_clean:
                fashion_direction = 'Dresses & Jumpsuits'
            elif 'indo' in f_clean:
                fashion_direction = 'Indo-Western'
            elif 'ethnic' in f_clean:
                fashion_direction = 'Ethnic'
            elif 'west' in f_clean:
                fashion_direction = 'Western'
            elif 'surprise' in f_clean or 'all' in f_clean:
                fashion_direction = 'Surprise Me'

        sort_by = params.get('sort_by', 'match')

        # Parse preferred colors
        raw_colors = params.get('preferred_colors')
        preferred_colors = []
        if isinstance(raw_colors, list):
            preferred_colors = [str(c).strip() for c in raw_colors if str(c).strip()]
        elif isinstance(raw_colors, str) and raw_colors.strip():
            preferred_colors = [c.strip() for c in raw_colors.split(',') if c.strip()]

        try:
            limit = int(params.get('limit', 6))
            limit = max(1, min(limit, 24))
        except (ValueError, TypeError):
            limit = 6

        # Fetch active products from database (excluding kids wear for adult styling)
        products_qs = Product.objects.filter(is_active=True).exclude(
            category__category_name='Kids Wear'
        ).select_related('category')
        candidates = []


        for p in products_qs:
            cat_name = p.category.category_name if p.category else ''
            candidates.append({
                'product_id': p.product_id,
                'product_name': p.product_name or 'Fashion Item',
                'category_id': p.category.category_id if p.category else None,
                'category_name': cat_name,
                'selling_price': float(p.selling_price or 0),
                'base_price': float(p.base_price or p.selling_price or 0),
                'color': p.color or '',
                'gender': p.gender or 'Women',
                'material': p.material or '',
                'image': get_product_image_url(p),
                'in_stock': True,
                'slot': get_slot_for_item({
                    'category_name': cat_name,
                    'product_name': p.product_name
                }),
            })

        # Assemble budget-compliant outfits
        outfits = OutfitCompatibilityEngine.assemble_outfits(
            candidate_items=candidates,
            budget=budget,
            occasion=occasion,
            style=style,
            fashion_direction=fashion_direction,
            preferred_colors=preferred_colors,
            complete_outfit=True,
            max_results=limit
        )

        # Apply secondary sort if specified
        if sort_by == 'price_asc':
            outfits.sort(key=lambda x: x['total_price'])
        elif sort_by == 'savings_desc':
            outfits.sort(key=lambda x: (-x['discount_percent'], -x['remaining_budget']))
        elif sort_by == 'score_desc':
            outfits.sort(key=lambda x: -x['score'])

        # Response payload
        return Response({
            'success': True,
            'budget': budget,
            'occasion': occasion or 'All Occasions',
            'style': style or 'All Styles',
            'fashion_direction': fashion_direction,
            'preferred_colors': preferred_colors,
            'sort_by': sort_by,
            'total_looks': len(outfits),
            'outfits': outfits,
            'available_options': {
                'occasions': ['College', 'Casual', 'Party', 'Formal', 'Festive'],
                'styles': ['Minimal', 'Chic', 'Streetwear', 'Traditional', 'Elegant'],
                'fashion_directions': ['Western', 'Ethnic', 'Indo-Western', 'Dresses & Jumpsuits', 'Surprise Me'],
                'colors': ['Black', 'White', 'Beige', 'Pink', 'Red', 'Blue', 'Green', 'Yellow', 'Purple', 'Maroon'],
                'budget_presets': [999, 1499, 2499, 4999],
            }
        }, status=status.HTTP_200_OK)

