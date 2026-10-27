"""
Reusable Outfit Compatibility Engine
TARIKA Fashion Retail

A rule-based, deterministic fashion recommendation and outfit compatibility engine.
Evaluates:
  1. Category Grammar (prevents 2 tops, classifies shoes vs bags, ensures completeness).
  2. Color Harmonization (contrasting neutrals, complementary and festive pairs).
  3. Style & Occasion Cohesion (College, Casual, Party, Formal, Festive).
  4. Seasonal Suitability (Summer, Winter, All Season).
  5. Strict Budget Compliance (total price <= budget).
  6. Transparent, human-understandable explanations for every match.
"""

from typing import List, Dict, Any, Optional
from decimal import Decimal
from recommendations.metadata_enrichment import (
    normalize_color,
    normalize_style,
    is_color_family_match,
    get_color_compatibility,
    infer_product_metadata
)

# Standard Slot Definitions
SLOT_TOP = 'TOP'
SLOT_BOTTOM = 'BOTTOM'
SLOT_ONE_PIECE = 'ONE_PIECE'
SLOT_FOOTWEAR = 'FOOTWEAR'
SLOT_BAG = 'BAG'
SLOT_ACCESSORY = 'ACCESSORY'
SLOT_LAYER = 'LAYER'

# Mapping categories to grammatical outfit slots
CATEGORY_TO_SLOT = {
    'tops': SLOT_TOP,
    'shirts': SLOT_TOP,
    't-shirts': SLOT_TOP,
    'tshirts': SLOT_TOP,
    'kurtis': SLOT_TOP,
    'dresses': SLOT_ONE_PIECE,
    'sarees': SLOT_ONE_PIECE,
    'co-ord set': SLOT_ONE_PIECE,
    'bottom wear': SLOT_BOTTOM,
    'trousers': SLOT_BOTTOM,
    'jeans': SLOT_BOTTOM,
    'footwear': SLOT_FOOTWEAR,
    'accessories': SLOT_ACCESSORY,
    'handbags': SLOT_BAG,
    'ethnic wear': SLOT_LAYER,  # Dupattas & Stoles act as layers/accents
    'jackets': SLOT_LAYER,
    'sweaters': SLOT_LAYER,
}

# Style Compatibility Matrix across the 5 canonical styles: Minimal, Chic, Streetwear, Traditional, Elegant
STYLE_COHESION_SCORES = {
    ('Traditional', 'Traditional'): 1.0,
    ('Traditional', 'Elegant'): 0.90,
    ('Traditional', 'Chic'): 0.85,
    ('Traditional', 'Minimal'): 0.75,
    ('Traditional', 'Streetwear'): 0.20,  # Clashing
    ('Minimal', 'Minimal'): 1.0,
    ('Minimal', 'Elegant'): 0.95,
    ('Minimal', 'Chic'): 0.90,
    ('Minimal', 'Streetwear'): 0.85,
    ('Chic', 'Chic'): 1.0,
    ('Chic', 'Elegant'): 0.95,
    ('Chic', 'Streetwear'): 0.85,
    ('Streetwear', 'Streetwear'): 1.0,
    ('Elegant', 'Elegant'): 1.0,
}

def get_slot_for_item(item: Dict[str, Any]) -> str:
    """Returns the functional grammatical outfit slot for a product or wardrobe item."""
    if not item:
        return SLOT_TOP
    cat = (item.get('category_name') or item.get('category') or '').strip().lower()
    name = (item.get('product_name') or item.get('item_name') or '').strip().lower()

    if any(k in name for k in ['dupatta', 'stole', 'shawl', 'shrug', 'cardigan']):
        return SLOT_LAYER
    if any(k in name for k in ['tunic', 'kurti', 'kurta', 'top', 'shirt', 'tee', 't-shirt', 'blouse']):
        return SLOT_TOP
    if any(k in name for k in ['palazzo', 'sharara', 'dhoti', 'churidar', 'skirt', 'shorts', 'trousers', 'trouser', 'jeans', 'jean', 'legging', 'pants', 'chinos']):
        return SLOT_BOTTOM
    if any(k in name for k in ['potli', 'clutch', 'tote', 'sling', 'handbag', 'shoulder bag', 'bag', 'purse', 'backpack', 'wallet']):
        return SLOT_BAG
    if any(k in name for k in ['jutti', 'mojari', 'kolhapuri', 'sneaker', 'heel', 'sandal', 'flat', 'loafer', 'boot', 'footwear', 'shoe', 'mule', 'slide']):
        return SLOT_FOOTWEAR
    if any(k in name for k in ['jhumka', 'earring', 'necklace', 'pendant', 'bangle', 'bracelet', 'ring', 'belt', 'watch', 'jewel', 'brooch', 'chain']):
        return SLOT_ACCESSORY
    if any(k in name for k in ['lehenga', 'salwar suit', 'anarkali', 'sherwani', 'jumpsuit', 'romper', 'co-ord', 'coord']):
        return SLOT_ONE_PIECE
    if any(k in name for k in ['dress', 'saree', 'sari']):
        return SLOT_ONE_PIECE

    return CATEGORY_TO_SLOT.get(cat, SLOT_TOP)

