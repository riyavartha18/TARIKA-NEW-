from rest_framework import serializers
from .models import Category, Product, Inventory, Review, Manufacturer


class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = [
            'manufacturer_id',
            'manufacturer_name',
            'contact_person',
            'email',
            'phone',
            'country',
            'city',
            'state'
        ]


CATEGORY_IMAGE_MAPPING = {
    'dresses': 'https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=600&auto=format&fit=crop&q=80',
    't-shirts': 'https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=600&auto=format&fit=crop&q=80',
    'tops': 'https://images.unsplash.com/photo-1564257631407-4deb1f99d992?w=600&auto=format&fit=crop&q=80',
    'shirts': 'https://images.unsplash.com/photo-1598033129183-c4f50c736f10?w=600&auto=format&fit=crop&q=80',
    'jeans': 'https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=600&auto=format&fit=crop&q=80',
    'trousers': 'https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=600&auto=format&fit=crop&q=80',
    'bottom wear': 'https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=600&auto=format&fit=crop&q=80',
    'kurtis': 'https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=600&auto=format&fit=crop&q=80',
    'sarees': 'https://images.unsplash.com/photo-1617627143750-d86bc21e42bb?w=600&auto=format&fit=crop&q=80',
    'jackets': 'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=600&auto=format&fit=crop&q=80',
    'sweaters': 'https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=600&auto=format&fit=crop&q=80',
    'ethnic wear': 'https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=600&auto=format&fit=crop&q=80',
    'footwear': 'https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=600&auto=format&fit=crop&q=80',
    'handbags': 'https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=600&auto=format&fit=crop&q=80',
    'accessories': 'https://images.unsplash.com/photo-1611652022419-a9419f74343d?w=600&auto=format&fit=crop&q=80',
    'kids wear': 'https://images.unsplash.com/photo-1514090458221-65bb69cf63e6?w=600&auto=format&fit=crop&q=80',
}


