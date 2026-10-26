import os
import sys
import json

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from catalog.models import Product
from catalog.serializers import TEST_PRODUCT_IMAGE_OVERRIDES

prods = Product.objects.filter(category_id='0951c9d1-81c0-496e-9279-3b8012fdc10a', is_active=True).order_by('product_name')

items = []
for p in prods:
    has_ovr = str(p.product_id) in TEST_PRODUCT_IMAGE_OVERRIDES
    items.append({
        'id': str(p.product_id),
        'name': p.product_name,
        'gender': p.gender,
        'color': p.color,
        'material': p.material,
        'description': p.description,
        'has_override': has_ovr
    })

print(f"Total active: {len(items)}")
# Print each item
for idx, it in enumerate(items, 1):
    status = "[HAS IMG]" if it['has_override'] else "[NEEDS IMG]"
    print(f"{idx:02d}. {status} {it['name']} ({it['color']} | {it['gender']}) - ID: {it['id']}")
    print(f"    Desc: {it['description']}")