def classify_product_fashion_direction(item: Dict[str, Any]) -> str:
    """
    Classifies an item into primary fashion categories:
      - 'Western'
      - 'Ethnic'
      - 'Indo-Western'
      - 'Dresses & Jumpsuits'
    """
    cat = (item.get('category_name') or item.get('category') or '').strip().lower()
    name = (item.get('product_name') or item.get('item_name') or '').strip().lower()

    if cat in ['dresses', 'co-ord set'] or any(k in name for k in ['dress', 'jumpsuit', 'romper', 'co-ord', 'coord']):
        return 'Dresses & Jumpsuits'

    if cat in ['kurtis', 'sarees', 'ethnic wear'] or any(
        k in name for k in [
            'kurti', 'kurta', 'saree', 'sari', 'lehenga', 'salwar', 'anarkali', 
            'palazzo', 'sharara', 'dhoti', 'churidar', 'dupatta', 'stole', 
            'jutti', 'mojari', 'kolhapuri', 'potli', 'jhumka', 'sherwani'
        ]
    ):
        return 'Ethnic'

    return 'Western'

def classify_outfit_fashion_direction(items: List[Dict[str, Any]]) -> str:
    """Determines whether an assembled outfit is Western, Ethnic, Indo-Western, or Dresses & Jumpsuits."""
    core_items = [it for it in items if get_slot_for_item(it) in (SLOT_TOP, SLOT_BOTTOM, SLOT_ONE_PIECE)]
    if not core_items:
        core_items = items

    core_dirs = [classify_product_fashion_direction(it) for it in core_items]

    if any(classify_product_fashion_direction(it) == 'Dresses & Jumpsuits' for it in core_items):
        return 'Dresses & Jumpsuits'

    # Fusion / Indo-Western: ethnic top + western bottom or vice versa
    if 'Ethnic' in core_dirs and 'Western' in core_dirs:
        return 'Indo-Western'

    if all(d == 'Ethnic' for d in core_dirs):
        return 'Ethnic'

    if all(d == 'Western' for d in core_dirs):
        return 'Western'

    return 'Western'

def evaluate_style_cohesion(items: List[Dict[str, Any]]) -> float:
    """Scores style harmony across all items in an outfit (0.0 to 1.0)."""
    styles = [infer_product_metadata(it)['style_tag'] for it in items]
    if len(styles) <= 1:
        return 1.0

    scores = []
    for i in range(len(styles)):
        for j in range(i + 1, len(styles)):
            s1, s2 = styles[i], styles[j]
            if s1 == s2:
                scores.append(1.0)
            elif (s1, s2) in STYLE_COHESION_SCORES:
                scores.append(STYLE_COHESION_SCORES[(s1, s2)])
            elif (s2, s1) in STYLE_COHESION_SCORES:
                scores.append(STYLE_COHESION_SCORES[(s2, s1)])
            else:
                scores.append(0.65)  # neutral compatibility
    return sum(scores) / len(scores)

def evaluate_color_harmony(items: List[Dict[str, Any]]) -> float:
    """Calculates overall color harmony score across all items in an outfit."""
    colors = [normalize_color(it.get('color') or it.get('primary_color')) for it in items]
    if len(colors) <= 1:
        return 1.0

    scores = []
    for i in range(len(colors)):
        for j in range(i + 1, len(colors)):
            scores.append(get_color_compatibility(colors[i], colors[j]))
    return sum(scores) / len(scores)

