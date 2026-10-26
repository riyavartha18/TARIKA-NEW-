import os
import sys
import json

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from catalog.models import Product, Category
from catalog.serializers import resolve_product_image

# Footwear category
fw_cat = Category.objects.filter(category_name__iexact='Footwear').first()
cat_id = fw_cat.category_id if fw_cat else None

# Products with category 'Footwear'
fw_products = Product.objects.filter(category_id=cat_id, is_active=True)

# Also check any other active products where category_name is footwear or name indicates footwear (excluding jeans like 'bootcut jeans')
all_fw = []
for p in fw_products:
    all_fw.append({
        'id': p.product_id,
        'name': p.product_name,
        'category': p.category.category_name if p.category else 'Footwear',
        'color': p.color,
        'gender': p.gender,
        'material': p.material,
        'description': p.description,
        'current_image': resolve_product_image(p.product_id, 'Footwear')
    })

# Also check our affordable catalog items in other categories if any are footwear:
other_fw = Product.objects.filter(is_active=True).exclude(category_id=cat_id)
for p in other_fw:
    name_l = (p.product_name or '').lower()
    if any(k in name_l for k in ['sandal', 'jutti', 'mule', 'mojari', 'kolhapuri', 'sneaker', 'loafer', 'stiletto']) and not any(k in name_l for k in ['jean', 'pant', 'trouser', 'dress', 'top']):
        all_fw.append({
            'id': p.product_id,
            'name': p.product_name,
            'category': p.category.category_name if p.category else 'Footwear',
            'color': p.color,
            'gender': p.gender,
            'material': p.material,
            'description': p.description,
            'current_image': resolve_product_image(p.product_id, p.category.category_name if p.category else None)
        })

print(f"Total footwear products to process: {len(all_fw)}")
with open('footwear_products.json', 'w') as f:
    json.dump(all_fw, f, indent=2)

print("Saved to footwear_products.json successfully.")
