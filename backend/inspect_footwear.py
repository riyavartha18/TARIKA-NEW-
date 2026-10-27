import os
import sys

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from catalog.models import Product, Category
from django.db.models import Q

# Check categories
print("=== CATEGORIES ===")
cats = Category.objects.all()
for c in cats:
    name = c.category_name or ''
    if any(k in name.lower() for k in ['foot', 'shoe', 'sandal', 'heel', 'flat', 'boot', 'jutti', 'mule', 'loafer']):
        print(f"Cat ID: {c.category_id} | Name: {c.category_name}")

# Check products
keywords = ['shoe', 'footwear', 'sandal', 'heel', 'flat', 'sneaker', 'boot', 'jutti', 'loafer', 'mule', 'mojari', 'slipper', 'kolhapuri', 'wedge', 'pump', 'stiletto', 'oxford', 'derby', 'brogue', 'slides', 'flip-flop', 'espadrille']
query = Q(category__category_name__icontains='footwear') | Q(category__category_name__icontains='shoe')
for kw in keywords:
    query |= Q(product_name__icontains=kw)

products = Product.objects.filter(query, is_active=True).select_related('category')
print(f"\n=== MATCHING FOOTWEAR PRODUCTS ({products.count()}) ===")
from catalog.serializers import resolve_product_image

for p in products:
    img = resolve_product_image(p.product_id, p.category.category_name if p.category else None)
    print(f"ID: {p.product_id}")
    print(f"  Name: {p.product_name}")
    print(f"  Category: {p.category.category_name if p.category else 'None'}")
    print(f"  Resolved Image: {img}")
    print(f"  Color: {p.color} | Material: {p.material} | Gender: {p.gender}")
    print(f"  Description: {p.description}")
    print("-" * 50)
