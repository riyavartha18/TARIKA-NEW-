"""
Metadata Enrichment & Normalization Layer (Non-Destructive)
TARIKA Fashion Retail

Maps and normalizes product attributes (colors, occasions, styles, seasons, fits)
for existing database records and new synthetic items at runtime without altering
the database schema or modifying existing records.
"""

# Canonical Color Normalization Map
COLOR_CANONICAL_MAP = {
    'white': 'White',
    'off white': 'Off-White',
    'off-white': 'Off-White',
    'cream': 'Off-White',
    'ivory': 'Off-White',
    'beige': 'Beige',
    'black': 'Black',
    'charcoal': 'Charcoal',
    'grey': 'Grey',
    'gray': 'Grey',
    'red': 'Red',
    'maroon': 'Maroon',
    'wine': 'Wine',
    'burgundy': 'Wine',
    'coral': 'Coral',
    'peach': 'Peach',
    'pink': 'Pink',
    'rani pink': 'Pink',
    'rose': 'Pink',
    'rose gold': 'Rose Gold',
    'magenta': 'Magenta',
    'purple': 'Purple',
    'lavender': 'Lavender',
    'navy blue': 'Navy Blue',
    'royal blue': 'Royal Blue',
    'sky blue': 'Sky Blue',
    'teal': 'Teal',
    'emerald green': 'Emerald Green',
    'olive': 'Olive',
    'mint green': 'Mint Green',
    'green': 'Emerald Green',
    'mustard': 'Mustard',
    'yellow': 'Mustard',
    'marigold': 'Mustard',
    'marigold yellow': 'Mustard',
    'rust': 'Rust',
    'orange': 'Rust',
    'tan': 'Tan',
    'brown': 'Tan',
    'gold': 'Gold',
    'silver': 'Silver',
    'metallic': 'Silver',
}

COLOR_HARMONY_PAIRS = {
    ('Black', 'White'): 1.0,
    ('Black', 'Off-White'): 1.0,
    ('Black', 'Beige'): 0.95,
    ('Black', 'Red'): 0.95,
    ('Black', 'Wine'): 0.95,
    ('Black', 'Royal Blue'): 0.90,
    ('Black', 'Emerald Green'): 0.90,
    ('Black', 'Mustard'): 0.90,
    ('Black', 'Gold'): 0.95,
    ('Black', 'Silver'): 0.95,
    ('Black', 'Pink'): 0.90,
    ('White', 'Navy Blue'): 1.0,
    ('White', 'Sky Blue'): 0.95,
    ('White', 'Red'): 0.90,
    ('White', 'Olive'): 0.95,
    ('White', 'Coral'): 0.90,
    ('White', 'Gold'): 0.95,
    ('Off-White', 'Maroon'): 1.0,
    ('Off-White', 'Wine'): 1.0,
    ('Off-White', 'Emerald Green'): 1.0,
    ('Off-White', 'Royal Blue'): 0.95,
    ('Off-White', 'Mustard'): 0.95,
    ('Off-White', 'Gold'): 1.0,
    ('Off-White', 'Rust'): 0.95,
    ('Beige', 'Navy Blue'): 0.95,
    ('Beige', 'Wine'): 0.90,
    ('Beige', 'Emerald Green'): 0.90,
    ('Beige', 'Olive'): 0.95,
    ('Beige', 'Rust'): 0.90,
    ('Navy Blue', 'Mustard'): 0.95,
    ('Navy Blue', 'Silver'): 0.95,
    ('Navy Blue', 'Peach'): 0.90,
    ('Maroon', 'Gold'): 1.0,
    ('Wine', 'Gold'): 1.0,
    ('Wine', 'Silver'): 0.95,
    ('Emerald Green', 'Gold'): 1.0,
    ('Emerald Green', 'Peach'): 0.90,
    ('Mustard', 'Maroon'): 0.95,
    ('Mustard', 'Pink'): 0.90,
    ('Pink', 'Mustard'): 0.90,
    ('Peach', 'Mint Green'): 0.90,
    ('Lavender', 'Off-White'): 0.95,
    ('Lavender', 'Silver'): 0.95,
    ('Teal', 'Gold'): 0.95,
    ('Teal', 'Off-White'): 0.95,
    ('Rust', 'Beige'): 0.95,
    ('Rust', 'Gold'): 0.95,
}

