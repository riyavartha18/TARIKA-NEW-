import os
import sys

# Ensure backend root is on sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import django

# Setup django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import transaction
from catalog.models import Category, Product, Manufacturer, Inventory
from accounts.models import Warehouse

# 19 curated affordable products
AFFORDABLE_PRODUCTS = [
    {
        'product_id': '8f000001-0000-4000-8000-000000000001',
        'sku': 'TAR-BUD-TOP-001',
        'product_name': 'Dusty Rose Ribbed Crop Top',
        'category_id': 'e5155fdd-f901-415b-be04-2e11b1d4a06f',  # Tops
        'selling_price': 199,
        'base_price': 399,
        'cost_price': 90,
        'color': 'Pink',
        'gender': 'Women',
        'size': 'M',
        'material': 'Cotton',
        'description': 'Soft ribbed cotton knit top with short sleeves in dusty rose. Casual everyday staple.',
        'occasion': 'Casual',
        'style': 'Minimal',
    },
    {
        'product_id': '8f000001-0000-4000-8000-000000000002',
        'sku': 'TAR-BUD-TEE-002',
        'product_name': 'Classic White Relaxed Crew Tee',
        'category_id': '0c94d2ca-460c-43e8-8935-27f85322e715',  # T-Shirts
        'selling_price': 179,
        'base_price': 349,
        'cost_price': 80,
        'color': 'White',
        'gender': 'Women',
        'size': 'M',
        'material': 'Cotton',
        'description': 'Breathable pure combed cotton crew neck t-shirt in crisp white. Essential college wardrobe piece.',
        'occasion': 'College',
        'style': 'Streetwear',
    },
    {
        'product_id': '8f000001-0000-4000-8000-000000000003',
        'sku': 'TAR-BUD-TOP-003',
        'product_name': 'Sage Green Ribbed Knit Top',
        'category_id': 'e5155fdd-f901-415b-be04-2e11b1d4a06f',  # Tops
        'selling_price': 219,
        'base_price': 429,
        'cost_price': 95,
        'color': 'Green',
        'gender': 'Women',
        'size': 'S',
        'material': 'Viscose',
        'description': 'Earthy sage green fine-ribbed round-neck top with ribbed cuffs. Contemporary chic style.',
        'occasion': 'Casual',
        'style': 'Chic',
    },
    {
        'product_id': '8f000001-0000-4000-8000-000000000004',
        'sku': 'TAR-BUD-TOP-004',
        'product_name': 'Black Square-Neck Fitted Top',
        'category_id': 'e5155fdd-f901-415b-be04-2e11b1d4a06f',  # Tops
        'selling_price': 249,
        'base_price': 499,
        'cost_price': 110,
        'color': 'Black',
        'gender': 'Women',
        'size': 'M',
        'material': 'Cotton Blend',
        'description': 'Sophisticated square-neck fitted full-sleeve top in solid black. Versatile for casual chic and evenings.',
        'occasion': 'Party',
        'style': 'Chic',
    },
    {
        'product_id': '8f000001-0000-4000-8000-000000000005',
        'sku': 'TAR-BUD-KRT-005',
        'product_name': 'Mustard Floral Printed Straight Kurti',
        'category_id': 'f8d9aa85-0657-4644-ba43-c39f910234e0',  # Kurtis
        'selling_price': 299,
        'base_price': 599,
        'cost_price': 130,
        'color': 'Mustard',
        'gender': 'Women',
        'size': 'M',
        'material': 'Cotton',
        'description': 'Traditional floral printed cotton straight kurti in bright marigold mustard with side slits.',
        'occasion': 'College',
        'style': 'Traditional',
    },
    {
        'product_id': '8f000001-0000-4000-8000-000000000006',
        'sku': 'TAR-BUD-KRT-006',
        'product_name': 'Powder Blue Embroidered Kurti',
        'category_id': 'f8d9aa85-0657-4644-ba43-c39f910234e0',  # Kurtis
        'selling_price': 329,
        'base_price': 649,
        'cost_price': 140,
        'color': 'Sky Blue',
        'gender': 'Women',
        'size': 'L',
        'material': 'Chanderi Cotton',
        'description': 'Serene powder blue straight kurti with delicate white threadwork embroidery. Festive and formal elegance.',
        'occasion': 'Festive',
        'style': 'Traditional',
    },
    {
        'product_id': '8f000001-0000-4000-8000-000000000007',
        'sku': 'TAR-BUD-KRT-007',
        'product_name': 'Indigo Handblock Short Peplum Tunic',
        'category_id': 'f8d9aa85-0657-4644-ba43-c39f910234e0',  # Kurtis
        'selling_price': 279,
        'base_price': 549,
        'cost_price': 120,
        'color': 'Navy Blue',
        'gender': 'Women',
        'size': 'M',
        'material': 'Cotton',
        'description': 'Indigo handblock printed short peplum kurti tunic. The quintessential Indo-Western fusion piece.',
        'occasion': 'College',
        'style': 'Chic',
    },
    {
        'product_id': '8f000001-0000-4000-8000-000000000008',
        'sku': 'TAR-BUD-TRS-008',
        'product_name': 'Beige Tailored Wide-Leg Trousers',
        'category_id': 'a323ea55-2482-4a26-b6ab-bac7ab3c891e',  # Trousers
        'selling_price': 399,
        'base_price': 799,
        'cost_price': 180,
        'color': 'Beige',
        'gender': 'Women',
        'size': '28',
        'material': 'Cotton Twill',
        'description': 'High-waisted tailored wide-leg trousers in warm beige. Crisp front pleats, modern minimalist aesthetic.',
        'occasion': 'Formal',
        'style': 'Minimal',
    },
    {
        'product_id': '8f000001-0000-4000-8000-000000000009',
        'sku': 'TAR-BUD-SKT-009',
        'product_name': 'Black Flared Cotton A-Line Skirt',
        'category_id': '2f77945f-03c5-440b-a251-1ca092ec19de',  # Bottom Wear
        'selling_price': 349,
        'base_price': 699,
        'cost_price': 150,
        'color': 'Black',
        'gender': 'Women',
        'size': 'M',
        'material': 'Cotton',
        'description': 'Flattering high-waisted flared A-line midi skirt with elasticated rear waistband in midnight black.',
        'occasion': 'Casual',
        'style': 'Chic',
    },
    {
        'product_id': '8f000001-0000-4000-8000-000000000010',
        'sku': 'TAR-BUD-PLZ-010',
        'product_name': 'Off-White Flared Rayon Palazzo',
        'category_id': '2f77945f-03c5-440b-a251-1ca092ec19de',  # Bottom Wear
        'selling_price': 299,
        'base_price': 599,
        'cost_price': 130,
        'color': 'Off-White',
        'gender': 'Women',
        'size': 'Free Size',
        'material': 'Rayon',
        'description': 'Breezy off-white flared rayon palazzo with graceful flow. Pairs seamlessly with any kurti or ethnic top.',
        'occasion': 'Casual',
        'style': 'Traditional',
    },
    {
        'product_id': '8f000001-0000-4000-8000-000000000011',
        'sku': 'TAR-BUD-CHN-011',
        'product_name': 'Olive Green Ankle Tapered Chinos',
        'category_id': 'a323ea55-2482-4a26-b6ab-bac7ab3c891e',  # Trousers
        'selling_price': 369,
        'base_price': 749,
        'cost_price': 160,
        'color': 'Olive',
        'gender': 'Women',
        'size': '30',
        'material': 'Cotton',
        'description': 'Ankle-length tapered cotton chinos in military olive green. Comfortable casual and college staple.',
        'occasion': 'College',
        'style': 'Streetwear',
    },
    {
        'product_id': '8f000001-0000-4000-8000-000000000012',
        'sku': 'TAR-BUD-DRS-012',
        'product_name': 'Sky Blue Floral Tiered Sundress',
        'category_id': '47f429fb-bc65-48d1-8dd0-f85bac9ad00b',  # Dresses
        'selling_price': 469,
        'base_price': 899,
        'cost_price': 200,
        'color': 'Sky Blue',
        'gender': 'Women',
        'size': 'M',
        'material': 'Cotton',
        'description': 'Delicate floral printed tiered A-line cotton sundress in sky blue with sweetheart neckline.',
        'occasion': 'Casual',
        'style': 'Chic',
    },
    {
        'product_id': '8f000001-0000-4000-8000-000000000013',
        'sku': 'TAR-BUD-DRS-013',
        'product_name': 'Terracotta Smocked Fit-and-Flare Dress',
        'category_id': '47f429fb-bc65-48d1-8dd0-f85bac9ad00b',  # Dresses
        'selling_price': 499,
        'base_price': 999,
        'cost_price': 210,
        'color': 'Rust',
        'gender': 'Women',
        'size': 'L',
        'material': 'Cotton Slub',
        'description': 'Rich terracotta rust smocked bodice midi dress with puffed sleeves. Elegant boho charm.',
        'occasion': 'Party',
        'style': 'Elegant',
    },
    {
        'product_id': '8f000001-0000-4000-8000-000000000014',
        'sku': 'TAR-BUD-FTW-014',
        'product_name': 'Tan Strappy Vegan Leather Flat Sandals',
        'category_id': '0951c9d1-81c0-496e-9279-3b8012fdc10a',  # Footwear
        'selling_price': 239,
        'base_price': 499,
        'cost_price': 100,
        'color': 'Tan',
        'gender': 'Women',
        'size': '38',
        'material': 'Synthetic Leather',
        'description': 'Comfortable cushioned tan vegan leather flat sandals with crossover strappy silhouette.',
        'occasion': 'Casual',
        'style': 'Minimal',
    },
    {
        'product_id': '8f000001-0000-4000-8000-000000000015',
        'sku': 'TAR-BUD-FTW-015',
        'product_name': 'Minimalist White Slip-On Mules',
        'category_id': '0951c9d1-81c0-496e-9279-3b8012fdc10a',  # Footwear
        'selling_price': 249,
        'base_price': 529,
        'cost_price': 105,
        'color': 'White',
        'gender': 'Women',
        'size': '38',
        'material': 'Faux Leather',
        'description': 'Pointed toe flat slip-on mules in clean ivory white. Sleek minimal footwear for western and formal outfits.',
        'occasion': 'College',
        'style': 'Minimal',
    },
    {
        'product_id': '8f000001-0000-4000-8000-000000000016',
        'sku': 'TAR-BUD-FTW-016',
        'product_name': 'Embroidered Marigold Mojari Juttis',
        'category_id': '0951c9d1-81c0-496e-9279-3b8012fdc10a',  # Footwear
        'selling_price': 279,
        'base_price': 599,
        'cost_price': 120,
        'color': 'Mustard',
        'gender': 'Women',
        'size': '38',
        'material': 'Silk Brocade',
        'description': 'Authentic Rajasthani hand-embroidered mojari juttis in festive marigold mustard yellow.',
        'occasion': 'Festive',
        'style': 'Traditional',
    },
    {
        'product_id': '8f000001-0000-4000-8000-000000000017',
        'sku': 'TAR-BUD-BAG-017',
        'product_name': 'Natural Canvas Mini Shopper Tote',
        'category_id': '27274ba6-698f-4499-9be3-7aedd5079cb9',  # Handbags
        'selling_price': 189,
        'base_price': 399,
        'cost_price': 80,
        'color': 'Off-White',
        'gender': 'Women',
        'size': 'Standard',
        'material': 'Canvas',
        'description': 'Eco-friendly sturdy cotton canvas mini tote with dual handles. Everyday college and casual companion.',
        'occasion': 'College',
        'style': 'Streetwear',
    },
    {
        'product_id': '8f000001-0000-4000-8000-000000000018',
        'sku': 'TAR-BUD-ACC-018',
        'product_name': 'Dainty Layered Gold Pendant Necklace',
        'category_id': 'bea121c3-2bba-4f9a-b121-bbe0ed160827',  # Accessories
        'selling_price': 89,
        'base_price': 199,
        'cost_price': 35,
        'color': 'Gold',
        'gender': 'Women',
        'size': 'Free Size',
        'material': 'Brass Alloy',
        'description': 'Minimalist double-strand gold-toned chain with geometric coin pendant. Chic daily styling accent.',
        'occasion': 'Casual',
        'style': 'Minimal',
    },
    {
        'product_id': '8f000001-0000-4000-8000-000000000019',
        'sku': 'TAR-BUD-ACC-019',
        'product_name': 'Traditional Oxidised Silver Jhumkas',
        'category_id': 'bea121c3-2bba-4f9a-b121-bbe0ed160827',  # Accessories
        'selling_price': 79,
        'base_price': 189,
        'cost_price': 30,
        'color': 'Silver',
        'gender': 'Women',
        'size': 'Free Size',
        'material': 'German Silver',
        'description': 'Intricately carved tribal oxidised silver dome jhumkas with hanging bell beads. Authentic ethnic accent.',
        'occasion': 'Festive',
        'style': 'Traditional',
    },
]

