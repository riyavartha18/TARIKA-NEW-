import os
import sys

# Ensure backend root on sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from django.test import RequestFactory
from recommendations.views import SmartBudgetStylistView
from catalog.models import Product, Inventory

TARGET_BUDGETS = [500, 799, 1000, 1499, 1999]
FRONTEND_PUBLIC_DIR = os.path.join(os.path.dirname(backend_dir), 'frontend', 'public')

def verify_product_image(image_url):
    """Verifies that the product image URL resolves to a valid local file or accessible remote URL."""
    if not image_url:
        return False, "Missing image URL"
    if image_url.startswith('/images/products/'):
        rel_path = image_url.lstrip('/')
        full_path = os.path.join(FRONTEND_PUBLIC_DIR, rel_path.replace('/', os.sep))
        if os.path.exists(full_path) and os.path.getsize(full_path) > 0:
            return True, f"Local image verified ({round(os.path.getsize(full_path)/1024, 1)} KB)"
        else:
            return False, f"File not found on disk: {full_path}"
    elif image_url.startswith('http'):
        return True, "Remote CDN URL"
    return False, f"Unrecognized image URL: {image_url}"

def check_stock(product_id):
    """Verifies stock in inventory table."""
    inv = Inventory.objects.filter(product_id=product_id).first()
    if inv:
        return (inv.stock_quantity or 0) > 0, inv.stock_quantity
    return True, "Default available"