TEST_PRODUCT_IMAGE_OVERRIDES = {
    '8cbb34d5-4bea-419e-81b7-4ed27a88ee7e': '/images/products/8cbb34d5-4bea-419e-81b7-4ed27a88ee7e.png',
    'c0b562f4-1dce-474b-8924-8416ed399595': '/images/products/c0b562f4-1dce-474b-8924-8416ed399595.png',
    '92a3e99a-a6a6-4930-bedf-56d02ba4740e': '/images/products/92a3e99a-a6a6-4930-bedf-56d02ba4740e.png',
    'c7125cbd-aeab-44c0-aa71-ec3ef3ed0b7f': '/images/products/c7125cbd-aeab-44c0-aa71-ec3ef3ed0b7f.png',
    '8e7b8c20-41f9-4e74-b55a-cadc8b5c6f7f': '/images/products/8e7b8c20-41f9-4e74-b55a-cadc8b5c6f7f.png',
    'c72193ee-ac55-4109-a7e4-7894be55ac2a': '/images/products/c72193ee-ac55-4109-a7e4-7894be55ac2a.jpg',
    '60a2d050-8af4-4a9d-8468-a14235ff8960': '/images/products/60a2d050-8af4-4a9d-8468-a14235ff8960.jpg',
    'faee2a9e-3ae3-46c3-b224-f42a9f03f311': '/images/products/faee2a9e-3ae3-46c3-b224-f42a9f03f311.jpg',
    '069ca6b5-8175-4272-8ca1-2d458b069dd5': '/images/products/069ca6b5-8175-4272-8ca1-2d458b069dd5.jpg',
    '415e7f69-1631-4fc8-b9ad-c3da62eb7c07': '/images/products/415e7f69-1631-4fc8-b9ad-c3da62eb7c07.jpg',
    'ab690c10-5dd5-41f9-853d-4090ab3e9d16': '/images/products/ab690c10-5dd5-41f9-853d-4090ab3e9d16.jpg',
    'acba5eb0-d381-40e8-a8c0-1f5c9c7d9407': '/images/products/acba5eb0-d381-40e8-a8c0-1f5c9c7d9407.jpg',
    'e0aa9c14-77a3-449e-a703-014298681d90': '/images/products/e0aa9c14-77a3-449e-a703-014298681d90.jpg',
    '12f33c64-50bc-4b94-b98d-36c2734651cb': '/images/products/12f33c64-50bc-4b94-b98d-36c2734651cb.jpg',
    '53d00696-fc2a-4a94-91fe-b64cc16c1f78': '/images/products/53d00696-fc2a-4a94-91fe-b64cc16c1f78.jpg',
    '82d3fd8d-d283-4c77-8d4c-9e6ec78c486d': '/images/products/82d3fd8d-d283-4c77-8d4c-9e6ec78c486d.jpg',
    '8c92b228-28ea-4b31-9153-04de0fb56a9b': '/images/products/8c92b228-28ea-4b31-9153-04de0fb56a9b.jpg',
    'a71aff6b-30e7-411d-9730-e83fb93fba0e': '/images/products/a71aff6b-30e7-411d-9730-e83fb93fba0e.jpg',
    '64df1560-0a7e-4cec-9197-b8b869001495': '/images/products/64df1560-0a7e-4cec-9197-b8b869001495.jpg',
    'f6e694ec-0a39-4861-b456-b00650819096': '/images/products/f6e694ec-0a39-4861-b456-b00650819096.jpg',
    '2007a7f0-a19b-4fc9-9304-f473b3478d0a': '/images/products/2007a7f0-a19b-4fc9-9304-f473b3478d0a.jpg',
    '3a1fba5a-017d-4b97-a7be-a2d3aedce437': '/images/products/3a1fba5a-017d-4b97-a7be-a2d3aedce437.jpg',
    '4a0eea13-a583-4e33-9a00-cce7e4f8a03e': '/images/products/4a0eea13-a583-4e33-9a00-cce7e4f8a03e.jpg',
    'a4f1adf8-2f26-46d2-8f75-7f90df5caa07': '/images/products/a4f1adf8-2f26-46d2-8f75-7f90df5caa07.jpg',
    'd6ad46fe-740d-4a97-8ee5-c528d043b806': '/images/products/d6ad46fe-740d-4a97-8ee5-c528d043b806.jpg',
    'd1cc733a-455f-47eb-a76b-e0e86fbe7442': '/images/products/d1cc733a-455f-47eb-a76b-e0e86fbe7442.jpg',
    '682aa35e-3f62-41aa-b175-51051c3c7488': '/images/products/682aa35e-3f62-41aa-b175-51051c3c7488.jpg',
    '129db31b-be17-486f-b0fc-7e07aa11766b': '/images/products/129db31b-be17-486f-b0fc-7e07aa11766b.jpg',
    'd426f10c-2ab2-4e07-b4f6-06185437fb87': '/images/products/d426f10c-2ab2-4e07-b4f6-06185437fb87.jpg',
    '84ebede3-17db-4331-8cc9-8854abc00183': '/images/products/84ebede3-17db-4331-8cc9-8854abc00183.jpg',
    'c933940c-938c-4ba8-8ef1-91b3025cf2c7': '/images/products/c933940c-938c-4ba8-8ef1-91b3025cf2c7.jpg',
    'ed2a23f4-811a-46cd-b5ac-70f7daa4fe0b': '/images/products/ed2a23f4-811a-46cd-b5ac-70f7daa4fe0b.jpg',
    'e2398fce-d59f-4cb8-b1ec-38a2a3b64df4': '/images/products/e2398fce-d59f-4cb8-b1ec-38a2a3b64df4.jpg',
    'eca93030-83da-46e3-946a-2988a9ee2882': '/images/products/eca93030-83da-46e3-946a-2988a9ee2882.jpg',
    'b75c04ea-81da-49ac-aed1-5204f7d8d014': '/images/products/b75c04ea-81da-49ac-aed1-5204f7d8d014.jpg',
    '94790ca8-bb2e-4876-a97b-7471dd98a9e1': '/images/products/94790ca8-bb2e-4876-a97b-7471dd98a9e1.jpg',
    '941f8d2b-b572-4453-9742-54d7e04f5d22': '/images/products/941f8d2b-b572-4453-9742-54d7e04f5d22.jpg',
    '0b93e413-a29b-4794-8b89-d8b81d61a02f': '/images/products/0b93e413-a29b-4794-8b89-d8b81d61a02f.jpg',
    'bd5d48dd-42a8-4ff9-99e1-678bf98375a8': '/images/products/bd5d48dd-42a8-4ff9-99e1-678bf98375a8.jpg',
    '5decc72d-5e9a-4b95-bed8-bde7f5edff99': '/images/products/5decc72d-5e9a-4b95-bed8-bde7f5edff99.jpg',
    '819b6451-53e6-4654-ba16-387a9d1b8904': '/images/products/819b6451-53e6-4654-ba16-387a9d1b8904.jpg',
    '05e42f57-aeeb-4307-95f4-c0f59bc98c3b': '/images/products/05e42f57-aeeb-4307-95f4-c0f59bc98c3b.jpg',
    '647a98d2-dbd9-4745-a91d-4144a97435a0': '/images/products/647a98d2-dbd9-4745-a91d-4144a97435a0.jpg',
    'b3b78f7b-4869-40cf-98f5-fd4af13b6c3a': '/images/products/b3b78f7b-4869-40cf-98f5-fd4af13b6c3a.jpg',
    '68402b81-a340-40ae-a44b-11a22dc424eb': '/images/products/68402b81-a340-40ae-a44b-11a22dc424eb.jpg',
}