def evaluate_occasion_match(items: List[Dict[str, Any]], target_occasion: Optional[str] = None) -> float:
    """Calculates occasion alignment score."""
    if not target_occasion or target_occasion.lower() == 'all':
        return 1.0

    target = target_occasion.strip().title()
    match_count = sum(1 for it in items if infer_product_metadata(it)['occasion'] == target)
    return match_count / len(items)

def generate_explanation(items: List[Dict[str, Any]], occasion: str, color_score: float, style_score: float) -> str:
    """Generates a rich, human-understandable explanation for why an outfit matches."""
    colors = list(dict.fromkeys(normalize_color(it.get('color') or it.get('primary_color')) for it in items))
    color_desc = " & ".join(colors[:3])

    if color_score >= 0.90:
        palette_text = f"striking {color_desc} palette"
    elif color_score >= 0.75:
        palette_text = f"harmonious {color_desc} combination"
    else:
        palette_text = f"subtle {color_desc} pairing"

    styles = list(dict.fromkeys(infer_product_metadata(it)['style_tag'] for it in items))
    style_text = " / ".join(styles[:2])

    if occasion and occasion != 'All':
        return f"Curated for {occasion}: Features a {palette_text} styled in a {style_text} silhouette, balancing aesthetic elegance with all-day comfort."
    return f"A cohesive look with a {palette_text} in a {style_text} aesthetic."

# Editorial outfit names by category and style
OUTFIT_NAME_REGISTRY = {
    'Western': [
        'Everyday Chic',
        'Minimal Muse',
        'Urban Streetwear',
        'Downtown Denim Edit',
        'Classic Sophisticate',
        'Modern Casual Luxe',
    ],
    'Ethnic': [
        'College Traditional',
        'Royal Heritage Ensemble',
        'Festive Grace',
        'Artisan Silk Charm',
        'Jaipur Pastel Bloom',
        'Boutique Anarkali Edit',
    ],
    'Indo-Western': [
        'Sunset Fusion',
        'Modern Indo-Chic',
        'Boho Radiance',
        'Contemporary Kurti & Denim',
        'Fusion Allure',
        'East-Meets-West Edit',
    ],
    'Dresses & Jumpsuits': [
        'A-Line Elegance',
        'Effortless Midi Look',
        'Monochrome Statement',
        'Boutique Day Dress',
        'Cocktail Radiance',
        'Co-ord Horizon',
    ],
}

def generate_outfit_title(fashion_dir: str, style: Optional[str], index: int) -> str:
    """Provides a polished editorial outfit title."""
    pool = OUTFIT_NAME_REGISTRY.get(fashion_dir, OUTFIT_NAME_REGISTRY['Western'])
    return pool[index % len(pool)]

def generate_outfit_description(items: List[Dict[str, Any]], fashion_dir: str, occasion: Optional[str], style: Optional[str]) -> str:
    """Generates concise editorial description."""
    occ = (occasion or 'any day').lower()
    sty = (style or 'stylish').lower()
    first_item = items[0].get('product_name') if items else 'ensemble'
    colors = [normalize_color(it.get('color')) for it in items if it.get('color')]
    color_hint = colors[0].lower() if colors else 'tonal'

    if fashion_dir == 'Ethnic':
        return f"A modern ethnic look with handcrafted touches and rich {color_hint} tones. Perfect for {occ}."
    elif fashion_dir == 'Indo-Western':
        return f"An effortless fusion pairing comfortable silhouettes with contemporary flair. Tailored for {occ}."
    elif fashion_dir == 'Dresses & Jumpsuits':
        return f"An elegant one-piece silhouette with curated accessories and seamless comfort for {occ}."
    else:
        return f"A fresh and versatile look featuring {color_hint} accents and timeless tailoring. Ideal for {occ}."