# Canonical Style Mapping to the 5 UI Styles: Minimal, Chic, Streetwear, Traditional, Elegant
STYLE_CANONICAL_MAP = {
    'minimal': 'Minimal',
    'minimalist': 'Minimal',
    'cozy minimalist': 'Minimal',
    'clean': 'Minimal',
    'chic': 'Chic',
    'bohemian': 'Chic',
    'boho': 'Chic',
    'indo-western': 'Chic',
    'contemporary': 'Chic',
    'streetwear': 'Streetwear',
    'urban': 'Streetwear',
    'relaxed': 'Streetwear',
    'oversized': 'Streetwear',
    'traditional': 'Traditional',
    'royal ethnic': 'Traditional',
    'ethnic': 'Traditional',
    'heritage': 'Traditional',
    'elegant': 'Elegant',
    'smart casual': 'Elegant',
    'formal': 'Elegant',
    'sophisticated': 'Elegant',
    'cocktail': 'Elegant',
}

# Color Family Grouping for flexible UI color queries (supporting single and multiple selections)
COLOR_FAMILY_MAP = {
    'pink': {'pink', 'rose', 'dusty rose', 'rani pink', 'magenta', 'peach', 'coral'},
    'white': {'white', 'off-white', 'off white', 'cream', 'ivory'},
    'off-white': {'off-white', 'off white', 'cream', 'ivory', 'white'},
    'beige': {'beige', 'tan', 'brown', 'khaki', 'nude', 'camel'},
    'black': {'black', 'charcoal', 'grey', 'gray'},
    'red': {'red', 'maroon', 'wine', 'burgundy', 'rust', 'coral'},
    'maroon': {'maroon', 'wine', 'burgundy', 'red'},
    'blue': {'blue', 'sky blue', 'navy blue', 'navy', 'royal blue', 'teal', 'indigo'},
    'green': {'green', 'emerald green', 'olive', 'sage green', 'mint green', 'teal'},
    'yellow': {'yellow', 'mustard', 'marigold', 'marigold yellow', 'gold'},
    'purple': {'purple', 'lavender', 'lilac', 'violet', 'magenta'},
}

def normalize_style(raw_style):
    """Maps any style string to one of the 5 canonical UI styles: Minimal, Chic, Streetwear, Traditional, Elegant."""
    if not raw_style:
        return 'Chic'
    clean = str(raw_style).strip().lower()
    return STYLE_CANONICAL_MAP.get(clean, 'Chic')

def is_color_family_match(product_color, target_colors):
    """
    Checks if a product's color matches any of the target preferred colors,
    normalizing variants such as cream/off-white, rani pink/rose, and maroon/wine.
    """
    if not target_colors:
        return True
    p_norm = normalize_color(product_color).strip().lower()

    if isinstance(target_colors, str):
        target_colors = [target_colors]

    for tc in target_colors:
        tc_clean = str(tc).strip().lower()
        if tc_clean == p_norm:
            return True
        family = COLOR_FAMILY_MAP.get(tc_clean, {tc_clean})
        if p_norm in family or any(f in p_norm for f in family):
            return True
        # Check reverse family lookup
        p_family = COLOR_FAMILY_MAP.get(p_norm, {p_norm})
        if tc_clean in p_family or any(f in tc_clean for f in p_family):
            return True

    return False

def normalize_color(raw_color):
    """Normalizes raw product color string to canonical color."""
    if not raw_color:
        return 'Multi'
    clean = str(raw_color).strip().lower()
    return COLOR_CANONICAL_MAP.get(clean, str(raw_color).title())

def get_color_compatibility(color1, color2):
    """Calculates color harmony score between 0.0 and 1.0."""
    c1 = normalize_color(color1)
    c2 = normalize_color(color2)
    if c1 == c2:
        return 1.0
    if (c1, c2) in COLOR_HARMONY_PAIRS:
        return COLOR_HARMONY_PAIRS[(c1, c2)]
    if (c2, c1) in COLOR_HARMONY_PAIRS:
        return COLOR_HARMONY_PAIRS[(c2, c1)]
    neutrals = {'White', 'Off-White', 'Black', 'Grey', 'Charcoal', 'Beige', 'Tan', 'Gold', 'Silver'}
    if c1 in neutrals or c2 in neutrals:
        return 0.75
    return 0.50