def resolve_product_image(product_id=None, category_name=None):
    if product_id:
        p_id_str = str(product_id).strip()
        if p_id_str in TEST_PRODUCT_IMAGE_OVERRIDES:
            return TEST_PRODUCT_IMAGE_OVERRIDES[p_id_str]
    if category_name:
        cat_key = str(category_name).strip().lower()
        return CATEGORY_IMAGE_MAPPING.get(cat_key, None)
    return None


def get_product_image_url(product_obj):
    if not product_obj:
        return None
    p_id = getattr(product_obj, 'product_id', None)
    cat_name = None
    if hasattr(product_obj, 'category') and product_obj.category:
        cat_name = getattr(product_obj.category, 'category_name', None)
    elif hasattr(product_obj, 'category_name'):
        cat_name = getattr(product_obj, 'category_name', None)
    return resolve_product_image(product_id=p_id, category_name=cat_name)



class CategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    product_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Category
        fields = [
            'category_id',
            'category_name',
            'parent_category_id',
            'description',
            'image',
            'product_count',
            'created_at'
        ]

    def get_image(self, obj):
        name = (obj.category_name or '').strip().lower()
        return CATEGORY_IMAGE_MAPPING.get(name, None)


class WarehouseStockSerializer(serializers.ModelSerializer):
    warehouse_name = serializers.CharField(source='warehouse.warehouse_name', read_only=True)
    city = serializers.CharField(source='warehouse.city', read_only=True)
    state = serializers.CharField(source='warehouse.state', read_only=True)

    class Meta:
        model = Inventory
        fields = [
            'warehouse_id',
            'warehouse_name',
            'city',
            'state',
            'stock_quantity',
            'reorder_level',
            'last_restock_date'
        ]


class ReviewDetailSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            'review_id',
            'product_id',
            'customer_id',
            'customer_name',
            'order_id',
            'rating',
            'review_text',
            'sentiment_label',
            'sentiment_score',
            'is_verified_purchase',
            'review_date'
        ]

    def get_customer_name(self, obj):
        if not obj.customer_id:
            return "Verified Buyer"
        try:
            from accounts.models import Customer
            cust = Customer.objects.filter(customer_id=obj.customer_id).first()
            if cust and cust.full_name:
                return cust.full_name
        except Exception:
            pass
        return "Verified Buyer"


class ProductListSerializer(serializers.ModelSerializer):
    category_id = serializers.CharField(source='category.category_id', read_only=True)
    category_name = serializers.CharField(source='category.category_name', read_only=True)
    manufacturer_id = serializers.CharField(source='manufacturer.manufacturer_id', read_only=True)
    manufacturer_name = serializers.CharField(source='manufacturer.manufacturer_name', read_only=True, default=None)
    in_stock = serializers.SerializerMethodField()
    total_stock = serializers.SerializerMethodField()
    rating_summary = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'product_id',
            'product_name',
            'category_id',
            'category_name',
            'manufacturer_id',
            'manufacturer_name',
            'sku',
            'description',
            'gender',
            'color',
            'size',
            'material',
            'base_price',
            'selling_price',
            'launch_date',
            'is_active',
            'in_stock',
            'total_stock',
            'rating_summary',
            'image'
        ]

    def get_total_stock(self, obj):
        # If annotated by queryset service (total_stock_annotated)
        if hasattr(obj, 'total_stock_annotated') and obj.total_stock_annotated is not None:
            return int(obj.total_stock_annotated)
        if hasattr(obj, '_prefetched_objects_cache') and 'inventory_items' in obj._prefetched_objects_cache:
            items = obj._prefetched_objects_cache['inventory_items']
            return sum(item.stock_quantity or 0 for item in items)
        try:
            return sum(item.stock_quantity or 0 for item in obj.inventory_items.all())
        except (Exception, AssertionError):
            return 0

    def get_in_stock(self, obj):
        return self.get_total_stock(obj) > 0

    def get_rating_summary(self, obj):
        try:
            if hasattr(obj, '_prefetched_objects_cache') and 'reviews' in obj._prefetched_objects_cache:
                reviews = obj._prefetched_objects_cache['reviews']
            else:
                reviews = obj.reviews.all()
            ratings = [r.rating for r in reviews if getattr(r, 'rating', None) is not None]
            count = len(ratings)
            avg = round(sum(ratings) / count, 1) if count > 0 else None
            return {'average_rating': avg, 'review_count': count}
        except Exception:
            return {'average_rating': None, 'review_count': 0}

    def get_image(self, obj):
        return get_product_image_url(obj)