def compute_item_relevance(
    item: Dict[str, Any],
    target_occasion: Optional[str] = None,
    target_style: Optional[str] = None,
    preferred_colors: Optional[List[str]] = None,
    budget: Optional[float] = None
) -> float:
    """
    Computes a composite relevance score for an item based on user filters:
    - Occasion alignment (College, Casual, Party, Formal, Festive)
    - Style alignment (Minimal, Chic, Streetwear, Traditional, Elegant)
    - Preferred colors (exact or family match, e.g. cream/off-white, rani pink/rose)
    - Budget-conscious weighting to prioritize high-quality purchasable combinations
    """
    meta = infer_product_metadata(item)
    score = 0.0
    item_price = float(item.get('selling_price') or 0)

    # Budget consideration
    if budget is not None:
        if item_price >= float(budget):
            return -999.0
        if budget <= 1000:
            if item_price <= 350:
                score += 25.0
            elif item_price <= 500:
                score += 15.0

    # 1. Occasion alignment
    if target_occasion and target_occasion.lower() != 'all':
        occ_target = target_occasion.strip().title()
        item_occ = meta.get('occasion', 'Casual')
        if item_occ == occ_target:
            score += 50.0
        elif (occ_target == 'College' and item_occ == 'Casual') or (occ_target == 'Casual' and item_occ in ('College', 'Party')):
            score += 20.0
        elif occ_target == 'Formal' and item_occ in ('Formal', 'College'):
            score += 20.0

    # 2. Style alignment
    if target_style and target_style.lower() != 'all':
        sty_target = normalize_style(target_style)
        item_sty = meta.get('style_tag', 'Chic')
        if item_sty == sty_target:
            score += 50.0
        elif (sty_target, item_sty) in STYLE_COHESION_SCORES and STYLE_COHESION_SCORES[(sty_target, item_sty)] >= 0.85:
            score += 20.0

    # 3. Preferred colors alignment
    if preferred_colors:
        item_color = item.get('color') or meta.get('canonical_color')
        if is_color_family_match(item_color, preferred_colors):
            score += 70.0
        elif normalize_color(item_color) in ('White', 'Off-White', 'Black', 'Beige'):
            score += 15.0

    return score