def run_seed(dry_run=False):
    print("=" * 60)
    print(f"AFFORDABLE CATALOG SEED RUNNER (Dry Run: {dry_run})")
    print("=" * 60)

    # 1. Verify manufacturer & warehouse
    manufacturer = Manufacturer.objects.first()
    if not manufacturer:
        print("[FAIL] No manufacturer found in DB!")
        return False
    print(f"[OK] Using Manufacturer: {manufacturer.manufacturer_name} ({manufacturer.manufacturer_id})")

    warehouse = Warehouse.objects.filter(warehouse_id='9ac8b56f-fc26-44a5-b3cb-42b843844d6a').first()
    if not warehouse:
        warehouse = Warehouse.objects.first()
    if not warehouse:
        print("[FAIL] No warehouse found in DB!")
        return False
    print(f"[OK] Using Warehouse: {warehouse.warehouse_name} ({warehouse.warehouse_id})")

    # 2. Check collisions
    prod_ids = [p['product_id'] for p in AFFORDABLE_PRODUCTS]
    skus = [p['sku'] for p in AFFORDABLE_PRODUCTS]

    existing_ids = set(Product.objects.filter(product_id__in=prod_ids).values_list('product_id', flat=True))
    existing_skus = set(Product.objects.filter(sku__in=skus).values_list('sku', flat=True))

    if existing_ids:
        print(f"[INFO] Found {len(existing_ids)} existing product IDs (will be skipped/upserted safely): {existing_ids}")
    if existing_skus:
        print(f"[INFO] Found {len(existing_skus)} existing SKUs: {existing_skus}")

    # 3. Check category mappings
    for p in AFFORDABLE_PRODUCTS:
        cat = Category.objects.filter(category_id=p['category_id']).first()
        if not cat:
            print(f"[FAIL] Category ID {p['category_id']} for product '{p['product_name']}' not found!")
            return False

    print(f"[OK] All {len(AFFORDABLE_PRODUCTS)} products have valid category mappings.")

    if dry_run:
        print("\n[DRY RUN COMPLETE] Pre-flight checks passed successfully.")
        return True

    # 4. Insert records atomically
    inserted_products = 0
    updated_products = 0
    created_inventory = 0

    with transaction.atomic():
        for p in AFFORDABLE_PRODUCTS:
            cat = Category.objects.get(category_id=p['category_id'])
            prod, created = Product.objects.get_or_create(
                product_id=p['product_id'],
                defaults={
                    'sku': p['sku'],
                    'product_name': p['product_name'],
                    'category': cat,
                    'manufacturer': manufacturer,
                    'selling_price': p['selling_price'],
                    'base_price': p['base_price'],
                    'cost_price': p['cost_price'],
                    'color': p['color'],
                    'gender': p['gender'],
                    'size': p['size'],
                    'material': p['material'],
                    'description': p['description'],
                    'is_active': True,
                    'launch_date': '2026-01-15',
                }
            )

            if created:
                inserted_products += 1
            else:
                # Update details non-destructively to ensure current pricing and active state
                prod.product_name = p['product_name']
                prod.sku = p['sku']
                prod.selling_price = p['selling_price']
                prod.base_price = p['base_price']
                prod.cost_price = p['cost_price']
                prod.color = p['color']
                prod.material = p['material']
                prod.description = p['description']
                prod.is_active = True
                prod.save()
                updated_products += 1

            # Inventory record
            inv_id = f"INV-{p['sku']}"
            inv, inv_created = Inventory.objects.get_or_create(
                inventory_id=inv_id,
                defaults={
                    'product': prod,
                    'warehouse': warehouse,
                    'stock_quantity': 50,
                    'reorder_level': 10,
                    'last_restock_date': '2026-10-20',
                }
            )
            if inv_created:
                created_inventory += 1
            else:
                inv.stock_quantity = max(inv.stock_quantity or 0, 50)
                inv.save()

    print(f"\n[SUCCESS] Seed finished:")
    print(f"  Products created: {inserted_products}")
    print(f"  Products verified/updated: {updated_products}")
    print(f"  Inventory items created/verified: {len(AFFORDABLE_PRODUCTS)}")
    return True

if __name__ == '__main__':
    dry_run_mode = '--dry-run' in sys.argv
    run_seed(dry_run=dry_run_mode)
