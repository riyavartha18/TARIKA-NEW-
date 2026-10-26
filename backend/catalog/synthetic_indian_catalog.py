"""
Synthetic Indian Fashion Catalog Definitions & Validation Tool
TARIKA Fashion Retail

This module defines approximately 115 curated Indian fashion items targeting
genuine catalogue gaps (Trousers, T-Shirts, Ethnic Bottoms, Juttis/Mojaris,
Traditional Jewellery, Potli Bags, and Handloom Dupattas).

Safety Design:
  1. Deterministic UUIDv5 identifiers (derived from SKU + fixed namespace).
  2. Strict SKU uniqueness with recognizable prefix 'SYN-IND-'.
  3. Pre-insert conflict validation against existing live products and SKUs.
  4. Generates a reproducible manifest of exact IDs before any write.
  5. Dry-run capability: inspect all inserts without touching the database.
"""

import uuid

# Fixed deterministic namespace for TARIKA synthetic records
TARIKA_SYNTHETIC_NAMESPACE = uuid.UUID('8f9c1b4e-7d2a-4f6c-8a1e-3b5c7d9e0f2a')

# Verified existing Category IDs from Supabase DB:
CAT_TSHIRTS = '0c94d2ca-460c-43e8-8935-27f85322e715'    # T-Shirts (currently 0 prods)
CAT_TROUSERS = 'a323ea55-2482-4a26-b6ab-bac7ab3c891e'   # Trousers (currently 0 prods)
CAT_BOTTOM_WEAR = '2f77945f-03c5-440b-a251-1ca092ec19de'# Bottom Wear (Palazzos, Shararas, Dhotis)
CAT_FOOTWEAR = '0951c9d1-81c0-496e-9279-3b8012fdc10a'   # Footwear (Juttis, Mojaris, Kolhapuris)
CAT_ACCESSORIES = 'bea121c3-2bba-4f9a-b121-bbe0ed160827'# Accessories (Jhumkas, Kundan, Bangles)
CAT_HANDBAGS = '27274ba6-698f-4499-9be3-7aedd5079cb9'   # Handbags (Potli Bags, Clutches)
CAT_ETHNIC_WEAR = '77d90e8d-d31e-421a-a0fa-0f0e8472ae3b'# Ethnic Wear (Dupattas, Stoles)

# Verified existing Manufacturer IDs:
MFG_RAJWADA = '56ea65bf-38ca-45f2-a945-b12ef8d13620'    # Rajwada Fabrics Ltd
MFG_COROMANDEL = 'fecd7107-0e34-4d52-b47f-fc0ee02b3edf' # Coromandel Clothing Co.
MFG_BRAHMAPUTRA = '4b8ddf6a-af97-4615-a26d-014abc502128'# Brahmaputra Apparel Works
MFG_COASTAL = '8ee1ea2f-dd3e-4e28-8d19-7618c6ef63b2'    # Coastal Cotton Co.
MFG_KAVERI = '4f12abe2-da34-4014-9c86-56f8aa3f200f'     # Kaveri Knitwear Ltd
MFG_MALWA = 'cde8236d-2418-4ba0-baff-6a298224e430'      # Malwa Fashion House

# Default warehouse for stock allocation:
WH_BHIWANDI = '9ac8b56f-fc26-44a5-b3cb-42b843844d6a'   # West Zone Fulfillment Center