class OutfitCompatibilityEngine:
    """
    Core Outfit Compatibility Engine supporting:
      - Category Grammar Validation across Western, Ethnic, Indo-Western, and One-Piece ensembles.
      - Budget Constrained Ranking (never exceeds budget).
      - Filter Alignment (Occasion, Style, Preferred Colors, Fashion Direction).
      - Explanatory scoring breakdown.
      - Support for combining Store Catalog items with Owned Wardrobe items.
    """

    @classmethod
    def validate_grammar(cls, items: List[Dict[str, Any]]) -> bool:
        """
        Validates outfit grammar:
          - Valid: TOP + BOTTOM + FOOTWEAR (+ optional BAG, ACCESSORY, LAYER)
          - Valid: ONE_PIECE + FOOTWEAR (+ optional BAG, ACCESSORY, LAYER)
          - Valid: TOP + BOTTOM (+ optional BAG, ACCESSORY, LAYER) if footwear is omitted
          - Invalid: 2 Tops without a bottom, Bag as Footwear, etc.
        """
        slots = [get_slot_for_item(it) for it in items]
        top_count = slots.count(SLOT_TOP)
        bottom_count = slots.count(SLOT_BOTTOM)
        one_piece_count = slots.count(SLOT_ONE_PIECE)
        footwear_count = slots.count(SLOT_FOOTWEAR)
        bag_count = slots.count(SLOT_BAG)
        layer_count = slots.count(SLOT_LAYER)
        accessory_count = slots.count(SLOT_ACCESSORY)

        # Rule 1: Cannot have more than 1 Top or 1 Bottom or 1 One-Piece
        if top_count > 1 or bottom_count > 1 or one_piece_count > 1:
            return False

        # Rule 2: Cannot mix One-Piece (Dress/Saree/Lehenga) with a Top or Bottom
        if one_piece_count >= 1 and (top_count >= 1 or bottom_count >= 1):
            return False

        # Rule 3: Must have either (Top + Bottom) OR (One-Piece)
        has_core = (top_count == 1 and bottom_count == 1) or (one_piece_count == 1)
        if not has_core:
            return False

        # Rule 4: Cannot have multiple Footwear or multiple Bags or multiple Layers
        if footwear_count > 1 or bag_count > 1 or layer_count > 1:
            return False

        # Rule 5: Cannot exceed 2 accessories
        if accessory_count > 2:
            return False

        return True

    @classmethod
    def score_outfit(
        cls,
        items: List[Dict[str, Any]],
        target_occasion: Optional[str] = None,
        target_style: Optional[str] = None,
        preferred_colors: Optional[List[str]] = None,
        budget: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Computes a weighted compatibility score between 0 and 100 for a candidate outfit.
        Integrates occasion match, style match, preferred color alignment, and color harmony.
        """
        # 1. Grammar Check
        if not cls.validate_grammar(items):
            return {'valid': False, 'score': 0, 'reason': 'Invalid outfit category grammar'}

        # 2. Budget Check
        total_price = sum(float(it.get('selling_price') or 0) for it in items if not it.get('is_owned'))
        if budget is not None and total_price > float(budget):
            return {
                'valid': False,
                'score': 0,
                'reason': f'Total price (₹{total_price:,.0f}) exceeds budget (₹{budget:,.0f})'
            }

        # 3. Factor Scores
        color_harmony = evaluate_color_harmony(items)
        style_cohesion = evaluate_style_cohesion(items)
        raw_occ_score = evaluate_occasion_match(items, target_occasion)

        # Occasion score with core emphasis
        if target_occasion and target_occasion.lower() != 'all':
            target_occ_clean = target_occasion.strip().title()
            core_items = [it for it in items if get_slot_for_item(it) in (SLOT_TOP, SLOT_BOTTOM, SLOT_ONE_PIECE)]
            core_match = sum(1 for it in core_items if infer_product_metadata(it)['occasion'] == target_occ_clean)
            core_rate = (core_match / len(core_items)) if core_items else 0.5
            occasion_score = (core_rate * 0.7) + (raw_occ_score * 0.3)
        else:
            occasion_score = raw_occ_score

        # Style matching score
        if target_style and target_style.lower() != 'all':
            target_s_clean = normalize_style(target_style)
            matching_styles = sum(1 for it in items if infer_product_metadata(it)['style_tag'] == target_s_clean)
            style_match_rate = matching_styles / len(items)
            style_score = (style_cohesion * 0.35) + (style_match_rate * 0.65)
        else:
            style_score = style_cohesion

        # Preferred color matching score
        has_pref_color = True
        if preferred_colors:
            matching_colors = sum(1 for it in items if is_color_family_match(it.get('color'), preferred_colors))
            has_pref_color = (matching_colors >= 1)
            if has_pref_color:
                color_match_rate = 0.75 + (0.25 * (matching_colors / len(items)))
            else:
                color_match_rate = 0.10
            color_score = (color_harmony * 0.20) + (color_match_rate * 0.80)
        else:
            color_score = color_harmony

        # Weighted composite score (0 to 100)
        # Filters have direct high impact
        has_filters = bool((target_occasion and target_occasion.lower() != 'all') or 
                           (target_style and target_style.lower() != 'all') or 
                           preferred_colors)

        if has_filters:
            raw_composite = (color_score * 0.35) + (style_score * 0.35) + (occasion_score * 0.30)
        else:
            raw_composite = (color_harmony * 0.40) + (style_cohesion * 0.40) + (occasion_score * 0.20)

        final_score = round(min(raw_composite, 1.0) * 100, 1)

        explanation = generate_explanation(items, target_occasion or 'Any Occasion', color_score, style_score)

        return {
            'valid': True,
            'score': final_score,
            'has_preferred_color': has_pref_color,
            'color_score': round(color_score * 100, 1),
            'style_score': round(style_score * 100, 1),
            'occasion_score': round(occasion_score * 100, 1),
            'total_price': total_price,
            'remaining_budget': (float(budget) - total_price) if budget is not None else None,
            'explanation': explanation,
        }

    @classmethod
    def assemble_outfits(
        cls,
        candidate_items: List[Dict[str, Any]],
        budget: Optional[float] = None,
        occasion: Optional[str] = None,
        style: Optional[str] = None,
        fashion_direction: Optional[str] = None,
        preferred_colors: Optional[List[str]] = None,
        seed_item: Optional[Dict[str, Any]] = None,
        complete_outfit: bool = True,
        max_results: int = 6
    ) -> List[Dict[str, Any]]:
        """
        Generates distinct, high-scoring, budget-compliant outfit combinations.
        Supports Western, Ethnic, Indo-Western, Dresses & Jumpsuits, and Surprise Me.
        """
        # Bucket items by grammatical slot
        slots_bucket = {
            SLOT_TOP: [],
            SLOT_BOTTOM: [],
            SLOT_ONE_PIECE: [],
            SLOT_FOOTWEAR: [],
            SLOT_BAG: [],
            SLOT_ACCESSORY: [],
            SLOT_LAYER: [],
        }

        # Filter candidates based on stock
        for item in candidate_items:
            slot = get_slot_for_item(item)
            is_avail = item.get('is_owned') or item.get('total_stock', 1) > 0 or item.get('in_stock', True)
            if not is_avail:
                continue
            slots_bucket[slot].append(item)

        # Sort candidate pools by relevance (Occasion, Style, Preferred Colors, Budget) and price
        for s in slots_bucket:
            slots_bucket[s].sort(
                key=lambda it: (
                    -compute_item_relevance(it, occasion, style, preferred_colors, budget),
                    float(it.get('selling_price') or 0)
                )
            )

        # Build candidate cores: (Top + Bottom) or (One-Piece)
        cores = []
        seed_slot = get_slot_for_item(seed_item) if seed_item else None

        if seed_item:
            if seed_slot == SLOT_TOP:
                for b in slots_bucket[SLOT_BOTTOM]:
                    cores.append([seed_item, b])
            elif seed_slot == SLOT_BOTTOM:
                for t in slots_bucket[SLOT_TOP]:
                    cores.append([t, seed_item])
            elif seed_slot == SLOT_ONE_PIECE:
                cores.append([seed_item])
            elif seed_slot == SLOT_FOOTWEAR:
                for t in slots_bucket[SLOT_TOP][:15]:
                    for b in slots_bucket[SLOT_BOTTOM][:15]:
                        cores.append([t, b])
                for op in slots_bucket[SLOT_ONE_PIECE][:15]:
                    cores.append([op])
            else:
                for t in slots_bucket[SLOT_TOP][:15]:
                    for b in slots_bucket[SLOT_BOTTOM][:15]:
                        cores.append([t, b])
                for op in slots_bucket[SLOT_ONE_PIECE][:15]:
                    cores.append([op])
        else:
            # Multi-category core generation
            clean_dir = (fashion_direction or 'Surprise Me').strip()

            tops = slots_bucket[SLOT_TOP]
            bottoms = slots_bucket[SLOT_BOTTOM]
            one_pieces = slots_bucket[SLOT_ONE_PIECE]

            if clean_dir == 'Western':
                # Western Top + Western Bottom
                w_tops = [t for t in tops if classify_product_fashion_direction(t) == 'Western']
                w_bottoms = [b for b in bottoms if classify_product_fashion_direction(b) == 'Western']
                for t in w_tops[:35]:
                    for b in w_bottoms[:35]:
                        cores.append([t, b])
            elif clean_dir == 'Ethnic':
                # Ethnic Top + Ethnic Bottom or Ethnic One-Piece (Saree / Lehenga / Salwar)
                e_tops = [t for t in tops if classify_product_fashion_direction(t) == 'Ethnic']
                e_bottoms = [b for b in bottoms if classify_product_fashion_direction(b) == 'Ethnic']
                e_ops = [op for op in one_pieces if classify_product_fashion_direction(op) == 'Ethnic']
                for t in e_tops[:30]:
                    for b in e_bottoms[:30]:
                        cores.append([t, b])
                for op in e_ops[:30]:
                    cores.append([op])
            elif clean_dir == 'Indo-Western':
                # Fusion: Ethnic Top + Western Bottom OR Western Top + Ethnic Bottom
                e_tops = [t for t in tops if classify_product_fashion_direction(t) == 'Ethnic']
                w_bottoms = [b for b in bottoms if classify_product_fashion_direction(b) == 'Western']
                w_tops = [t for t in tops if classify_product_fashion_direction(t) == 'Western']
                e_bottoms = [b for b in bottoms if classify_product_fashion_direction(b) == 'Ethnic']

                for t in e_tops[:25]:
                    for b in w_bottoms[:25]:
                        cores.append([t, b])
                for t in w_tops[:25]:
                    for b in e_bottoms[:25]:
                        cores.append([t, b])
            elif clean_dir == 'Dresses & Jumpsuits':
                dresses = [op for op in one_pieces if classify_product_fashion_direction(op) == 'Dresses & Jumpsuits']
                for op in dresses[:35]:
                    cores.append([op])
            else:
                # Surprise Me / All: blend Western, Ethnic, Indo-Western, and Dresses
                # 1. Western cores
                w_tops = [t for t in tops if classify_product_fashion_direction(t) == 'Western']
                w_bottoms = [b for b in bottoms if classify_product_fashion_direction(b) == 'Western']
                for t in w_tops[:20]:
                    for b in w_bottoms[:20]:
                        cores.append([t, b])
                # 2. Ethnic cores
                e_tops = [t for t in tops if classify_product_fashion_direction(t) == 'Ethnic']
                e_bottoms = [b for b in bottoms if classify_product_fashion_direction(b) == 'Ethnic']
                for t in e_tops[:20]:
                    for b in e_bottoms[:20]:
                        cores.append([t, b])
                # 3. Indo-Western fusion cores
                for t in e_tops[:20]:
                    for b in w_bottoms[:20]:
                        cores.append([t, b])
                # 4. One-Pieces (Dresses, Sarees, Co-ords)
                for op in one_pieces[:30]:
                    cores.append([op])


        # Attach Footwear, Bags, and Accessories
        candidate_combinations = []
        clean_dir = (fashion_direction or 'Surprise Me').strip()
        fw_pool = slots_bucket[SLOT_FOOTWEAR]
        bag_pool = slots_bucket[SLOT_BAG]
        acc_pool = slots_bucket[SLOT_ACCESSORY]

        if clean_dir == 'Western':
            fw_pool = [fw for fw in fw_pool if classify_product_fashion_direction(fw) == 'Western'] or fw_pool
            bag_pool = [b for b in bag_pool if classify_product_fashion_direction(b) == 'Western'] or bag_pool
            acc_pool = [a for a in acc_pool if classify_product_fashion_direction(a) == 'Western'] or acc_pool
        elif clean_dir == 'Ethnic':
            fw_pool = [fw for fw in fw_pool if classify_product_fashion_direction(fw) == 'Ethnic'] or fw_pool
            bag_pool = [b for b in bag_pool if classify_product_fashion_direction(b) == 'Ethnic'] or bag_pool
            acc_pool = [a for a in acc_pool if classify_product_fashion_direction(a) == 'Ethnic'] or acc_pool


        for core in cores:
            core_cost = sum(float(c.get('selling_price') or 0) for c in core if not c.get('is_owned'))
            if budget is not None and core_cost > float(budget):
                continue
            rem_budget = (float(budget) - core_cost) if budget is not None else 999999.0

            # If seed item was footwear or accessory, ensure it is added
            if seed_item and seed_slot == SLOT_FOOTWEAR:
                fw_candidates = [seed_item]
            elif fw_pool:
                valid_fw = [fw for fw in fw_pool if (float(fw.get('selling_price') or 0) if not fw.get('is_owned') else 0) <= rem_budget]
                fw_candidates = valid_fw[:8] if valid_fw else ([None] if rem_budget >= 0 else [])
            else:
                fw_candidates = [None]

            for fw in fw_candidates:
                base_combo = list(core)
                if fw:
                    base_combo.append(fw)

                # Add seed item if not already in combo
                if seed_item and seed_item not in base_combo:
                    base_combo.append(seed_item)

                base_cost = sum(float(it.get('selling_price') or 0) for it in base_combo if not it.get('is_owned'))
                if budget is not None and base_cost > float(budget):
                    continue
                rem_after_base = (float(budget) - base_cost) if budget is not None else 999999.0

                # Option 1: Clean Core (+ Footwear)
                has_one_piece = any(get_slot_for_item(it) == SLOT_ONE_PIECE for it in base_combo)
                if len(base_combo) >= 3 or (has_one_piece and len(base_combo) >= 2):
                    candidate_combinations.append(list(base_combo))

                # Option 2: Core + Footwear + Accessory
                valid_acc = [a for a in acc_pool if float(a.get('selling_price') or 0) <= rem_after_base and a not in base_combo]
                if valid_acc:
                    candidate_combinations.append(base_combo + [valid_acc[0]])

                # Option 3: Core + Footwear + Bag
                valid_bags = [b for b in bag_pool if float(b.get('selling_price') or 0) <= rem_after_base and b not in base_combo]
                if valid_bags:
                    candidate_combinations.append(base_combo + [valid_bags[0]])

                # Option 4: Full 4-piece look (Core + Footwear + Bag + Accessory)
                if valid_bags and valid_acc:
                    bag_item = valid_bags[0]
                    rem_after_bag = rem_after_base - float(bag_item.get('selling_price') or 0)
                    acc_candidates_4p = [a for a in valid_acc if float(a.get('selling_price') or 0) <= rem_after_bag and a != bag_item]
                    if acc_candidates_4p:
                        candidate_combinations.append(base_combo + [bag_item, acc_candidates_4p[0]])


        # Score and rank all combinations
        scored_outfits = []
        seen_compositions = set()

        for combo in candidate_combinations:
            # Prevent duplicate item IDs in same outfit
            ids = [c.get('product_id') or c.get('id') for c in combo if c]
            if len(ids) != len(set(ids)):
                continue

            comp_key = tuple(sorted(str(i) for i in ids))
            if comp_key in seen_compositions:
                continue

            res = cls.score_outfit(
                combo,
                target_occasion=occasion,
                target_style=style,
                preferred_colors=preferred_colors,
                budget=budget
            )
            if res['valid']:
                seen_compositions.add(comp_key)
                outfit_dir = classify_outfit_fashion_direction(combo)

                # Calculate original (MRP) strike-through price and discount
                tot_p = res['total_price']
                raw_base = sum(float(it.get('base_price') or it.get('selling_price') * 1.25) for it in combo)
                original_price = raw_base if raw_base > tot_p else round(tot_p * 1.22)
                discount_pct = max(round(((original_price - tot_p) / original_price) * 100), 12) if original_price > tot_p else 15

                scored_outfits.append({
                    'items': combo,
                    'total_price': tot_p,
                    'original_price': original_price,
                    'discount_percent': discount_pct,
                    'remaining_budget': res['remaining_budget'],
                    'has_preferred_color': res.get('has_preferred_color', True),
                    'score': res['score'],
                    'color_score': res['color_score'],
                    'style_score': res['style_score'],
                    'occasion_score': res['occasion_score'],
                    'explanation': res['explanation'],
                    'fashion_direction': outfit_dir,
                })

        # Ensure diversity if Surprise Me or All
        clean_dir = (fashion_direction or 'Surprise Me').strip()
        if clean_dir in ('Surprise Me', 'All') and len(scored_outfits) > 1:
            # Group by direction and interleave
            grouped: Dict[str, List[Dict[str, Any]]] = {}
            for out in scored_outfits:
                grouped.setdefault(out['fashion_direction'], []).append(out)

            for d in grouped:
                grouped[d].sort(key=lambda x: (x.get('has_preferred_color', True), x['score'], -x['total_price']), reverse=True)

            interleaved = []
            max_depth = max(len(lst) for lst in grouped.values())
            for idx in range(max_depth):
                for d in ['Western', 'Ethnic', 'Indo-Western', 'Dresses & Jumpsuits']:
                    if d in grouped and idx < len(grouped[d]):
                        interleaved.append(grouped[d][idx])

            scored_outfits = interleaved if interleaved else scored_outfits
        else:
            scored_outfits.sort(key=lambda x: (x.get('has_preferred_color', True), x['score'], -x['total_price']), reverse=True)

        # Slice results and assign editorial presentation metadata
        final_results = []
        tags = ['Most Popular', 'Best Match', 'Atelier Pick', 'Trending Look', 'Editor\'s Choice', 'Budget Icon']

        for idx, out in enumerate(scored_outfits[:max_results]):
            f_dir = out['fashion_direction']
            out_id = f"look-{idx + 1}"
            index_str = f"{idx + 1:02d}"
            name = generate_outfit_title(f_dir, style, idx)
            tag = tags[idx % len(tags)]
            desc = generate_outfit_description(out['items'], f_dir, occasion, style)

            final_results.append({
                'id': out_id,
                'index_number': index_str,
                'name': name,
                'tag': tag,
                'fashion_direction': f_dir,
                'description': desc,
                'items': out['items'],
                'total_price': out['total_price'],
                'original_price': out['original_price'],
                'discount_percent': out['discount_percent'],
                'remaining_budget': out['remaining_budget'],
                'score': out['score'],
                'color_score': out['color_score'],
                'style_score': out['style_score'],
                'occasion_score': out['occasion_score'],
                'explanation': out['explanation'],
            })

        return final_results