class ProductDetailSerializer(serializers.ModelSerializer):
    category_id = serializers.CharField(source='category.category_id', read_only=True)
    category_name = serializers.CharField(source='category.category_name', read_only=True)
    category = CategorySerializer(read_only=True)
    in_stock = serializers.SerializerMethodField()
    total_stock = serializers.SerializerMethodField()
    inventory_breakdown = serializers.SerializerMethodField()
    rating_summary = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'product_id',
            'product_name',
            'category_id',
            'category_name',
            'category',
            'manufacturer_id',
            'sku',
            'description',
            'gender',
            'color',
            'size',
            'material',
            'cost_price',
            'base_price',
            'selling_price',
            'launch_date',
            'is_active',
            'created_at',
            'updated_at',
            'in_stock',
            'total_stock',
            'inventory_breakdown',
            'rating_summary',
            'reviews',
            'image'
        ]

    def get_total_stock(self, obj):
        if hasattr(obj, 'total_stock_annotated') and obj.total_stock_annotated is not None:
            return int(obj.total_stock_annotated)
        if hasattr(obj, '_prefetched_objects_cache') and 'inventory_items' in obj._prefetched_objects_cache:
            items = obj._prefetched_objects_cache['inventory_items']
            return sum(item.stock_quantity or 0 for item in items)
        try:
            return sum(item.stock_quantity or 0 for item in obj.inventory_items.all())
        except (Exception, AssertionError):
            return 0

    def get_in_stock(self, obj):
        return self.get_total_stock(obj) > 0

    def get_inventory_breakdown(self, obj):
        if hasattr(obj, '_prefetched_objects_cache') and 'inventory_items' in obj._prefetched_objects_cache:
            items = obj._prefetched_objects_cache['inventory_items']
            return WarehouseStockSerializer(items, many=True).data
        try:
            items = obj.inventory_items.select_related('warehouse').all()
            return WarehouseStockSerializer(items, many=True).data
        except (Exception, AssertionError):
            return []

    def get_rating_summary(self, obj):
        try:
            if hasattr(obj, '_prefetched_objects_cache') and 'reviews' in obj._prefetched_objects_cache:
                reviews = obj._prefetched_objects_cache['reviews']
            else:
                reviews = obj.reviews.all()
            ratings = [r.rating for r in reviews if getattr(r, 'rating', None) is not None]
            review_count = len(ratings)
            average_rating = round(sum(ratings) / review_count, 1) if review_count > 0 else None
            return {
                'average_rating': average_rating,
                'review_count': review_count
            }
        except (Exception, AssertionError):
            return {'average_rating': None, 'review_count': 0}

    def get_reviews(self, obj):
        try:
            if hasattr(obj, '_prefetched_objects_cache') and 'reviews' in obj._prefetched_objects_cache:
                rev_list = list(obj._prefetched_objects_cache['reviews'])
            else:
                rev_list = list(obj.reviews.all())
            # Sort newest first
            rev_list.sort(key=lambda r: (r.review_date or '', r.review_id or ''), reverse=True)
            return ReviewDetailSerializer(rev_list[:50], many=True).data
        except Exception:
            return []

    def get_image(self, obj):
        return get_product_image_url(obj)


class CategoryGroupedProductsSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    products = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'category_id',
            'category_name',
            'parent_category_id',
            'description',
            'image',
            'product_count',
            'products'
        ]

    def get_image(self, obj):
        name = (obj.category_name or '').strip().lower()
        return CATEGORY_IMAGE_MAPPING.get(name, None)

    def get_products(self, obj):
        prods = obj.products.filter(is_active=True).select_related('category', 'manufacturer')
        return ProductListSerializer(prods, many=True).data

    def get_product_count(self, obj):
        return obj.products.filter(is_active=True).count()