RAW_SYNTHETIC_ITEMS = [
    # -------------------------------------------------------------
    # 1. T-SHIRTS (Category: T-Shirts) - 20 items (College & Casual)
    # -------------------------------------------------------------
    {
        'sku': 'SYN-IND-TSH-001', 'name': 'Oversized Khadi Cotton Graphic Tee',
        'category_id': CAT_TSHIRTS, 'category_name': 'T-Shirts', 'mfg_id': MFG_COASTAL,
        'gender': 'unisex', 'color': 'Off-White', 'size': 'L', 'material': 'Cotton',
        'cost_price': 350, 'base_price': 899, 'selling_price': 699,
        'description': 'Breathable slub khadi cotton oversized tee with minimalist desi typography motif. Perfect for campus everyday wear.',
        'occasion': 'College', 'style_tag': 'Streetwear', 'season': 'Summer', 'fit': 'Oversized', 'stock': 85
    },
    {
        'sku': 'SYN-IND-TSH-002', 'name': 'Block Printed Indigo Crew T-Shirt',
        'category_id': CAT_TSHIRTS, 'category_name': 'T-Shirts', 'mfg_id': MFG_RAJWADA,
        'gender': 'men', 'color': 'Navy Blue', 'size': 'M', 'material': 'Cotton',
        'cost_price': 400, 'base_price': 999, 'selling_price': 799,
        'description': 'Handcrafted Dabu block print artisan tee dyed in natural indigo. Soft pre-shrunk combed cotton.',
        'occasion': 'Casual', 'style_tag': 'Indo-Western', 'season': 'All Season', 'fit': 'Regular', 'stock': 70
    },
    {
        'sku': 'SYN-IND-TSH-003', 'name': 'Kalamkari Patchwork Pocket T-Shirt',
        'category_id': CAT_TSHIRTS, 'category_name': 'T-Shirts', 'mfg_id': MFG_COROMANDEL,
        'gender': 'women', 'color': 'Maroon', 'size': 'S', 'material': 'Cotton',
        'cost_price': 380, 'base_price': 899, 'selling_price': 749,
        'description': 'Premium jersey cotton tee featuring an authentic Andhra Kalamkari peacock art patch pocket.',
        'occasion': 'College', 'style_tag': 'Bohemian', 'season': 'All Season', 'fit': 'Regular', 'stock': 65
    },
    {
        'sku': 'SYN-IND-TSH-004', 'name': 'Solid Olive Combed Cotton Crew Neck',
        'category_id': CAT_TSHIRTS, 'category_name': 'T-Shirts', 'mfg_id': MFG_KAVERI,
        'gender': 'men', 'color': 'Olive', 'size': 'L', 'material': 'Cotton',
        'cost_price': 300, 'base_price': 799, 'selling_price': 599,
        'description': 'Super-soft 100% bio-washed cotton essential tee in versatile army olive. Ribbed crew collar.',
        'occasion': 'Casual', 'style_tag': 'Minimalist', 'season': 'All Season', 'fit': 'Slim', 'stock': 90
    },
    {
        'sku': 'SYN-IND-TSH-005', 'name': 'Mustard Yellow Henna Motif Crop Tee',
        'category_id': CAT_TSHIRTS, 'category_name': 'T-Shirts', 'mfg_id': MFG_MALWA,
        'gender': 'women', 'color': 'Mustard', 'size': 'M', 'material': 'Cotton',
        'cost_price': 320, 'base_price': 799, 'selling_price': 649,
        'description': 'Vibrant mustard cropped silhouette tee with delicate gold foil mandala print across the back.',
        'occasion': 'College', 'style_tag': 'Indo-Western', 'season': 'Summer', 'fit': 'Relaxed', 'stock': 80
    },
    {
        'sku': 'SYN-IND-TSH-006', 'name': 'Charcoal Melange Athleisure T-Shirt',
        'category_id': CAT_TSHIRTS, 'category_name': 'T-Shirts', 'mfg_id': MFG_KAVERI,
        'gender': 'men', 'color': 'Charcoal', 'size': 'XL', 'material': 'Blended',
        'cost_price': 340, 'base_price': 849, 'selling_price': 699,
        'description': 'Stretch-blend performance heather grey tee with moisture-wicking weave for campus and active commutes.',
        'occasion': 'Casual', 'style_tag': 'Streetwear', 'season': 'All Season', 'fit': 'Slim', 'stock': 75
    },
    {
        'sku': 'SYN-IND-TSH-007', 'name': 'Embroidered Lotus Pale Pink T-Shirt',
        'category_id': CAT_TSHIRTS, 'category_name': 'T-Shirts', 'mfg_id': MFG_COROMANDEL,
        'gender': 'women', 'color': 'Pink', 'size': 'S', 'material': 'Cotton',
        'cost_price': 360, 'base_price': 899, 'selling_price': 720,
        'description': 'Pastel blush pink tee with delicate silk-thread hand-embroidered lotus bloom on left chest.',
        'occasion': 'College', 'style_tag': 'Minimalist', 'season': 'Summer', 'fit': 'Regular', 'stock': 60
    },
    {
        'sku': 'SYN-IND-TSH-008', 'name': 'Ikat Trim Ribbed Collar T-Shirt',
        'category_id': CAT_TSHIRTS, 'category_name': 'T-Shirts', 'mfg_id': MFG_RAJWADA,
        'gender': 'men', 'color': 'White', 'size': 'M', 'material': 'Cotton',
        'cost_price': 390, 'base_price': 949, 'selling_price': 799,
        'description': 'Crisp white round-neck tee accentuated with handwoven Pochampally Ikat fabric tape along neck and sleeves.',
        'occasion': 'Casual', 'style_tag': 'Indo-Western', 'season': 'All Season', 'fit': 'Regular', 'stock': 80
    },
    {
        'sku': 'SYN-IND-TSH-009', 'name': 'Rust Ochre Relaxed Drop-Shoulder Tee',
        'category_id': CAT_TSHIRTS, 'category_name': 'T-Shirts', 'mfg_id': MFG_COASTAL,
        'gender': 'women', 'color': 'Rust', 'size': 'L', 'material': 'Cotton',
        'cost_price': 350, 'base_price': 899, 'selling_price': 699,
        'description': 'Earthy terracotta rust oversized cotton tee with raw edge cuffs and relaxed drape for effortless pairing.',
        'occasion': 'College', 'style_tag': 'Bohemian', 'season': 'All Season', 'fit': 'Oversized', 'stock': 70
    },
    {
        'sku': 'SYN-IND-TSH-010', 'name': 'Royal Blue Classic Supima Cotton Tee',
        'category_id': CAT_TSHIRTS, 'category_name': 'T-Shirts', 'mfg_id': MFG_KAVERI,
        'gender': 'men', 'color': 'Royal Blue', 'size': 'L', 'material': 'Cotton',
        'cost_price': 450, 'base_price': 1199, 'selling_price': 899,
        'description': 'Heavyweight 220 GSM long-staple cotton tee in deep royal blue with smooth silken hand feel.',
        'occasion': 'Casual', 'style_tag': 'Minimalist', 'season': 'All Season', 'fit': 'Regular', 'stock': 65
    },
    {
        'sku': 'SYN-IND-TSH-011', 'name': 'Ajrakh Geometric Printed Cotton Tee',
        'category_id': CAT_TSHIRTS, 'category_name': 'T-Shirts', 'mfg_id': MFG_RAJWADA,
        'gender': 'women', 'color': 'Wine', 'size': 'M', 'material': 'Cotton',
        'cost_price': 420, 'base_price': 1049, 'selling_price': 849,
        'description': 'Kutch Ajrakh star print graphic center panel on rich wine red slub knit cotton fabric.',
        'occasion': 'Casual', 'style_tag': 'Indo-Western', 'season': 'All Season', 'fit': 'Regular', 'stock': 55
    },
    {
        'sku': 'SYN-IND-TSH-012', 'name': 'Sky Blue Linen-Blend Breathable Tee',
        'category_id': CAT_TSHIRTS, 'category_name': 'T-Shirts', 'mfg_id': MFG_COASTAL,
        'gender': 'men', 'color': 'Sky Blue', 'size': 'M', 'material': 'Linen',
        'cost_price': 480, 'base_price': 1299, 'selling_price': 999,
        'description': 'Airy linen-cotton hybrid knit tee crafted for humid Indian summers. Natural slub texture.',
        'occasion': 'Casual', 'style_tag': 'Smart Casual', 'season': 'Summer', 'fit': 'Relaxed', 'stock': 60
    },
    {
        'sku': 'SYN-IND-TSH-013', 'name': 'Black & Gold Foil Elephant Graphic Tee',
        'category_id': CAT_TSHIRTS, 'category_name': 'T-Shirts', 'mfg_id': MFG_MALWA,
        'gender': 'unisex', 'color': 'Black', 'size': 'L', 'material': 'Cotton',
        'cost_price': 380, 'base_price': 999, 'selling_price': 799,
        'description': 'Jet black bio-wash tee with lustrous micro-foil royal caparisoned elephant art print.',
        'occasion': 'Party', 'style_tag': 'Streetwear', 'season': 'All Season', 'fit': 'Regular', 'stock': 85
    },
    {
        'sku': 'SYN-IND-TSH-014', 'name': 'Mint Green Pastel Ribbed Henley Tee',
        'category_id': CAT_TSHIRTS, 'category_name': 'T-Shirts', 'mfg_id': MFG_KAVERI,
        'gender': 'men', 'color': 'Mint Green', 'size': 'M', 'material': 'Cotton',
        'cost_price': 410, 'base_price': 1099, 'selling_price': 849,
        'description': 'Three-button placket henley tee in soothing mint sage green. Wooden coconut shell buttons.',
        'occasion': 'College', 'style_tag': 'Smart Casual', 'season': 'Summer', 'fit': 'Slim', 'stock': 70
    },
    {
        'sku': 'SYN-IND-TSH-015', 'name': 'Teal Mandana Tribal Print Boxy Tee',
        'category_id': CAT_TSHIRTS, 'category_name': 'T-Shirts', 'mfg_id': MFG_RAJWADA,
        'gender': 'women', 'color': 'Teal', 'size': 'S', 'material': 'Cotton',
        'cost_price': 370, 'base_price': 899, 'selling_price': 729,
        'description': 'Deep teal boxy crop t-shirt inspired by Rajasthan folk wall art with white chalk lines.',
        'occasion': 'College', 'style_tag': 'Bohemian', 'season': 'All Season', 'fit': 'Relaxed', 'stock': 75
    },
    {
        'sku': 'SYN-IND-TSH-016', 'name': 'Beige Waffle Knit Thermal Long Tee',
        'category_id': CAT_TSHIRTS, 'category_name': 'T-Shirts', 'mfg_id': MFG_BRAHMAPUTRA,
        'gender': 'men', 'color': 'Beige', 'size': 'L', 'material': 'Cotton',
        'cost_price': 460, 'base_price': 1199, 'selling_price': 899,
        'description': 'Textured honeycomb waffle cotton tee in warm sandstone beige. Excellent for lightweight winter layering.',
        'occasion': 'Casual', 'style_tag': 'Minimalist', 'season': 'Winter', 'fit': 'Regular', 'stock': 50
    },
    {
        'sku': 'SYN-IND-TSH-017', 'name': 'Lavender Floral Slogan Cotton Tee',
        'category_id': CAT_TSHIRTS, 'category_name': 'T-Shirts', 'mfg_id': MFG_COROMANDEL,
        'gender': 'women', 'color': 'Lavender', 'size': 'M', 'material': 'Cotton',
        'cost_price': 340, 'base_price': 849, 'selling_price': 679,
        'description': 'Soft lilac purple jersey tee with cursive embroidery and botanical wild floral artwork.',
        'occasion': 'College', 'style_tag': 'Chic', 'season': 'Summer', 'fit': 'Regular', 'stock': 65
    },
    {
        'sku': 'SYN-IND-TSH-018', 'name': 'Burgundy Embroidered Collar Polo Tee',
        'category_id': CAT_TSHIRTS, 'category_name': 'T-Shirts', 'mfg_id': MFG_KAVERI,
        'gender': 'men', 'color': 'Wine', 'size': 'L', 'material': 'Cotton',
        'cost_price': 520, 'base_price': 1399, 'selling_price': 999,
        'description': 'Structured pique cotton polo collar t-shirt in regal burgundy wine with fine gold tipping on collar.',
        'occasion': 'Formal', 'style_tag': 'Smart Casual', 'season': 'All Season', 'fit': 'Slim', 'stock': 55
    },
    {
        'sku': 'SYN-IND-TSH-019', 'name': 'Coral Ombre Dip-Dyed Cotton Tee',
        'category_id': CAT_TSHIRTS, 'category_name': 'T-Shirts', 'mfg_id': MFG_COASTAL,
        'gender': 'women', 'color': 'Coral', 'size': 'S', 'material': 'Cotton',
        'cost_price': 360, 'base_price': 899, 'selling_price': 710,
        'description': 'Hand dip-dyed sunset gradient from ivory white to warm coral peach in featherlight cotton.',
        'occasion': 'Casual', 'style_tag': 'Bohemian', 'season': 'Summer', 'fit': 'Regular', 'stock': 60
    },
    {
        'sku': 'SYN-IND-TSH-020', 'name': 'Pure White Classic V-Neck Undershirt Tee',
        'category_id': CAT_TSHIRTS, 'category_name': 'T-Shirts', 'mfg_id': MFG_KAVERI,
        'gender': 'men', 'color': 'White', 'size': 'M', 'material': 'Cotton',
        'cost_price': 280, 'base_price': 699, 'selling_price': 549,
        'description': 'Essential crisp white V-neck cotton tee. Invisible under kurtas or worn standalone over denim.',
        'occasion': 'College', 'style_tag': 'Minimalist', 'season': 'All Season', 'fit': 'Slim', 'stock': 95
    },

    # -------------------------------------------------------------
    # 2. TROUSERS (Category: Trousers) - 20 items (Formal, College, Smart Casual)
    # -------------------------------------------------------------
    {
        'sku': 'SYN-IND-TRS-001', 'name': 'Slim Fit Khaki Chino Trousers',
        'category_id': CAT_TROUSERS, 'category_name': 'Trousers', 'mfg_id': MFG_COASTAL,
        'gender': 'men', 'color': 'Beige', 'size': '32', 'material': 'Cotton',
        'cost_price': 650, 'base_price': 1899, 'selling_price': 1499,
        'description': 'Tailored flat-front stretch-twill chino trousers in versatile khaki beige. Coin pocket and horn buttons.',
        'occasion': 'Formal', 'style_tag': 'Smart Casual', 'season': 'All Season', 'fit': 'Slim', 'stock': 60
    },
    {
        'sku': 'SYN-IND-TRS-002', 'name': 'High-Waisted Charcoal Pleated Trousers',
        'category_id': CAT_TROUSERS, 'category_name': 'Trousers', 'mfg_id': MFG_MALWA,
        'gender': 'women', 'color': 'Charcoal', 'size': '28', 'material': 'Viscose',
        'cost_price': 720, 'base_price': 2199, 'selling_price': 1699,
        'description': 'Chic Parisian-inspired double-pleated tailored trousers with wide belt loops and clean tapered hem.',
        'occasion': 'Formal', 'style_tag': 'Chic', 'season': 'All Season', 'fit': 'Tailored', 'stock': 50
    },
    {
        'sku': 'SYN-IND-TRS-003', 'name': 'Navy Blue Stretch Formal Dress Pants',
        'category_id': CAT_TROUSERS, 'category_name': 'Trousers', 'mfg_id': MFG_KAVERI,
        'gender': 'men', 'color': 'Navy Blue', 'size': '34', 'material': 'Blended',
        'cost_price': 750, 'base_price': 2299, 'selling_price': 1799,
        'description': 'Wrinkle-resistant poly-viscose blend formal trousers with flexi-waistband for presentation days.',
        'occasion': 'Formal', 'style_tag': 'Smart Casual', 'season': 'All Season', 'fit': 'Slim', 'stock': 65
    },
    {
        'sku': 'SYN-IND-TRS-004', 'name': 'Olive Green Straight Cut Linen Trousers',
        'category_id': CAT_TROUSERS, 'category_name': 'Trousers', 'mfg_id': MFG_COASTAL,
        'gender': 'women', 'color': 'Olive', 'size': '30', 'material': 'Linen',
        'cost_price': 700, 'base_price': 1999, 'selling_price': 1599,
        'description': 'Breathable pure linen trousers with elasticated back waist and deep side slash pockets.',
        'occasion': 'College', 'style_tag': 'Minimalist', 'season': 'Summer', 'fit': 'Regular', 'stock': 55
    },
    {
        'sku': 'SYN-IND-TRS-005', 'name': 'Black Ankle-Length Cigarette Trousers',
        'category_id': CAT_TROUSERS, 'category_name': 'Trousers', 'mfg_id': MFG_MALWA,
        'gender': 'women', 'color': 'Black', 'size': '28', 'material': 'Cotton',
        'cost_price': 580, 'base_price': 1699, 'selling_price': 1299,
        'description': 'Sharp ankle-grazing stretch cigarette pants with side zip closure and concealed ankle slits.',
        'occasion': 'Formal', 'style_tag': 'Chic', 'season': 'All Season', 'fit': 'Slim', 'stock': 70
    },
    {
        'sku': 'SYN-IND-TRS-006', 'name': 'Grey Windowpane Check Tailored Trousers',
        'category_id': CAT_TROUSERS, 'category_name': 'Trousers', 'mfg_id': MFG_BRAHMAPUTRA,
        'gender': 'men', 'color': 'Grey', 'size': '32', 'material': 'Blended',
        'cost_price': 780, 'base_price': 2499, 'selling_price': 1899,
        'description': 'Subtle windowpane checked formal trousers with hook-and-bar clasp and pressed center crease.',
        'occasion': 'Formal', 'style_tag': 'Smart Casual', 'season': 'All Season', 'fit': 'Regular', 'stock': 45
    },
    {
        'sku': 'SYN-IND-TRS-007', 'name': 'Tan Brown Relaxed Gurkha Trousers',
        'category_id': CAT_TROUSERS, 'category_name': 'Trousers', 'mfg_id': MFG_RAJWADA,
        'gender': 'men', 'color': 'Tan', 'size': '32', 'material': 'Cotton',
        'cost_price': 800, 'base_price': 2599, 'selling_price': 1999,
        'description': 'Heritage British-Indian Gurkha trousers with double buckle waistband and military-grade cotton drill.',
        'occasion': 'College', 'style_tag': 'Indo-Western', 'season': 'All Season', 'fit': 'Relaxed', 'stock': 40
    },
    {
        'sku': 'SYN-IND-TRS-008', 'name': 'Off-White Wide Leg Flowy Trousers',
        'category_id': CAT_TROUSERS, 'category_name': 'Trousers', 'mfg_id': MFG_COROMANDEL,
        'gender': 'women', 'color': 'Off-White', 'size': '30', 'material': 'Rayon',
        'cost_price': 620, 'base_price': 1799, 'selling_price': 1399,
        'description': 'Breezy palazzo-trousers fusion in ivory modal rayon with flattering high rise and clean silhouette.',
        'occasion': 'Casual', 'style_tag': 'Contemporary', 'season': 'Summer', 'fit': 'Flared', 'stock': 60
    },
    {
        'sku': 'SYN-IND-TRS-009', 'name': 'Deep Wine Velvet Evening Trousers',
        'category_id': CAT_TROUSERS, 'category_name': 'Trousers', 'mfg_id': MFG_MALWA,
        'gender': 'women', 'color': 'Wine', 'size': '28', 'material': 'Blended',
        'cost_price': 900, 'base_price': 2999, 'selling_price': 2299,
        'description': 'Luxurious micro-velvet tailored trousers with gold satin piping along the outseams for festive evenings.',
        'occasion': 'Party', 'style_tag': 'Royal Ethnic', 'season': 'Winter', 'fit': 'Straight', 'stock': 35
    },
    {
        'sku': 'SYN-IND-TRS-010', 'name': 'Khaki 6-Pocket Utility Cargo Trousers',
        'category_id': CAT_TROUSERS, 'category_name': 'Trousers', 'mfg_id': MFG_COASTAL,
        'gender': 'men', 'color': 'Beige', 'size': '34', 'material': 'Cotton',
        'cost_price': 720, 'base_price': 2199, 'selling_price': 1649,
        'description': 'Rugged ripstop cotton cargo pants with gusseted side bellows pockets and adjustable ankle bungee cords.',
        'occasion': 'College', 'style_tag': 'Streetwear', 'season': 'All Season', 'fit': 'Relaxed', 'stock': 65
    },
    {
        'sku': 'SYN-IND-TRS-011', 'name': 'Sage Green Paperbag Waist Trousers',
        'category_id': CAT_TROUSERS, 'category_name': 'Trousers', 'mfg_id': MFG_COROMANDEL,
        'gender': 'women', 'color': 'Mint Green', 'size': '30', 'material': 'Cotton',
        'cost_price': 590, 'base_price': 1799, 'selling_price': 1349,
        'description': 'Ruffled paperbag waist trousers with detachable self-fabric tie sash and tapered ankle turn-ups.',
        'occasion': 'College', 'style_tag': 'Chic', 'season': 'Summer', 'fit': 'Regular', 'stock': 55
    },
    {
        'sku': 'SYN-IND-TRS-012', 'name': 'Charcoal Houndstooth Checked Trousers',
        'category_id': CAT_TROUSERS, 'category_name': 'Trousers', 'mfg_id': MFG_BRAHMAPUTRA,
        'gender': 'men', 'color': 'Charcoal', 'size': '32', 'material': 'Blended',
        'cost_price': 760, 'base_price': 2399, 'selling_price': 1849,
        'description': 'Micro-houndstooth pattern semi-formal trousers with crease-recovery finish and button-through rear pockets.',
        'occasion': 'Formal', 'style_tag': 'Smart Casual', 'season': 'Winter', 'fit': 'Slim', 'stock': 45
    },
    {
        'sku': 'SYN-IND-TRS-013', 'name': 'Black Flared Formal Bell-Bottom Trousers',
        'category_id': CAT_TROUSERS, 'category_name': 'Trousers', 'mfg_id': MFG_MALWA,
        'gender': 'women', 'color': 'Black', 'size': '28', 'material': 'Viscose',
        'cost_price': 680, 'base_price': 1999, 'selling_price': 1499,
        'description': 'Power-dressing flared retro trousers crafted in ponte roma knit with flattering stretch and knee seam.',
        'occasion': 'Party', 'style_tag': 'Contemporary', 'season': 'All Season', 'fit': 'Flared', 'stock': 50
    },
    {
        'sku': 'SYN-IND-TRS-014', 'name': 'Teal Blue Tailored Cropped Trousers',
        'category_id': CAT_TROUSERS, 'category_name': 'Trousers', 'mfg_id': MFG_COROMANDEL,
        'gender': 'women', 'color': 'Teal', 'size': '30', 'material': 'Cotton',
        'cost_price': 630, 'base_price': 1899, 'selling_price': 1399,
        'description': 'Jewel-toned teal structured formal trousers with ankle length and welt back pockets.',
        'occasion': 'Formal', 'style_tag': 'Smart Casual', 'season': 'All Season', 'fit': 'Slim', 'stock': 50
    },
    {
        'sku': 'SYN-IND-TRS-015', 'name': 'Mustard Yellow Straight Linen Slacks',
        'category_id': CAT_TROUSERS, 'category_name': 'Trousers', 'mfg_id': MFG_COASTAL,
        'gender': 'women', 'color': 'Mustard', 'size': '32', 'material': 'Linen',
        'cost_price': 670, 'base_price': 1999, 'selling_price': 1549,
        'description': 'Warm mustard pure linen slacks with drawstring elastic waist and clean pressed side seams.',
        'occasion': 'Casual', 'style_tag': 'Bohemian', 'season': 'Summer', 'fit': 'Regular', 'stock': 45
    },
    {
        'sku': 'SYN-IND-TRS-016', 'name': 'Dark Navy Pleated Peg-Leg Trousers',
        'category_id': CAT_TROUSERS, 'category_name': 'Trousers', 'mfg_id': MFG_BRAHMAPUTRA,
        'gender': 'men', 'color': 'Navy Blue', 'size': '34', 'material': 'Cotton',
        'cost_price': 710, 'base_price': 2099, 'selling_price': 1599,
        'description': 'Contemporary peg-leg silhouette with roomy thigh and sharp taper toward the cuff.',
        'occasion': 'College', 'style_tag': 'Streetwear', 'season': 'All Season', 'fit': 'Tailored', 'stock': 55
    },
    {
        'sku': 'SYN-IND-TRS-017', 'name': 'Burgundy Wool-Blend Winter Trousers',
        'category_id': CAT_TROUSERS, 'category_name': 'Trousers', 'mfg_id': MFG_BRAHMAPUTRA,
        'gender': 'men', 'color': 'Wine', 'size': '32', 'material': 'Wool',
        'cost_price': 850, 'base_price': 2799, 'selling_price': 2099,
        'description': 'Warm flannel wool-blend trousers in deep burgundy red for winter conferences and evening formals.',
        'occasion': 'Formal', 'style_tag': 'Smart Casual', 'season': 'Winter', 'fit': 'Regular', 'stock': 40
    },
    {
        'sku': 'SYN-IND-TRS-018', 'name': 'Rust Ochre High-Rise Slit-Hem Trousers',
        'category_id': CAT_TROUSERS, 'category_name': 'Trousers', 'mfg_id': MFG_MALWA,
        'gender': 'women', 'color': 'Rust', 'size': '28', 'material': 'Cotton',
        'cost_price': 640, 'base_price': 1899, 'selling_price': 1420,
        'description': 'Terracotta rust trousers featuring a chic 4-inch inner hem split to spotlight stylish footwear.',
        'occasion': 'Casual', 'style_tag': 'Chic', 'season': 'All Season', 'fit': 'Slim', 'stock': 50
    },
    {
        'sku': 'SYN-IND-TRS-019', 'name': 'Beige Pin-Stripe Business Trousers',
        'category_id': CAT_TROUSERS, 'category_name': 'Trousers', 'mfg_id': MFG_KAVERI,
        'gender': 'men', 'color': 'Beige', 'size': '34', 'material': 'Blended',
        'cost_price': 730, 'base_price': 2299, 'selling_price': 1749,
        'description': 'Subtle chalk pin-stripe trousers with stain-resistant nano finish for full-day boardroom comfort.',
        'occasion': 'Formal', 'style_tag': 'Smart Casual', 'season': 'All Season', 'fit': 'Regular', 'stock': 50
    },
    {
        'sku': 'SYN-IND-TRS-020', 'name': 'Pure White Wide-Leg Linen Trousers',
        'category_id': CAT_TROUSERS, 'category_name': 'Trousers', 'mfg_id': MFG_COASTAL,
        'gender': 'women', 'color': 'White', 'size': '30', 'material': 'Linen',
        'cost_price': 690, 'base_price': 2099, 'selling_price': 1599,
        'description': 'Pristine white European flax linen trousers with wide flowing palazzo legs and zip side closure.',
        'occasion': 'Casual', 'style_tag': 'Minimalist', 'season': 'Summer', 'fit': 'Flared', 'stock': 55
    },

    # -------------------------------------------------------------
    # 3. ETHNIC BOTTOMS (Palazzos, Shararas, Dhotis under Bottom Wear) - 20 items
    # -------------------------------------------------------------
    {
        'sku': 'SYN-IND-PLZ-001', 'name': 'Off-White Embroidered Chikankari Palazzo',
        'category_id': CAT_BOTTOM_WEAR, 'category_name': 'Bottom Wear', 'mfg_id': MFG_RAJWADA,
        'gender': 'women', 'color': 'Off-White', 'size': 'Free', 'material': 'Cotton',
        'cost_price': 480, 'base_price': 1399, 'selling_price': 1099,
        'description': 'Lucknowi Chikankari floral hand embroidery on pure cambric cotton with scalloped lace hem. Pairs with any kurti.',
        'occasion': 'Festive', 'style_tag': 'Traditional', 'season': 'All Season', 'fit': 'Flared', 'stock': 75
    },
    {
        'sku': 'SYN-IND-PLZ-002', 'name': 'Golden Shimmer Flared Tiered Sharara',
        'category_id': CAT_BOTTOM_WEAR, 'category_name': 'Bottom Wear', 'mfg_id': MFG_MALWA,
        'gender': 'women', 'color': 'Gold', 'size': 'M', 'material': 'Georgette',
        'cost_price': 680, 'base_price': 2199, 'selling_price': 1699,
        'description': 'Triple-tiered pleated festive sharara in flowy georgette with zari ribbon accents and golden shimmer lining.',
        'occasion': 'Festive', 'style_tag': 'Traditional', 'season': 'Festive', 'fit': 'Flared', 'stock': 60
    },
    {
        'sku': 'SYN-IND-PLZ-003', 'name': 'Maroon Silk Blend Zari Border Palazzo',
        'category_id': CAT_BOTTOM_WEAR, 'category_name': 'Bottom Wear', 'mfg_id': MFG_RAJWADA,
        'gender': 'women', 'color': 'Maroon', 'size': 'L', 'material': 'Silk',
        'cost_price': 550, 'base_price': 1699, 'selling_price': 1299,
        'description': 'Lustrous Art Silk palazzo pant in deep royal maroon finished with 2-inch temple zari weave hem.',
        'occasion': 'Festive', 'style_tag': 'Royal Ethnic', 'season': 'All Season', 'fit': 'Flared', 'stock': 65
    },
    {
        'sku': 'SYN-IND-PLZ-004', 'name': 'Black Rayon Flared Wide-Leg Palazzo',
        'category_id': CAT_BOTTOM_WEAR, 'category_name': 'Bottom Wear', 'mfg_id': MFG_COROMANDEL,
        'gender': 'women', 'color': 'Black', 'size': 'Free', 'material': 'Rayon',
        'cost_price': 380, 'base_price': 999, 'selling_price': 749,
        'description': 'Ultra-soft heavy drape viscose rayon palazzo in jet black with elastic waistband and functional pockets.',
        'occasion': 'College', 'style_tag': 'Indo-Western', 'season': 'All Season', 'fit': 'Flared', 'stock': 90
    },
    {
        'sku': 'SYN-IND-PLZ-005', 'name': 'Mustard Yellow Crinkled Cotton Dhoti Pant',
        'category_id': CAT_BOTTOM_WEAR, 'category_name': 'Bottom Wear', 'mfg_id': MFG_RAJWADA,
        'gender': 'women', 'color': 'Mustard', 'size': 'Free', 'material': 'Cotton',
        'cost_price': 440, 'base_price': 1299, 'selling_price': 999,
        'description': 'Pre-draped modern dhoti trousers in soft mulmul cotton with graceful side cowls. Pairs with short kurtis.',
        'occasion': 'Casual', 'style_tag': 'Indo-Western', 'season': 'Summer', 'fit': 'Relaxed', 'stock': 70
    },
    {
        'sku': 'SYN-IND-PLZ-006', 'name': 'Emerald Green Brocade Banarasi Cigarette Pants',
        'category_id': CAT_BOTTOM_WEAR, 'category_name': 'Bottom Wear', 'mfg_id': MFG_RAJWADA,
        'gender': 'women', 'color': 'Emerald Green', 'size': 'M', 'material': 'Silk',
        'cost_price': 720, 'base_price': 2299, 'selling_price': 1799,
        'description': 'Regal Banarasi woven floral brocade pants with side zip and ankle length. Ideal pairing for rich party tunics.',
        'occasion': 'Party', 'style_tag': 'Royal Ethnic', 'season': 'Festive', 'fit': 'Slim', 'stock': 45
    },
    {
        'sku': 'SYN-IND-PLZ-007', 'name': 'Navy Blue Chanderi Gota Patti Palazzo',
        'category_id': CAT_BOTTOM_WEAR, 'category_name': 'Bottom Wear', 'mfg_id': MFG_MALWA,
        'gender': 'women', 'color': 'Navy Blue', 'size': 'L', 'material': 'Silk',
        'cost_price': 610, 'base_price': 1899, 'selling_price': 1449,
        'description': 'Chanderi silk-cotton palazzo in deep navy adorned with gold gota patti ribbon work along the flare.',
        'occasion': 'Festive', 'style_tag': 'Traditional', 'season': 'All Season', 'fit': 'Flared', 'stock': 55
    },
    {
        'sku': 'SYN-IND-PLZ-008', 'name': 'Beige Khadi Cotton Gathered Salwar',
        'category_id': CAT_BOTTOM_WEAR, 'category_name': 'Bottom Wear', 'mfg_id': MFG_COASTAL,
        'gender': 'women', 'color': 'Beige', 'size': 'Free', 'material': 'Cotton',
        'cost_price': 400, 'base_price': 1199, 'selling_price': 899,
        'description': 'Traditional pleated Punjabi salwar in natural textured handloom khadi with comfortable drawstring waist.',
        'occasion': 'College', 'style_tag': 'Traditional', 'season': 'Summer', 'fit': 'Relaxed', 'stock': 65
    },
    {
        'sku': 'SYN-IND-PLZ-009', 'name': 'Wine Red Pleated Georgette Gharara',
        'category_id': CAT_BOTTOM_WEAR, 'category_name': 'Bottom Wear', 'mfg_id': MFG_MALWA,
        'gender': 'women', 'color': 'Wine', 'size': 'M', 'material': 'Georgette',
        'cost_price': 750, 'base_price': 2499, 'selling_price': 1899,
        'description': 'Knee-gathered Awadhi royal gharara with delicate sequin and zari lace borders in majestic wine red.',
        'occasion': 'Party', 'style_tag': 'Traditional', 'season': 'Festive', 'fit': 'Flared', 'stock': 40
    },
    {
        'sku': 'SYN-IND-PLZ-010', 'name': 'Teal Printed Cotton Straight Pants',
        'category_id': CAT_BOTTOM_WEAR, 'category_name': 'Bottom Wear', 'mfg_id': MFG_COROMANDEL,
        'gender': 'women', 'color': 'Teal', 'size': 'L', 'material': 'Cotton',
        'cost_price': 390, 'base_price': 1099, 'selling_price': 849,
        'description': 'Geometric ethnic block print ankle pants in rich teal blue. Slit hems and comfortable side pocket.',
        'occasion': 'College', 'style_tag': 'Indo-Western', 'season': 'All Season', 'fit': 'Regular', 'stock': 75
    },
    {
        'sku': 'SYN-IND-PLZ-011', 'name': 'Coral Orange Mirror-Work Border Palazzo',
        'category_id': CAT_BOTTOM_WEAR, 'category_name': 'Bottom Wear', 'mfg_id': MFG_RAJWADA,
        'gender': 'women', 'color': 'Coral', 'size': 'M', 'material': 'Rayon',
        'cost_price': 520, 'base_price': 1599, 'selling_price': 1199,
        'description': 'Festive coral rayon palazzo highlighted with authentic Gujarati foil-mirror embroidery along the hemline.',
        'occasion': 'Festive', 'style_tag': 'Traditional', 'season': 'Summer', 'fit': 'Flared', 'stock': 60
    },
    {
        'sku': 'SYN-IND-PLZ-012', 'name': 'Pure White Cotton Lycra Stretch Churidar',
        'category_id': CAT_BOTTOM_WEAR, 'category_name': 'Bottom Wear', 'mfg_id': MFG_KAVERI,
        'gender': 'women', 'color': 'White', 'size': 'Free', 'material': 'Cotton',
        'cost_price': 280, 'base_price': 699, 'selling_price': 549,
        'description': '4-way stretch 95% combed cotton churidar leggings with multiple elegant gathers at the ankle.',
        'occasion': 'College', 'style_tag': 'Traditional', 'season': 'All Season', 'fit': 'Slim', 'stock': 120
    },
    {
        'sku': 'SYN-IND-PLZ-013', 'name': 'Black Gold Gota Border Flared Palazzo',
        'category_id': CAT_BOTTOM_WEAR, 'category_name': 'Bottom Wear', 'mfg_id': MFG_MALWA,
        'gender': 'women', 'color': 'Black', 'size': 'Free', 'material': 'Rayon',
        'cost_price': 490, 'base_price': 1499, 'selling_price': 1120,
        'description': 'Dramatic circular flare palazzo pant in jet black rayon with 3 rows of gleaming gold gota ribbons.',
        'occasion': 'Party', 'style_tag': 'Indo-Western', 'season': 'All Season', 'fit': 'Flared', 'stock': 70
    },
    {
        'sku': 'SYN-IND-PLZ-014', 'name': 'Rust Orange Slub Cotton Tulip Pants',
        'category_id': CAT_BOTTOM_WEAR, 'category_name': 'Bottom Wear', 'mfg_id': MFG_COASTAL,
        'gender': 'women', 'color': 'Rust', 'size': 'M', 'material': 'Cotton',
        'cost_price': 420, 'base_price': 1249, 'selling_price': 949,
        'description': 'Overlapping tulip-petal silhouette trousers with curved front seams and delicate bead fringe.',
        'occasion': 'College', 'style_tag': 'Bohemian', 'season': 'Summer', 'fit': 'Relaxed', 'stock': 65
    },
    {
        'sku': 'SYN-IND-PLZ-015', 'name': 'Mint Green Floral Print Georgette Sharara',
        'category_id': CAT_BOTTOM_WEAR, 'category_name': 'Bottom Wear', 'mfg_id': MFG_COROMANDEL,
        'gender': 'women', 'color': 'Mint Green', 'size': 'S', 'material': 'Georgette',
        'cost_price': 630, 'base_price': 1999, 'selling_price': 1499,
        'description': 'Pastel mint green floral digital print sharara with soft santoon inner lining and wide sweeping flare.',
        'occasion': 'Festive', 'style_tag': 'Traditional', 'season': 'Summer', 'fit': 'Flared', 'stock': 50
    },
    {
        'sku': 'SYN-IND-PLZ-016', 'name': 'Men Raw Silk Cream Wedding Dhoti Pant',
        'category_id': CAT_BOTTOM_WEAR, 'category_name': 'Bottom Wear', 'mfg_id': MFG_RAJWADA,
        'gender': 'men', 'color': 'Off-White', 'size': 'Free', 'material': 'Silk',
        'cost_price': 680, 'base_price': 2199, 'selling_price': 1699,
        'description': 'Readymade stitched dhoti for men with golden kasavu border in lustrous art raw silk with drawstring waist.',
        'occasion': 'Festive', 'style_tag': 'Traditional', 'season': 'Festive', 'fit': 'Relaxed', 'stock': 45
    },
    {
        'sku': 'SYN-IND-PLZ-017', 'name': 'Men Black Stretch Churidar Pyjama',
        'category_id': CAT_BOTTOM_WEAR, 'category_name': 'Bottom Wear', 'mfg_id': MFG_KAVERI,
        'gender': 'men', 'color': 'Black', 'size': 'Free', 'material': 'Cotton',
        'cost_price': 320, 'base_price': 899, 'selling_price': 699,
        'description': 'Men tailored cotton-stretch churidar bottoms engineered to pair with long or short kurtas.',
        'occasion': 'Festive', 'style_tag': 'Traditional', 'season': 'All Season', 'fit': 'Slim', 'stock': 80
    },
    {
        'sku': 'SYN-IND-PLZ-018', 'name': 'Lavender Zari Embroidered Silk Pants',
        'category_id': CAT_BOTTOM_WEAR, 'category_name': 'Bottom Wear', 'mfg_id': MFG_MALWA,
        'gender': 'women', 'color': 'Lavender', 'size': 'M', 'material': 'Silk',
        'cost_price': 650, 'base_price': 2099, 'selling_price': 1599,
        'description': 'Modern pastel lilac chanderi silk trousers with antique silver thread embroidery along ankles.',
        'occasion': 'Party', 'style_tag': 'Chic', 'season': 'All Season', 'fit': 'Slim', 'stock': 50
    },
    {
        'sku': 'SYN-IND-PLZ-019', 'name': 'Red Raw Silk Embroidered Sharara Pants',
        'category_id': CAT_BOTTOM_WEAR, 'category_name': 'Bottom Wear', 'mfg_id': MFG_RAJWADA,
        'gender': 'women', 'color': 'Red', 'size': 'L', 'material': 'Silk',
        'cost_price': 790, 'base_price': 2599, 'selling_price': 1999,
        'description': 'Crimson red bridal raw silk sharara pants with floral kalidar panels and heavy gold resham thread work.',
        'occasion': 'Festive', 'style_tag': 'Royal Ethnic', 'season': 'Festive', 'fit': 'Flared', 'stock': 35
    },
    {
        'sku': 'SYN-IND-PLZ-020', 'name': 'Beige Linen-Cotton Casual Kurta Pants',
        'category_id': CAT_BOTTOM_WEAR, 'category_name': 'Bottom Wear', 'mfg_id': MFG_COASTAL,
        'gender': 'men', 'color': 'Beige', 'size': '32', 'material': 'Linen',
        'cost_price': 450, 'base_price': 1399, 'selling_price': 1049,
        'description': 'Straight-leg casual trousers with back elastication and front flat waistband designed for ethnic kurtas.',
        'occasion': 'College', 'style_tag': 'Smart Casual', 'season': 'Summer', 'fit': 'Regular', 'stock': 70
    },

    # -------------------------------------------------------------
    # 4. ETHNIC FOOTWEAR (Juttis, Mojaris, Kolhapuris under Footwear) - 15 items
    # -------------------------------------------------------------
    {
        'sku': 'SYN-IND-JUT-001', 'name': 'Golden Zardozi Embroidered Punjabi Jutti',
        'category_id': CAT_FOOTWEAR, 'category_name': 'Footwear', 'mfg_id': MFG_RAJWADA,
        'gender': 'women', 'color': 'Gold', 'size': '38', 'material': 'Silk',
        'cost_price': 520, 'base_price': 1699, 'selling_price': 1299,
        'description': 'Handcrafted genuine leather sole Punjabi jutti embellished with intricate gold zari, beads, and dabka work.',
        'occasion': 'Festive', 'style_tag': 'Traditional', 'season': 'All Season', 'fit': 'Regular', 'stock': 60
    },
    {
        'sku': 'SYN-IND-JUT-002', 'name': 'Tan Brown Braided Leather Kolhapuri Chappals',
        'category_id': CAT_FOOTWEAR, 'category_name': 'Footwear', 'mfg_id': MFG_COROMANDEL,
        'gender': 'men', 'color': 'Tan', 'size': '42', 'material': 'Leather',
        'cost_price': 480, 'base_price': 1599, 'selling_price': 1199,
        'description': 'Authentic Kolhapuri flat sandals with braided strap and T-ring toe loop. Hand-stitched with vegetable tan leather.',
        'occasion': 'College', 'style_tag': 'Indo-Western', 'season': 'Summer', 'fit': 'Regular', 'stock': 55
    },
    {
        'sku': 'SYN-IND-JUT-003', 'name': 'Maroon Velvet Royal Mojari Shoes',
        'category_id': CAT_FOOTWEAR, 'category_name': 'Footwear', 'mfg_id': MFG_MALWA,
        'gender': 'men', 'color': 'Maroon', 'size': '43', 'material': 'Blended',
        'cost_price': 580, 'base_price': 1899, 'selling_price': 1449,
        'description': 'Royal velvet sherwani mojaris with curved toe and antique brass thread zardozi embroidery.',
        'occasion': 'Festive', 'style_tag': 'Royal Ethnic', 'season': 'Festive', 'fit': 'Regular', 'stock': 45
    },
    {
        'sku': 'SYN-IND-JUT-004', 'name': 'Mirror Work Pastel Pink Festive Jutti',
        'category_id': CAT_FOOTWEAR, 'category_name': 'Footwear', 'mfg_id': MFG_RAJWADA,
        'gender': 'women', 'color': 'Pink', 'size': '37', 'material': 'Cotton',
        'cost_price': 490, 'base_price': 1599, 'selling_price': 1199,
        'description': 'Blush pink jutti featuring glistening real glass mirror-work and dual-density memory foam insole.',
        'occasion': 'Festive', 'style_tag': 'Traditional', 'season': 'All Season', 'fit': 'Regular', 'stock': 50
    },
    {
        'sku': 'SYN-IND-JUT-005', 'name': 'Black Threadwork Embroidered Jutti',
        'category_id': CAT_FOOTWEAR, 'category_name': 'Footwear', 'mfg_id': MFG_MALWA,
        'gender': 'women', 'color': 'Black', 'size': '38', 'material': 'Cotton',
        'cost_price': 460, 'base_price': 1499, 'selling_price': 1099,
        'description': 'Midnight black jutti with colourful Kashmiri thread needlework motifs. Versatile with jeans or sarees.',
        'occasion': 'Casual', 'style_tag': 'Indo-Western', 'season': 'All Season', 'fit': 'Regular', 'stock': 65
    },
    {
        'sku': 'SYN-IND-JUT-006', 'name': 'Off-White Pearl Encrusted Bridal Jutti',
        'category_id': CAT_FOOTWEAR, 'category_name': 'Footwear', 'mfg_id': MFG_RAJWADA,
        'gender': 'women', 'color': 'Off-White', 'size': '39', 'material': 'Silk',
        'cost_price': 650, 'base_price': 2299, 'selling_price': 1799,
        'description': 'Couture raw silk bridal jutti with pearl clusters and sequin spray. Double-cushioned bite-free collar.',
        'occasion': 'Festive', 'style_tag': 'Royal Ethnic', 'season': 'Festive', 'fit': 'Regular', 'stock': 40
    },
    {
        'sku': 'SYN-IND-JUT-007', 'name': 'Mustard Gota Patti Ankle-Strap Mojari',
        'category_id': CAT_FOOTWEAR, 'category_name': 'Footwear', 'mfg_id': MFG_COROMANDEL,
        'gender': 'women', 'color': 'Mustard', 'size': '38', 'material': 'Silk',
        'cost_price': 510, 'base_price': 1699, 'selling_price': 1249,
        'description': 'Bright turmeric yellow jutti with adjustable ankle-strap and delicate gold gota leaf work.',
        'occasion': 'Festive', 'style_tag': 'Traditional', 'season': 'Summer', 'fit': 'Regular', 'stock': 50
    },
    {
        'sku': 'SYN-IND-JUT-008', 'name': 'Men Handcrafted Tan Peshawari Chappal',
        'category_id': CAT_FOOTWEAR, 'category_name': 'Footwear', 'mfg_id': MFG_BRAHMAPUTRA,
        'gender': 'men', 'color': 'Tan', 'size': '41', 'material': 'Leather',
        'cost_price': 620, 'base_price': 1999, 'selling_price': 1499,
        'description': 'Traditional semi-closed Peshawari sandal with cross-over leather straps and durable Goodyear welt sole.',
        'occasion': 'Festive', 'style_tag': 'Traditional', 'season': 'All Season', 'fit': 'Regular', 'stock': 45
    },
    {
        'sku': 'SYN-IND-JUT-009', 'name': 'Emerald Green Velvet Sequin Slip-ons',
        'category_id': CAT_FOOTWEAR, 'category_name': 'Footwear', 'mfg_id': MFG_MALWA,
        'gender': 'women', 'color': 'Emerald Green', 'size': '37', 'material': 'Blended',
        'cost_price': 540, 'base_price': 1799, 'selling_price': 1349,
        'description': 'Deep forest green velvet flat mule jutti with subtle champagne gold sequin shimmer.',
        'occasion': 'Party', 'style_tag': 'Chic', 'season': 'Winter', 'fit': 'Regular', 'stock': 45
    },
    {
        'sku': 'SYN-IND-JUT-010', 'name': 'Silver Metallic Cutwork Kolhapuri Flats',
        'category_id': CAT_FOOTWEAR, 'category_name': 'Footwear', 'mfg_id': MFG_COROMANDEL,
        'gender': 'women', 'color': 'Silver', 'size': '38', 'material': 'Blended',
        'cost_price': 420, 'base_price': 1399, 'selling_price': 999,
        'description': 'Modernized silver metallic Kolhapuri slip-on sandal with geometric laser cutwork and soft footbed.',
        'occasion': 'Party', 'style_tag': 'Indo-Western', 'season': 'Summer', 'fit': 'Regular', 'stock': 60
    },
    {
        'sku': 'SYN-IND-JUT-011', 'name': 'Teal Floral Printed Mules with Tassels',
        'category_id': CAT_FOOTWEAR, 'category_name': 'Footwear', 'mfg_id': MFG_COASTAL,
        'gender': 'women', 'color': 'Teal', 'size': '39', 'material': 'Cotton',
        'cost_price': 440, 'base_price': 1449, 'selling_price': 1049,
        'description': 'Backless mule jutti in peacock teal canvas with miniature hanging silk tassels.',
        'occasion': 'College', 'style_tag': 'Bohemian', 'season': 'All Season', 'fit': 'Regular', 'stock': 55
    },
    {
        'sku': 'SYN-IND-JUT-012', 'name': 'Men Gold Textured Brocade Wedding Nagra',
        'category_id': CAT_FOOTWEAR, 'category_name': 'Footwear', 'mfg_id': MFG_RAJWADA,
        'gender': 'men', 'color': 'Gold', 'size': '44', 'material': 'Silk',
        'cost_price': 640, 'base_price': 2199, 'selling_price': 1699,
        'description': 'Rich metallic gold brocade pointed nagra shoe tailored to match wedding and sangeet kurtas.',
        'occasion': 'Festive', 'style_tag': 'Royal Ethnic', 'season': 'Festive', 'fit': 'Regular', 'stock': 35
    },
    {
        'sku': 'SYN-IND-JUT-013', 'name': 'Red Zari Border Bridal Khussa',
        'category_id': CAT_FOOTWEAR, 'category_name': 'Footwear', 'mfg_id': MFG_MALWA,
        'gender': 'women', 'color': 'Red', 'size': '38', 'material': 'Silk',
        'cost_price': 570, 'base_price': 1899, 'selling_price': 1399,
        'description': 'Traditional sindoori red khussa jutti adorned with gold salma and sitara hand-embroidery.',
        'occasion': 'Festive', 'style_tag': 'Traditional', 'season': 'Festive', 'fit': 'Regular', 'stock': 40
    },
    {
        'sku': 'SYN-IND-JUT-014', 'name': 'Beige Braided Jute Casual Slip-on Flats',
        'category_id': CAT_FOOTWEAR, 'category_name': 'Footwear', 'mfg_id': MFG_COASTAL,
        'gender': 'women', 'color': 'Beige', 'size': '37', 'material': 'Cotton',
        'cost_price': 380, 'base_price': 1199, 'selling_price': 899,
        'description': 'Eco-conscious braided jute and natural cotton everyday flats with anti-skid rubber sole.',
        'occasion': 'College', 'style_tag': 'Minimalist', 'season': 'Summer', 'fit': 'Regular', 'stock': 65
    },
    {
        'sku': 'SYN-IND-JUT-015', 'name': 'Wine Velvet Kundan Studded Jutti',
        'category_id': CAT_FOOTWEAR, 'category_name': 'Footwear', 'mfg_id': MFG_RAJWADA,
        'gender': 'women', 'color': 'Wine', 'size': '38', 'material': 'Silk',
        'cost_price': 610, 'base_price': 1999, 'selling_price': 1499,
        'description': 'Rich burgundy wine velvet base with hand-set kundan stones and tiny gold seed beads.',
        'occasion': 'Party', 'style_tag': 'Traditional', 'season': 'Winter', 'fit': 'Regular', 'stock': 45
    },

    # -------------------------------------------------------------
    # 5. INDIAN JEWELLERY & ETHNIC ACCESSORIES (Category: Accessories) - 15 items
    # -------------------------------------------------------------
    {
        'sku': 'SYN-IND-ACC-001', 'name': 'Antique Gold Kundan Chandbali Earrings',
        'category_id': CAT_ACCESSORIES, 'category_name': 'Accessories', 'mfg_id': MFG_RAJWADA,
        'gender': 'women', 'color': 'Gold', 'size': 'Free', 'material': 'Blended',
        'cost_price': 280, 'base_price': 999, 'selling_price': 699,
        'description': 'Crescent moon chandbali earrings with sparkling polki glass kundan stones and tiny white seed pearls.',
        'occasion': 'Festive', 'style_tag': 'Traditional', 'season': 'All Season', 'fit': 'Regular', 'stock': 80
    },
    {
        'sku': 'SYN-IND-ACC-002', 'name': 'Traditional Meenakari Peacock Jhumkas',
        'category_id': CAT_ACCESSORIES, 'category_name': 'Accessories', 'mfg_id': MFG_MALWA,
        'gender': 'women', 'color': 'Teal', 'size': 'Free', 'material': 'Blended',
        'cost_price': 320, 'base_price': 1199, 'selling_price': 799,
        'description': 'Jaipuri hand-enameled meenakari dome jhumkas in peacock blue and green with hanging pearl drops.',
        'occasion': 'Festive', 'style_tag': 'Traditional', 'season': 'All Season', 'fit': 'Regular', 'stock': 70
    },
    {
        'sku': 'SYN-IND-ACC-003', 'name': 'Oxidized Silver Tribal Choker Necklace',
        'category_id': CAT_ACCESSORIES, 'category_name': 'Accessories', 'mfg_id': MFG_COROMANDEL,
        'gender': 'women', 'color': 'Silver', 'size': 'Free', 'material': 'Blended',
        'cost_price': 350, 'base_price': 1299, 'selling_price': 899,
        'description': 'Vintage German silver oxidized bohemian choker necklace with floral motifs and ghungroo bell drops.',
        'occasion': 'College', 'style_tag': 'Bohemian', 'season': 'All Season', 'fit': 'Regular', 'stock': 75
    },
    {
        'sku': 'SYN-IND-ACC-004', 'name': 'Ruby Red Temple Jewellery Choker Set',
        'category_id': CAT_ACCESSORIES, 'category_name': 'Accessories', 'mfg_id': MFG_RAJWADA,
        'gender': 'women', 'color': 'Red', 'size': 'Free', 'material': 'Blended',
        'cost_price': 480, 'base_price': 1799, 'selling_price': 1299,
        'description': 'South Indian temple jewellery inspired choker with matte gold finish, red kempu stones, and matching earrings.',
        'occasion': 'Festive', 'style_tag': 'Royal Ethnic', 'season': 'Festive', 'fit': 'Regular', 'stock': 50
    },
    {
        'sku': 'SYN-IND-ACC-005', 'name': 'Emerald Green Layered Kundan Mala',
        'category_id': CAT_ACCESSORIES, 'category_name': 'Accessories', 'mfg_id': MFG_MALWA,
        'gender': 'unisex', 'color': 'Emerald Green', 'size': 'Free', 'material': 'Blended',
        'cost_price': 420, 'base_price': 1599, 'selling_price': 1149,
        'description': 'Three-strand emerald green faux gemstone beaded mala with royal kundan pendant. Suitable for men and women.',
        'occasion': 'Festive', 'style_tag': 'Royal Ethnic', 'season': 'Festive', 'fit': 'Regular', 'stock': 60
    },
    {
        'sku': 'SYN-IND-ACC-006', 'name': 'Gold Plated Floral Hathphool Hand Harness',
        'category_id': CAT_ACCESSORIES, 'category_name': 'Accessories', 'mfg_id': MFG_RAJWADA,
        'gender': 'women', 'color': 'Gold', 'size': 'Free', 'material': 'Blended',
        'cost_price': 290, 'base_price': 999, 'selling_price': 699,
        'description': 'Dainty gold hand harness connecting adjustable ring to wrist bracelet with kundan studded floral centre.',
        'occasion': 'Party', 'style_tag': 'Traditional', 'season': 'All Season', 'fit': 'Regular', 'stock': 65
    },
    {
        'sku': 'SYN-IND-ACC-007', 'name': 'Oxidized Silver Mirror Nose Pin (Clip-on)',
        'category_id': CAT_ACCESSORIES, 'category_name': 'Accessories', 'mfg_id': MFG_COROMANDEL,
        'gender': 'women', 'color': 'Silver', 'size': 'Free', 'material': 'Blended',
        'cost_price': 110, 'base_price': 399, 'selling_price': 249,
        'description': 'Non-pierced clip-on oxidized silver nose pin with mirror stone centerpiece for instant Indo-Western flair.',
        'occasion': 'College', 'style_tag': 'Bohemian', 'season': 'All Season', 'fit': 'Regular', 'stock': 100
    },
    {
        'sku': 'SYN-IND-ACC-008', 'name': 'Pearl & Gold Sheeshpatti / Matha Patti',
        'category_id': CAT_ACCESSORIES, 'category_name': 'Accessories', 'mfg_id': MFG_RAJWADA,
        'gender': 'women', 'color': 'Gold', 'size': 'Free', 'material': 'Blended',
        'cost_price': 420, 'base_price': 1499, 'selling_price': 1099,
        'description': 'Regal bridal forehead hairline band adorned with lustrous pearls, kundan work, and secure bobby pin loops.',
        'occasion': 'Festive', 'style_tag': 'Royal Ethnic', 'season': 'Festive', 'fit': 'Regular', 'stock': 45
    },
    {
        'sku': 'SYN-IND-ACC-009', 'name': 'Set of 4 Brass Textured Gold Bangles',
        'category_id': CAT_ACCESSORIES, 'category_name': 'Accessories', 'mfg_id': MFG_MALWA,
        'gender': 'women', 'color': 'Gold', 'size': '2.6', 'material': 'Blended',
        'cost_price': 310, 'base_price': 1099, 'selling_price': 799,
        'description': 'Handcrafted solid brass antique matte gold finish kada bangles with floral filigree engravings.',
        'occasion': 'Festive', 'style_tag': 'Traditional', 'season': 'All Season', 'fit': 'Regular', 'stock': 70
    },
    {
        'sku': 'SYN-IND-ACC-010', 'name': 'Oxidized Silver Afgani Ghungroo Payal (Anklet)',
        'category_id': CAT_ACCESSORIES, 'category_name': 'Accessories', 'mfg_id': MFG_COROMANDEL,
        'gender': 'women', 'color': 'Silver', 'size': 'Free', 'material': 'Blended',
        'cost_price': 260, 'base_price': 899, 'selling_price': 599,
        'description': 'Musical melodious ghungroo bell anklet in antique oxidized polish with lobster claw clasp.',
        'occasion': 'College', 'style_tag': 'Bohemian', 'season': 'All Season', 'fit': 'Regular', 'stock': 85
    },
    {
        'sku': 'SYN-IND-ACC-011', 'name': 'Men Royal Lion Crest Gold Kurta Brooch',
        'category_id': CAT_ACCESSORIES, 'category_name': 'Accessories', 'mfg_id': MFG_BRAHMAPUTRA,
        'gender': 'men', 'color': 'Gold', 'size': 'Free', 'material': 'Blended',
        'cost_price': 240, 'base_price': 849, 'selling_price': 599,
        'description': 'Regal lion crest brooch with hanging double gold curb chain for bandhgala, blazer, or kurta collars.',
        'occasion': 'Festive', 'style_tag': 'Royal Ethnic', 'season': 'All Season', 'fit': 'Regular', 'stock': 75
    },
    {
        'sku': 'SYN-IND-ACC-012', 'name': 'Polki Crystal Dangler Statement Earrings',
        'category_id': CAT_ACCESSORIES, 'category_name': 'Accessories', 'mfg_id': MFG_RAJWADA,
        'gender': 'women', 'color': 'Silver', 'size': 'Free', 'material': 'Blended',
        'cost_price': 360, 'base_price': 1299, 'selling_price': 899,
        'description': 'Gleaming faceted uncut polki stones set in rhodium silver casing with delicate post-back closure.',
        'occasion': 'Party', 'style_tag': 'Chic', 'season': 'All Season', 'fit': 'Regular', 'stock': 60
    },
    {
        'sku': 'SYN-IND-ACC-013', 'name': 'Handmade Silk Thread Bangles Set (12 Pcs)',
        'category_id': CAT_ACCESSORIES, 'category_name': 'Accessories', 'mfg_id': MFG_COROMANDEL,
        'gender': 'women', 'color': 'Maroon', 'size': '2.6', 'material': 'Silk',
        'cost_price': 220, 'base_price': 799, 'selling_price': 549,
        'description': 'Handcrafted deep maroon and gold zari wound silk thread bangles studded with sparkling rhinestone ball chains.',
        'occasion': 'Festive', 'style_tag': 'Traditional', 'season': 'All Season', 'fit': 'Regular', 'stock': 65
    },
    {
        'sku': 'SYN-IND-ACC-014', 'name': 'Ethnic Embroidered Gold Waist Belt (Kamarbandh)',
        'category_id': CAT_ACCESSORIES, 'category_name': 'Accessories', 'mfg_id': MFG_MALWA,
        'gender': 'women', 'color': 'Gold', 'size': 'Free', 'material': 'Blended',
        'cost_price': 340, 'base_price': 1199, 'selling_price': 849,
        'description': 'Adjustable gold metallic thread fabric waist cincher belt with hanging ghungroo tassels to cinch sarees and lehengas.',
        'occasion': 'Festive', 'style_tag': 'Traditional', 'season': 'Festive', 'fit': 'Regular', 'stock': 55
    },
    {
        'sku': 'SYN-IND-ACC-015', 'name': 'Black Enamel Geometric Stud Earrings',
        'category_id': CAT_ACCESSORIES, 'category_name': 'Accessories', 'mfg_id': MFG_COROMANDEL,
        'gender': 'women', 'color': 'Black', 'size': 'Free', 'material': 'Blended',
        'cost_price': 140, 'base_price': 499, 'selling_price': 349,
        'description': 'Minimalist gold-framed jet black enamel studs. Lightweight and chic for everyday college looks.',
        'occasion': 'College', 'style_tag': 'Minimalist', 'season': 'All Season', 'fit': 'Regular', 'stock': 90
    },

    # -------------------------------------------------------------
    # 6. TRADITIONAL POTLI BAGS & CLUTCHES (Category: Handbags) - 10 items
    # -------------------------------------------------------------
    {
        'sku': 'SYN-IND-BAG-001', 'name': 'Golden Zari Embroidered Drawstring Potli',
        'category_id': CAT_HANDBAGS, 'category_name': 'Handbags', 'mfg_id': MFG_RAJWADA,
        'gender': 'women', 'color': 'Gold', 'size': 'Free', 'material': 'Silk',
        'cost_price': 450, 'base_price': 1499, 'selling_price': 1099,
        'description': 'Traditional pouch potli crafted in gold dupion silk with braided beaded drawstrings and pearl tassel bells.',
        'occasion': 'Festive', 'style_tag': 'Traditional', 'season': 'All Season', 'fit': 'Regular', 'stock': 55
    },
    {
        'sku': 'SYN-IND-BAG-002', 'name': 'Velvet Maroon Sequin Box Clutch with Chain',
        'category_id': CAT_HANDBAGS, 'category_name': 'Handbags', 'mfg_id': MFG_MALWA,
        'gender': 'women', 'color': 'Maroon', 'size': 'Free', 'material': 'Blended',
        'cost_price': 580, 'base_price': 1899, 'selling_price': 1399,
        'description': 'Structured hard-case evening clutch in plush deep maroon velvet with gold magnetic snap and detachable sling chain.',
        'occasion': 'Party', 'style_tag': 'Royal Ethnic', 'season': 'All Season', 'fit': 'Regular', 'stock': 45
    },
    {
        'sku': 'SYN-IND-BAG-003', 'name': 'Pearl Embellished White Silk Potli Bag',
        'category_id': CAT_HANDBAGS, 'category_name': 'Handbags', 'mfg_id': MFG_RAJWADA,
        'gender': 'women', 'color': 'Off-White', 'size': 'Free', 'material': 'Silk',
        'cost_price': 520, 'base_price': 1699, 'selling_price': 1249,
        'description': 'Pristine raw silk potli bag intricately covered in floral freshwater faux pearls and golden beads.',
        'occasion': 'Festive', 'style_tag': 'Traditional', 'season': 'All Season', 'fit': 'Regular', 'stock': 50
    },
    {
        'sku': 'SYN-IND-BAG-004', 'name': 'Emerald Green Gota Work Pouch with Tassels',
        'category_id': CAT_HANDBAGS, 'category_name': 'Handbags', 'mfg_id': MFG_MALWA,
        'gender': 'women', 'color': 'Emerald Green', 'size': 'Free', 'material': 'Silk',
        'cost_price': 430, 'base_price': 1399, 'selling_price': 999,
        'description': 'Bottle green silk festive pouch with geometric gota ribbons and ornate hanging latkans.',
        'occasion': 'Festive', 'style_tag': 'Traditional', 'season': 'All Season', 'fit': 'Regular', 'stock': 60
    },
    {
        'sku': 'SYN-IND-BAG-005', 'name': 'Black & Gold Jacquard Weave Evening Clutch',
        'category_id': CAT_HANDBAGS, 'category_name': 'Handbags', 'mfg_id': MFG_COROMANDEL,
        'gender': 'women', 'color': 'Black', 'size': 'Free', 'material': 'Silk',
        'cost_price': 480, 'base_price': 1599, 'selling_price': 1199,
        'description': 'Sleek envelope clutch in brocade jacquard pattern with antique gold metal frame and interior card slot.',
        'occasion': 'Party', 'style_tag': 'Chic', 'season': 'All Season', 'fit': 'Regular', 'stock': 50
    },
    {
        'sku': 'SYN-IND-BAG-006', 'name': 'Mustard Yellow Mirror Work Boho Potli',
        'category_id': CAT_HANDBAGS, 'category_name': 'Handbags', 'mfg_id': MFG_RAJWADA,
        'gender': 'women', 'color': 'Mustard', 'size': 'Free', 'material': 'Cotton',
        'cost_price': 390, 'base_price': 1299, 'selling_price': 949,
        'description': 'Festive mustard yellow cotton potli showcasing authentic Kutch reflective mirror and colorful wool embroidery.',
        'occasion': 'Festive', 'style_tag': 'Bohemian', 'season': 'All Season', 'fit': 'Regular', 'stock': 65
    },
    {
        'sku': 'SYN-IND-BAG-007', 'name': 'Wine Velvet Embroidered Oval Minaudière',
        'category_id': CAT_HANDBAGS, 'category_name': 'Handbags', 'mfg_id': MFG_MALWA,
        'gender': 'women', 'color': 'Wine', 'size': 'Free', 'material': 'Blended',
        'cost_price': 620, 'base_price': 2199, 'selling_price': 1599,
        'description': 'Capsule oval minaudière with rich wine velvet exterior, jeweled clasp lock, and golden cross-body chain.',
        'occasion': 'Party', 'style_tag': 'Royal Ethnic', 'season': 'Winter', 'fit': 'Regular', 'stock': 40
    },
    {
        'sku': 'SYN-IND-BAG-008', 'name': 'Silver Metallic Beaded Festive Wristlet',
        'category_id': CAT_HANDBAGS, 'category_name': 'Handbags', 'mfg_id': MFG_COROMANDEL,
        'gender': 'women', 'color': 'Silver', 'size': 'Free', 'material': 'Blended',
        'cost_price': 460, 'base_price': 1499, 'selling_price': 1149,
        'description': 'Shimmering silver micro-cut glass beads woven over durable satin backing with wristlet strap.',
        'occasion': 'Party', 'style_tag': 'Contemporary', 'season': 'All Season', 'fit': 'Regular', 'stock': 55
    },
    {
        'sku': 'SYN-IND-BAG-009', 'name': 'Blush Pink Organza Floral Ruffle Potli',
        'category_id': CAT_HANDBAGS, 'category_name': 'Handbags', 'mfg_id': MFG_RAJWADA,
        'gender': 'women', 'color': 'Pink', 'size': 'Free', 'material': 'Silk',
        'cost_price': 470, 'base_price': 1599, 'selling_price': 1180,
        'description': 'Romantic translucent organza ruffles over satin base in delicate blush pink with pearl handle strap.',
        'occasion': 'Festive', 'style_tag': 'Traditional', 'season': 'Summer', 'fit': 'Regular', 'stock': 50
    },
    {
        'sku': 'SYN-IND-BAG-010', 'name': 'Teal Silk Gold Zari Bucket Potli',
        'category_id': CAT_HANDBAGS, 'category_name': 'Handbags', 'mfg_id': MFG_MALWA,
        'gender': 'women', 'color': 'Teal', 'size': 'Free', 'material': 'Silk',
        'cost_price': 440, 'base_price': 1449, 'selling_price': 1049,
        'description': 'Roomy cylindrical bucket-style potli bag in peacock teal art silk with heavy golden zari embroidery.',
        'occasion': 'Festive', 'style_tag': 'Traditional', 'season': 'All Season', 'fit': 'Regular', 'stock': 60
    },

    # -------------------------------------------------------------
    # 7. HANDLOOM DUPATTAS & ETHNIC STOLES (Category: Ethnic Wear) - 15 items
    # -------------------------------------------------------------
    {
        'sku': 'SYN-IND-DUP-001', 'name': 'Red & Gold Banarasi Silk Zari Dupatta',
        'category_id': CAT_ETHNIC_WEAR, 'category_name': 'Ethnic Wear', 'mfg_id': MFG_RAJWADA,
        'gender': 'women', 'color': 'Red', 'size': '2.5m', 'material': 'Silk',
        'cost_price': 650, 'base_price': 2299, 'selling_price': 1799,
        'description': 'Heirloom quality 2.5-meter Banarasi Katan silk dupatta woven with intricate golden floral jaal and broad border.',
        'occasion': 'Festive', 'style_tag': 'Traditional', 'season': 'All Season', 'fit': 'Regular', 'stock': 50
    },
    {
        'sku': 'SYN-IND-DUP-002', 'name': 'Off-White Chanderi Gota Patti Dupatta',
        'category_id': CAT_ETHNIC_WEAR, 'category_name': 'Ethnic Wear', 'mfg_id': MFG_MALWA,
        'gender': 'women', 'color': 'Off-White', 'size': '2.4m', 'material': 'Silk',
        'cost_price': 520, 'base_price': 1799, 'selling_price': 1349,
        'description': 'Sheer lightweight Chanderi silk dupatta in regal ivory white decorated with floral gota patti appliques.',
        'occasion': 'Festive', 'style_tag': 'Traditional', 'season': 'All Season', 'fit': 'Regular', 'stock': 60
    },
    {
        'sku': 'SYN-IND-DUP-003', 'name': 'Multicolor Traditional Phulkari Embroidered Dupatta',
        'category_id': CAT_ETHNIC_WEAR, 'category_name': 'Ethnic Wear', 'mfg_id': MFG_BRAHMAPUTRA,
        'gender': 'women', 'color': 'Mustard', 'size': '2.3m', 'material': 'Chiffon',
        'cost_price': 480, 'base_price': 1699, 'selling_price': 1299,
        'description': 'Authentic Amritsari hand-embroidered Phulkari dupatta on chiffon base with vibrant geometric silk floss threadwork.',
        'occasion': 'Festive', 'style_tag': 'Traditional', 'season': 'All Season', 'fit': 'Regular', 'stock': 55
    },
    {
        'sku': 'SYN-IND-DUP-004', 'name': 'Royal Blue Bandhani Silk Crinkle Dupatta',
        'category_id': CAT_ETHNIC_WEAR, 'category_name': 'Ethnic Wear', 'mfg_id': MFG_RAJWADA,
        'gender': 'women', 'color': 'Royal Blue', 'size': '2.5m', 'material': 'Silk',
        'cost_price': 550, 'base_price': 1899, 'selling_price': 1399,
        'description': 'Traditional Gujarati tie-and-dye Bandhej dupatta in deep royal blue with contrast white dots and gold border.',
        'occasion': 'Festive', 'style_tag': 'Traditional', 'season': 'All Season', 'fit': 'Regular', 'stock': 50
    },
    {
        'sku': 'SYN-IND-DUP-005', 'name': 'Black & Gold Kalamkari Hand Block Print Dupatta',
        'category_id': CAT_ETHNIC_WEAR, 'category_name': 'Ethnic Wear', 'mfg_id': MFG_COROMANDEL,
        'gender': 'women', 'color': 'Black', 'size': '2.4m', 'material': 'Cotton',
        'cost_price': 420, 'base_price': 1499, 'selling_price': 1099,
        'description': 'Natural dye hand-painted Kalamkari cotton dupatta featuring heritage mythological motifs and zari border.',
        'occasion': 'College', 'style_tag': 'Bohemian', 'season': 'All Season', 'fit': 'Regular', 'stock': 65
    },
    {
        'sku': 'SYN-IND-DUP-006', 'name': 'Emerald Green Organza Scalloped Dupatta',
        'category_id': CAT_ETHNIC_WEAR, 'category_name': 'Ethnic Wear', 'mfg_id': MFG_MALWA,
        'gender': 'women', 'color': 'Emerald Green', 'size': '2.5m', 'material': 'Silk',
        'cost_price': 580, 'base_price': 1999, 'selling_price': 1499,
        'description': 'Crisp sheer organza dupatta in rich bottle green with delicate cutwork scalloped borders and small buttis.',
        'occasion': 'Party', 'style_tag': 'Chic', 'season': 'Summer', 'fit': 'Regular', 'stock': 50
    },
    {
        'sku': 'SYN-IND-DUP-007', 'name': 'Mustard Yellow Leheriya Chiffon Dupatta',
        'category_id': CAT_ETHNIC_WEAR, 'category_name': 'Ethnic Wear', 'mfg_id': MFG_RAJWADA,
        'gender': 'women', 'color': 'Mustard', 'size': '2.3m', 'material': 'Chiffon',
        'cost_price': 350, 'base_price': 1199, 'selling_price': 899,
        'description': 'Diagonal Rajasthani Leheriya wave pattern in saffron yellow and white on featherlight flowy chiffon.',
        'occasion': 'Festive', 'style_tag': 'Traditional', 'season': 'Summer', 'fit': 'Regular', 'stock': 70
    },
    {
        'sku': 'SYN-IND-DUP-008', 'name': 'Wine Zari Woven Tussar Silk Stole',
        'category_id': CAT_ETHNIC_WEAR, 'category_name': 'Ethnic Wear', 'mfg_id': MFG_BRAHMAPUTRA,
        'gender': 'unisex', 'color': 'Wine', 'size': '2.0m', 'material': 'Silk',
        'cost_price': 590, 'base_price': 2099, 'selling_price': 1599,
        'description': 'Rich wild Tussar silk stole in deep wine with subtle antique gold zari stripes and twisted fringe ends.',
        'occasion': 'Formal', 'style_tag': 'Smart Casual', 'season': 'Winter', 'fit': 'Regular', 'stock': 45
    },
    {
        'sku': 'SYN-IND-DUP-009', 'name': 'Pink & Gold Tissue Silk Festive Dupatta',
        'category_id': CAT_ETHNIC_WEAR, 'category_name': 'Ethnic Wear', 'mfg_id': MFG_MALWA,
        'gender': 'women', 'color': 'Pink', 'size': '2.4m', 'material': 'Silk',
        'cost_price': 610, 'base_price': 2199, 'selling_price': 1649,
        'description': 'Luminous metallic tissue silk dupatta in dual-tone rose gold pink with fine thread tassels.',
        'occasion': 'Party', 'style_tag': 'Royal Ethnic', 'season': 'Festive', 'fit': 'Regular', 'stock': 45
    },
    {
        'sku': 'SYN-IND-DUP-010', 'name': 'Beige Kantha Stitched Cotton Tussar Dupatta',
        'category_id': CAT_ETHNIC_WEAR, 'category_name': 'Ethnic Wear', 'mfg_id': MFG_BRAHMAPUTRA,
        'gender': 'women', 'color': 'Beige', 'size': '2.4m', 'material': 'Cotton',
        'cost_price': 450, 'base_price': 1599, 'selling_price': 1199,
        'description': 'Bengal artisan Kantha running stitch embroidery depicting village folklore on natural unbleached cotton.',
        'occasion': 'College', 'style_tag': 'Bohemian', 'season': 'All Season', 'fit': 'Regular', 'stock': 55
    },
    {
        'sku': 'SYN-IND-DUP-011', 'name': 'Teal Blue Chanderi Zari Border Dupatta',
        'category_id': CAT_ETHNIC_WEAR, 'category_name': 'Ethnic Wear', 'mfg_id': MFG_MALWA,
        'gender': 'women', 'color': 'Teal', 'size': '2.4m', 'material': 'Silk',
        'cost_price': 490, 'base_price': 1699, 'selling_price': 1249,
        'description': 'Peacock teal sheer chanderi dupatta with lustrous gold tissue pallu and floral woven motifs.',
        'occasion': 'Festive', 'style_tag': 'Traditional', 'season': 'All Season', 'fit': 'Regular', 'stock': 50
    },
    {
        'sku': 'SYN-IND-DUP-012', 'name': 'Men Off-White Embroidered Kurta Stole',
        'category_id': CAT_ETHNIC_WEAR, 'category_name': 'Ethnic Wear', 'mfg_id': MFG_RAJWADA,
        'gender': 'men', 'color': 'Off-White', 'size': '2.2m', 'material': 'Silk',
        'cost_price': 520, 'base_price': 1799, 'selling_price': 1349,
        'description': 'Men festive raw silk stole in cream ivory with golden zardozi borders for wedding kurtas and sherwanis.',
        'occasion': 'Festive', 'style_tag': 'Royal Ethnic', 'season': 'Festive', 'fit': 'Regular', 'stock': 40
    },
    {
        'sku': 'SYN-IND-DUP-013', 'name': 'Rust Ochre Ajrakh Modal Silk Dupatta',
        'category_id': CAT_ETHNIC_WEAR, 'category_name': 'Ethnic Wear', 'mfg_id': MFG_RAJWADA,
        'gender': 'women', 'color': 'Rust', 'size': '2.5m', 'material': 'Silk',
        'cost_price': 580, 'base_price': 1999, 'selling_price': 1499,
        'description': 'Handcrafted Kutch Ajrakh block printed dupatta on soft modal silk with natural madder red and indigo dyes.',
        'occasion': 'Casual', 'style_tag': 'Indo-Western', 'season': 'All Season', 'fit': 'Regular', 'stock': 50
    },
    {
        'sku': 'SYN-IND-DUP-014', 'name': 'Lavender Sheer Net Sequin Border Dupatta',
        'category_id': CAT_ETHNIC_WEAR, 'category_name': 'Ethnic Wear', 'mfg_id': MFG_COROMANDEL,
        'gender': 'women', 'color': 'Lavender', 'size': '2.3m', 'material': 'Blended',
        'cost_price': 380, 'base_price': 1299, 'selling_price': 949,
        'description': 'Soft net pastel lilac dupatta with scalloped borders embroidered with shimmering silver sequins.',
        'occasion': 'Party', 'style_tag': 'Chic', 'season': 'Summer', 'fit': 'Regular', 'stock': 55
    },
    {
        'sku': 'SYN-IND-DUP-015', 'name': 'Pure White Chikankari Mulmul Cotton Dupatta',
        'category_id': CAT_ETHNIC_WEAR, 'category_name': 'Ethnic Wear', 'mfg_id': MFG_RAJWADA,
        'gender': 'women', 'color': 'White', 'size': '2.4m', 'material': 'Cotton',
        'cost_price': 460, 'base_price': 1599, 'selling_price': 1199,
        'description': 'Breezy Lucknowi shadow work and bakhiya hand-embroidered pure mulmul cotton dupatta with crochet lace hem.',
        'occasion': 'College', 'style_tag': 'Traditional', 'season': 'Summer', 'fit': 'Regular', 'stock': 70
    },
]