def infer_product_metadata(product_dict):
    """
    Infers occasion, style_tag, season, and fit for any product
    based on its existing attributes without writing to database.
    """
    category = (product_dict.get('category_name') or '').strip().lower()
    name = (product_dict.get('product_name') or '').strip().lower()
    material = (product_dict.get('material') or '').strip().lower()
    desc = (product_dict.get('description') or '').strip().lower()
    color = normalize_color(product_dict.get('color'))

    occasion = 'Casual'
    style_tag = 'Contemporary'
    season = 'All Season'
    fit = 'Regular'

    if any(k in category for k in ['saree', 'ethnic', 'kurti']) or any(k in name for k in ['saree', 'kurta', 'kurti', 'lehenga', 'anarkali', 'sharara', 'palazzo', 'dupatta', 'jhumka']):
        if 'saree' in category or 'saree' in name or any(m in material for m in ['silk', 'brocade', 'velvet', 'georgette', 'chiffon']) or any(w in name for w in ['embroidered', 'zari', 'festive', 'bridal', 'banarasi', 'kanjivaram', 'kanjeevaram']):
            occasion = 'Festive'
            style_tag = 'Traditional'
        elif any(w in name for w in ['party', 'sequin', 'glam', 'metallic']):
            occasion = 'Party'
            style_tag = 'Royal Ethnic'
        else:
            occasion = 'College' if any(m in material for m in ['cotton', 'rayon', 'linen']) else 'Casual'
            style_tag = 'Indo-Western'

    elif 'dress' in category or 'dress' in name:
        if any(w in name for w in ['gown', 'evening', 'party', 'cocktail', 'metallic', 'sequin']) or material in ['silk', 'satin']:
            occasion = 'Party'
            style_tag = 'Chic'
        elif any(w in name for w in ['maxi', 'floral', 'boho', 'wrap']):
            occasion = 'Casual'
            style_tag = 'Bohemian'
        else:
            occasion = 'College'
            style_tag = 'Minimalist'

    elif 't-shirt' in category or 't-shirt' in name or 'tshirt' in name:
        occasion = 'College'
        style_tag = 'Streetwear'
        fit = 'Oversized' if 'oversized' in name else ('Slim' if 'slim' in name else 'Regular')

    elif any(k in category for k in ['trouser', 'shirt']) or any(k in name for k in ['trouser', 'formal shirt', 'oxford', 'blazer']):
        occasion = 'Formal'
        style_tag = 'Smart Casual'
        fit = 'Slim' if 'slim' in name or 'slim' in desc else 'Regular'

    elif 'jean' in category or 'jean' in name:
        occasion = 'Casual'
        style_tag = 'Streetwear'
        fit = 'Slim' if 'slim' in name else ('Relaxed' if 'relaxed' in name or 'baggy' in name else 'Regular')

    elif 'jacket' in category or 'jacket' in name:
        season = 'Winter'
        if any(w in name for w in ['nehru', 'bandhgala', 'ethnic']):
            occasion = 'Festive'
            style_tag = 'Indo-Western'
        else:
            occasion = 'Casual'
            style_tag = 'Streetwear'

    elif 'sweater' in category or 'sweater' in name:
        season = 'Winter'
        occasion = 'College'
        style_tag = 'Cozy Minimalist'

    elif 'footwear' in category or 'footwear' in name:
        if any(w in name for w in ['jutti', 'mojari', 'kolhapuri', 'ethnic']):
            occasion = 'Festive'
            style_tag = 'Traditional'
        elif any(w in name for w in ['heel', 'stiletto', 'pump']):
            occasion = 'Party'
            style_tag = 'Chic'
        elif any(w in name for w in ['sneaker', 'trainer']):
            occasion = 'College'
            style_tag = 'Streetwear'
        else:
            occasion = 'Casual'
            style_tag = 'Minimalist'

    elif any(k in category for k in ['handbag', 'accessories']):
        if any(w in name for w in ['potli', 'clutch', 'jhumka', 'necklace', 'kundan', 'polki']):
            occasion = 'Festive'
            style_tag = 'Traditional'
        elif any(w in name for w in ['tote', 'backpack']):
            occasion = 'College'
            style_tag = 'Minimalist'
        else:
            occasion = 'Casual'
            style_tag = 'Contemporary'

    if material in ['wool', 'fleece', 'corduroy', 'leather']:
        season = 'Winter'
    elif material in ['linen', 'cotton', 'chambray']:
        season = 'Summer'
    elif occasion == 'Festive':
        season = 'Festive'

    canonical_style = normalize_style(style_tag)

    return {
        'canonical_color': color,
        'occasion': occasion,
        'style_tag': canonical_style,
        'raw_style': style_tag,
        'season': season,
        'fit': fit,
    }