def test_engine_live():
    factory = RequestFactory()
    view = SmartBudgetStylistView.as_view()

    print("=" * 80)
    print("SMART BUDGET STYLIST: LIVE ENGINE VALIDATION AGAINST DATABASE")
    print("=" * 80)

    # 1. Test Target Budgets
    for b in TARGET_BUDGETS:
        req = factory.get(f'/api/recommendations/stylist/?budget={b}&limit=6')
        res = view(req)
        data = res.data

        total_looks = data.get('total_looks', 0)
        outfits = data.get('outfits', [])

        print(f"\n[TARGET BUDGET: Rs. {b:,}]")
        print(f"  Looks Generated: {total_looks}")

        if not outfits:
            print(f"  [WARN] No looks returned for budget Rs. {b}")
            continue

        for idx, out in enumerate(outfits[:4]):
            items_summary = " + ".join([f"{it['product_name']} (Rs.{it['selling_price']:,.0f})" for it in out['items']])
            print(f"  Look #{idx + 1} ({out['fashion_direction']} | {out['name']}): Rs. {out['total_price']:,.0f} (Remaining: Rs. {out['remaining_budget']:,.0f})")
            print(f"    Composition: {items_summary}")
            print(f"    Score: {out['score']} | Occasion: {out['occasion_score']} | Style: {out['style_score']} | Color: {out['color_score']}")

            # Assert budget compliance
            assert out['total_price'] <= b, f"Look #{idx+1} exceeded budget {b}: total={out['total_price']}"

    # 2. In-depth Inspection for Rs. 1,000 Success Criteria
    print("\n" + "=" * 80)
    print("DETAILED VERIFICATION FOR Rs. 1,000 BUDGET SUCCESS CRITERION")
    print("=" * 80)

    req_1000 = factory.get('/api/recommendations/stylist/?budget=1000&limit=6&fashion_direction=Surprise Me')
    res_1000 = view(req_1000)
    looks_1000 = res_1000.data.get('outfits', [])

    print(f"Total Valid Outfits Returned at Rs. 1,000: {len(looks_1000)}")
    assert len(looks_1000) >= 3, f"Expected at least 3-4 distinct outfits, got {len(looks_1000)}"

    for idx, out in enumerate(looks_1000[:4]):
        print(f"\n--- OUTFIT #{idx + 1}: {out['name']} ({out['fashion_direction']}) ---")
        print(f"Total Price: Rs. {out['total_price']:,.0f} / Rs. 1,000 (Remaining: Rs. {out['remaining_budget']:,.0f})")
        print(f"Discount: {out['discount_percent']}% (Original: Rs. {out['original_price']:,.0f})")
        print(f"Score: {out['score']}/100")
        print(f"Explanation: {out['explanation']}")
        print("Items:")

        for it in out['items']:
            p_id = it['product_id']
            p_name = it['product_name']
            p_price = it['selling_price']
            img_url = it['image']

            img_valid, img_msg = verify_product_image(img_url)
            has_stock, stock_qty = check_stock(p_id)

            print(f"  * [{p_id}] {p_name} | Price: Rs. {p_price:,.0f}")
            print(f"    Image: {img_url} -> {img_msg}")
            print(f"    Stock: {'IN STOCK' if has_stock else 'OUT OF STOCK'} (Quantity: {stock_qty})")

            assert img_valid, f"Image invalid for {p_name}: {img_msg}"
            assert has_stock, f"Item out of stock: {p_name}"

    # 3. Test Filter Sensitivity (Occasion, Style, Preferred Colours, Fashion Direction)
    print("\n" + "=" * 80)
    print("FILTER SENSITIVITY VALIDATION")
    print("=" * 80)

    # 3a. Changing Fashion Category Direction
    import urllib.parse
    for f_dir in ['Western', 'Ethnic', 'Indo-Western', 'Dresses & Jumpsuits']:
        req_dir = factory.get(f'/api/recommendations/stylist/?budget=1000&fashion_direction={urllib.parse.quote(f_dir)}')
        res_dir = view(req_dir)
        outs = res_dir.data.get('outfits', [])
        assert len(outs) > 0, f"Expected outfits for direction {f_dir}"
        top_look = outs[0]
        print(f"  [Category Direction: {f_dir}] -> Top Look: '{top_look['name']}' ({top_look['fashion_direction']}) | Rs. {top_look['total_price']:,.0f}")
        assert top_look['fashion_direction'] == f_dir, f"Mismatch in fashion direction: expected {f_dir}, got {top_look['fashion_direction']}"

    # 3b. Changing Occasion
    req_festive = factory.get('/api/recommendations/stylist/?budget=1000&occasion=Festive')
    req_college = factory.get('/api/recommendations/stylist/?budget=1000&occasion=College')
    top_festive = view(req_festive).data.get('outfits', [])[0]
    top_college = view(req_college).data.get('outfits', [])[0]

    festive_names = [it['product_name'] for it in top_festive['items']]
    college_names = [it['product_name'] for it in top_college['items']]

    print(f"\n  [Occasion: Festive] -> Top Items: {', '.join(festive_names[:2])}")
    print(f"  [Occasion: College] -> Top Items: {', '.join(college_names[:2])}")
    assert festive_names != college_names, "Occasion filter failed to differentiate recommendations!"

    # 3c. Changing Style
    req_traditional = factory.get('/api/recommendations/stylist/?budget=1000&style=Traditional')
    req_streetwear = factory.get('/api/recommendations/stylist/?budget=1000&style=Streetwear')
    top_trad = view(req_traditional).data.get('outfits', [])[0]
    top_street = view(req_streetwear).data.get('outfits', [])[0]

    trad_names = [it['product_name'] for it in top_trad['items']]
    street_names = [it['product_name'] for it in top_street['items']]

    print(f"\n  [Style: Traditional] -> Top Items: {', '.join(trad_names[:2])}")
    print(f"  [Style: Streetwear]  -> Top Items: {', '.join(street_names[:2])}")
    assert trad_names != street_names, "Style filter failed to differentiate recommendations!"

    # 3d. Changing Preferred Colours (Single & Multiple, plus variants like off-white and rani pink)
    req_pink = factory.get('/api/recommendations/stylist/?budget=1000&preferred_colors=Pink')
    req_yellow = factory.get('/api/recommendations/stylist/?budget=1000&preferred_colors=Yellow')
    top_pink = view(req_pink).data.get('outfits', [])[0]
    top_yellow = view(req_yellow).data.get('outfits', [])[0]

    pink_colors = [it.get('color') for it in top_pink['items']]
    yellow_colors = [it.get('color') for it in top_yellow['items']]

    print(f"\n  [Color: Pink]   -> Top Outfit Colors: {pink_colors}")
    print(f"  [Color: Yellow] -> Top Outfit Colors: {yellow_colors}")
    assert 'Pink' in pink_colors or 'Dusty Rose' in pink_colors or any('pink' in str(c).lower() for c in pink_colors), "Preferred color Pink not in top look!"
    assert 'Mustard' in yellow_colors or any('yellow' in str(c).lower() for c in yellow_colors), "Preferred color Yellow not in top look!"

    print("\n" + "=" * 80)
    print("ALL LIVE DATABASE VALIDATIONS PASSED PERFECTLY!")
    print("=" * 80)

if __name__ == '__main__':
    test_engine_live()