def generate_synthetic_catalog_records():
    """
    Computes deterministic UUIDv5 identifiers and formats the complete list
    of product and inventory records ready for safe insertion.
    """
    products = []
    inventory = []

    for item in RAW_SYNTHETIC_ITEMS:
        sku = item['sku']
        # Deterministic UUID derived from SKU
        p_id = str(uuid.uuid5(TARIKA_SYNTHETIC_NAMESPACE, sku))
        inv_id = str(uuid.uuid5(TARIKA_SYNTHETIC_NAMESPACE, f"INV-{sku}"))

        product_record = {
            'product_id': p_id,
            'product_name': item['name'],
            'category_id': item['category_id'],
            'category_name': item['category_name'],
            'manufacturer_id': item['mfg_id'],
            'sku': sku,
            'description': item['description'],
            'gender': item['gender'],
            'color': item['color'],
            'size': item['size'],
            'material': item['material'],
            'cost_price': item['cost_price'],
            'base_price': item['base_price'],
            'selling_price': item['selling_price'],
            'launch_date': '2026-03-01',
            'is_active': True,
            'occasion': item['occasion'],
            'style_tag': item['style_tag'],
            'season': item['season'],
            'fit': item['fit'],
        }

        inv_record = {
            'inventory_id': inv_id,
            'product_id': p_id,
            'warehouse_id': WH_BHIWANDI,
            'stock_quantity': item['stock'],
            'reorder_level': 20,
            'last_restock_date': '2026-03-01',
        }

        products.append(product_record)
        inventory.append(inv_record)

    return products, inventory
