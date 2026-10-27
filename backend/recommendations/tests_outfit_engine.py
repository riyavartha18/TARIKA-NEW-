"""
Unit Tests for Outfit Compatibility Engine
TARIKA Fashion Retail

Tests category grammar, color harmony, style cohesion, occasion matching,
budget compliance, explanation generation, and outfit assembly with seed items.
"""

from unittest import TestCase
from decimal import Decimal
from recommendations.outfit_engine import (
    OutfitCompatibilityEngine,
    get_slot_for_item,
    evaluate_color_harmony,
    evaluate_style_cohesion,
    evaluate_occasion_match,
    generate_explanation,
    SLOT_TOP,
    SLOT_BOTTOM,
    SLOT_ONE_PIECE,
    SLOT_FOOTWEAR,
    SLOT_BAG,
    SLOT_ACCESSORY,
    SLOT_LAYER
)
from recommendations.metadata_enrichment import (
    normalize_color,
    get_color_compatibility,
    infer_product_metadata
)


class OutfitGrammarTests(TestCase):
    """Verifies category grammar rules for complete, realistic fashion outfits."""

    def setUp(self):
        self.top = {'product_id': 't1', 'category_name': 'T-Shirts', 'product_name': 'Classic Polo', 'selling_price': 799, 'color': 'Navy Blue'}
        self.kurti = {'product_id': 'k1', 'category_name': 'Kurtis', 'product_name': 'Floral Straight Kurti', 'selling_price': 1199, 'color': 'Mustard'}
        self.bottom = {'product_id': 'b1', 'category_name': 'Trousers', 'product_name': 'Slim Fit Chinos', 'selling_price': 1299, 'color': 'Beige'}
        self.palazzo = {'product_id': 'p1', 'category_name': 'Bottom Wear', 'product_name': 'Flared Cotton Palazzo', 'selling_price': 899, 'color': 'White'}
        self.dress = {'product_id': 'd1', 'category_name': 'Dresses', 'product_name': 'A-Line Midi Dress', 'selling_price': 1999, 'color': 'Emerald Green'}
        self.saree = {'product_id': 's1', 'category_name': 'Sarees', 'product_name': 'Kanjeevaram Silk Saree', 'selling_price': 4999, 'color': 'Maroon'}
        self.shoes = {'product_id': 'f1', 'category_name': 'Footwear', 'product_name': 'Classic Leather Loafers', 'selling_price': 1899, 'color': 'Tan'}
        self.bag = {'product_id': 'bg1', 'category_name': 'Handbags', 'product_name': 'Structured Shoulder Tote', 'selling_price': 1499, 'color': 'Black'}
        self.earrings = {'product_id': 'a1', 'category_name': 'Accessories', 'product_name': 'Kundan Drop Earrings', 'selling_price': 599, 'color': 'Gold'}
        self.dupatta = {'product_id': 'l1', 'category_name': 'Ethnic Wear', 'product_name': 'Banarasi Silk Dupatta', 'selling_price': 999, 'color': 'Red'}

    def test_slot_assignment(self):
        """Checks accurate slot assignment based on category and keyword heuristics."""
        self.assertEqual(get_slot_for_item(self.top), SLOT_TOP)
        self.assertEqual(get_slot_for_item(self.kurti), SLOT_TOP)
        self.assertEqual(get_slot_for_item(self.bottom), SLOT_BOTTOM)
        self.assertEqual(get_slot_for_item(self.palazzo), SLOT_BOTTOM)
        self.assertEqual(get_slot_for_item(self.dress), SLOT_ONE_PIECE)
        self.assertEqual(get_slot_for_item(self.saree), SLOT_ONE_PIECE)
        self.assertEqual(get_slot_for_item(self.shoes), SLOT_FOOTWEAR)
        self.assertEqual(get_slot_for_item(self.bag), SLOT_BAG)
        self.assertEqual(get_slot_for_item(self.earrings), SLOT_ACCESSORY)
        self.assertEqual(get_slot_for_item(self.dupatta), SLOT_LAYER)

    def test_valid_top_bottom_footwear(self):
        """Top + Bottom + Footwear is a valid core outfit."""
        outfit = [self.top, self.bottom, self.shoes]
        self.assertTrue(OutfitCompatibilityEngine.validate_grammar(outfit))

    def test_valid_one_piece_footwear(self):
        """One-Piece (Dress/Saree) + Footwear is a valid core outfit."""
        outfit = [self.dress, self.shoes]
        self.assertTrue(OutfitCompatibilityEngine.validate_grammar(outfit))

    def test_valid_outfit_with_accessories_and_bag(self):
        """Outfits with optional accessories and bags are valid."""
        outfit = [self.kurti, self.palazzo, self.shoes, self.dupatta, self.earrings, self.bag]
        self.assertTrue(OutfitCompatibilityEngine.validate_grammar(outfit))

    def test_invalid_duplicate_tops(self):
        """Two tops without a bottom is invalid."""
        outfit = [self.top, self.kurti, self.shoes]
        self.assertFalse(OutfitCompatibilityEngine.validate_grammar(outfit))

    def test_invalid_duplicate_bottoms(self):
        """Two bottoms without a top is invalid."""
        outfit = [self.bottom, self.palazzo, self.shoes]
        self.assertFalse(OutfitCompatibilityEngine.validate_grammar(outfit))

    def test_invalid_one_piece_with_bottom(self):
        """Cannot combine a one-piece dress/saree with trousers."""
        outfit = [self.dress, self.bottom, self.shoes]
        self.assertFalse(OutfitCompatibilityEngine.validate_grammar(outfit))

    def test_invalid_multiple_footwear(self):
        """An outfit cannot have 2 pairs of footwear."""
        shoes2 = {'product_id': 'f2', 'category_name': 'Footwear', 'product_name': 'Kolhapuri Sandals', 'selling_price': 899, 'color': 'Brown'}
        outfit = [self.top, self.bottom, self.shoes, shoes2]
        self.assertFalse(OutfitCompatibilityEngine.validate_grammar(outfit))

    def test_invalid_incomplete_outfit(self):
        """Only accessories or shoes without clothes is invalid."""
        self.assertFalse(OutfitCompatibilityEngine.validate_grammar([self.shoes, self.bag]))
        self.assertFalse(OutfitCompatibilityEngine.validate_grammar([self.top]))


class OutfitColorAndStyleTests(TestCase):
    """Verifies color harmony, style cohesion, and occasion scoring."""

    def test_color_normalization(self):
        """Color normalization maps raw variants to canonical color names."""
        self.assertEqual(normalize_color('navy blue'), 'Navy Blue')
        self.assertEqual(normalize_color('marigold yellow'), 'Mustard')
        self.assertEqual(normalize_color('off-white'), 'Off-White')
        self.assertEqual(normalize_color('emerald green'), 'Emerald Green')
        self.assertEqual(normalize_color('rani pink'), 'Pink')
        self.assertEqual(normalize_color(''), 'Multi')

    def test_color_compatibility_neutrals_and_festive(self):
        """High compatibility for neutral pairings and classic festive pairings."""
        # Neutral + Neutral
        self.assertGreaterEqual(get_color_compatibility('White', 'Navy Blue'), 0.85)
        self.assertGreaterEqual(get_color_compatibility('Black', 'Beige'), 0.85)
        # Indian festive pairing: Pink + Yellow
        self.assertGreaterEqual(get_color_compatibility('Pink', 'Yellow'), 0.80)
        # Same color monochromatic
        self.assertEqual(get_color_compatibility('Black', 'Black'), 1.0)

    def test_style_cohesion_scoring(self):
        """Evaluates harmonious styles vs clashing styles."""
        traditional_items = [
            {'product_name': 'Anarkali Kurti', 'category_name': 'Kurtis', 'color': 'Red'},
            {'product_name': 'Banarasi Silk Dupatta', 'category_name': 'Ethnic Wear', 'color': 'Gold'},
            {'product_name': 'Embroidered Jutti', 'category_name': 'Footwear', 'color': 'Gold'}
        ]
        trad_score = evaluate_style_cohesion(traditional_items)
        self.assertGreaterEqual(trad_score, 0.85)

        clashing_items = [
            {'product_name': 'Kanjeevaram Saree', 'category_name': 'Sarees', 'color': 'Red'},
            {'product_name': 'Oversized Street Graphic Hoodie', 'category_name': 'T-Shirts', 'color': 'Black'}
        ]
        clash_score = evaluate_style_cohesion(clashing_items)
        self.assertLessEqual(clash_score, 0.50)

    def test_occasion_matching(self):
        """Matches items suited for target occasions."""
        festive_items = [
            {'product_name': 'Silk Saree for Diwali Festive Puja', 'category_name': 'Sarees'},
            {'product_name': 'Kundan Festive Jhumkas', 'category_name': 'Accessories'}
        ]
        score = evaluate_occasion_match(festive_items, 'Festive')
        self.assertEqual(score, 1.0)

        score_casual = evaluate_occasion_match(festive_items, 'Casual')
        self.assertEqual(score_casual, 0.0)


class OutfitBudgetAndAssemblyTests(TestCase):
    """Verifies strict budget capping, owned item zero-cost deduction, and outfit ranking."""

    def setUp(self):
        self.candidates = [
            {'product_id': 't1', 'category_name': 'T-Shirts', 'product_name': 'Casual Crewneck', 'selling_price': 500, 'color': 'Navy Blue', 'in_stock': True},
            {'product_id': 't2', 'category_name': 'T-Shirts', 'product_name': 'Premium Polo', 'selling_price': 1500, 'color': 'White', 'in_stock': True},
            {'product_id': 'b1', 'category_name': 'Trousers', 'product_name': 'Slim Chinos', 'selling_price': 800, 'color': 'Beige', 'in_stock': True},
            {'product_id': 'b2', 'category_name': 'Trousers', 'product_name': 'Formal Trousers', 'selling_price': 2200, 'color': 'Black', 'in_stock': True},
            {'product_id': 'f1', 'category_name': 'Footwear', 'product_name': 'Canvas Sneakers', 'selling_price': 600, 'color': 'White', 'in_stock': True},
            {'product_id': 'f2', 'category_name': 'Footwear', 'product_name': 'Leather Oxford Shoes', 'selling_price': 2800, 'color': 'Brown', 'in_stock': True},
            {'product_id': 'a1', 'category_name': 'Accessories', 'product_name': 'Leather Belt', 'selling_price': 300, 'color': 'Brown', 'in_stock': True},
        ]

    def test_strict_budget_enforcement(self):
        """Score_outfit returns valid=False if total price exceeds budget."""
        # Total price: 1500 + 2200 + 2800 = 6500
        expensive_outfit = [self.candidates[1], self.candidates[3], self.candidates[5]]
        result = OutfitCompatibilityEngine.score_outfit(expensive_outfit, budget=3000)
        self.assertFalse(result['valid'])
        self.assertEqual(result['score'], 0)
        self.assertIn('exceeds budget', result['reason'])

    def test_budget_compliant_outfit(self):
        """Score_outfit succeeds when total price <= budget."""
        # Total price: 500 + 800 + 600 = 1900 <= 2000
        affordable_outfit = [self.candidates[0], self.candidates[2], self.candidates[4]]
        result = OutfitCompatibilityEngine.score_outfit(affordable_outfit, budget=2000)
        self.assertTrue(result['valid'])
        self.assertGreater(result['score'], 50)
        self.assertEqual(result['total_price'], 1900)
        self.assertEqual(result['remaining_budget'], 100)
        self.assertTrue(len(result['explanation']) > 10)

    def test_owned_wardrobe_items_cost_zero(self):
        """Owned items in digital wardrobe have is_owned=True and do not count toward budget."""
        owned_jeans = {
            'product_id': 'w_b1',
            'category_name': 'Trousers',
            'product_name': 'My Favorite Denim',
            'selling_price': 1999,
            'color': 'Blue',
            'is_owned': True
        }
        # Only top (500) and shoes (600) are purchased = 1100
        outfit = [self.candidates[0], owned_jeans, self.candidates[4]]
        result = OutfitCompatibilityEngine.score_outfit(outfit, budget=1200)
        self.assertTrue(result['valid'])
        self.assertEqual(result['total_price'], 1100)
        self.assertEqual(result['remaining_budget'], 100)

    def test_assemble_outfits_ranking(self):
        """Assemble_outfits produces budget-compliant combinations sorted by score."""
        outfits = OutfitCompatibilityEngine.assemble_outfits(
            candidate_items=self.candidates,
            budget=2500,
            occasion='Casual',
            complete_outfit=False,
            max_results=5
        )
        self.assertGreater(len(outfits), 0)
        for out in outfits:
            self.assertLessEqual(out['total_price'], 2500)
            self.assertTrue(out['score'] > 0)
            self.assertTrue(len(out['items']) >= 3)

    def test_style_with_what_you_own_seed_item(self):
        """Assemble_outfits anchors all combinations to the provided seed item."""
        seed_kurti = {
            'product_id': 'seed_k1',
            'category_name': 'Kurtis',
            'product_name': 'Owned Floral Yellow Kurti',
            'selling_price': 1200,
            'color': 'Yellow',
            'is_owned': True
        }
        catalog_pool = list(self.candidates)

        outfits = OutfitCompatibilityEngine.assemble_outfits(
            candidate_items=catalog_pool,
            budget=2000,
            seed_item=seed_kurti,
            max_results=3
        )
        self.assertGreater(len(outfits), 0)
        for out in outfits:
            # Every outfit must include the seed item
            item_ids = [it.get('product_id') for it in out['items']]
            self.assertIn('seed_k1', item_ids)
            # Seed item is owned, so its price shouldn't increase out['total_price']
            self.assertLessEqual(out['total_price'], 2000)


class MultiCategoryAndStylistTests(TestCase):
    """Verifies support for Western, Ethnic, Indo-Western, Dresses & Jumpsuits, and Surprise Me."""

    def setUp(self):
        self.catalog = [
            # Western Tops & Bottoms
            {'product_id': 'w_top_1', 'category_name': 'Tops', 'product_name': 'Ribbed Crop Top', 'selling_price': 499, 'color': 'Pink', 'in_stock': True},
            {'product_id': 'w_jean_1', 'category_name': 'Jeans', 'product_name': 'High Rise Wide Leg Jeans', 'selling_price': 899, 'color': 'Navy Blue', 'in_stock': True},
            {'product_id': 'w_trouser_1', 'category_name': 'Trousers', 'product_name': 'Tailored Straight Trousers', 'selling_price': 899, 'color': 'Black', 'in_stock': True},

            # Ethnic Tops & Bottoms & Sarees
            {'product_id': 'e_kurti_1', 'category_name': 'Kurtis', 'product_name': 'Embroidered Anarkali Kurti', 'selling_price': 999, 'color': 'Pink', 'in_stock': True},
            {'product_id': 'e_palazzo_1', 'category_name': 'Bottom Wear', 'product_name': 'Flared Cotton Palazzo', 'selling_price': 699, 'color': 'White', 'in_stock': True},
            {'product_id': 'e_saree_1', 'category_name': 'Sarees', 'product_name': 'Banarasi Silk Saree', 'selling_price': 1499, 'color': 'Maroon', 'in_stock': True},

            # Dresses & Jumpsuits & Co-ords
            {'product_id': 'd_dress_1', 'category_name': 'Dresses', 'product_name': 'Floral A-Line Midi Dress', 'selling_price': 1199, 'color': 'Emerald Green', 'in_stock': True},
            {'product_id': 'd_jumpsuit_1', 'category_name': 'Dresses', 'product_name': 'Belted Linen Jumpsuit', 'selling_price': 1299, 'color': 'Beige', 'in_stock': True},
            {'product_id': 'd_coord_1', 'category_name': 'Co-ord Set', 'product_name': 'Summer Printed Co-ord Set', 'selling_price': 1399, 'color': 'Yellow', 'in_stock': True},

            # Footwear (Western & Ethnic)
            {'product_id': 'f_sneaker_1', 'category_name': 'Footwear', 'product_name': 'Minimalist White Sneakers', 'selling_price': 599, 'color': 'White', 'in_stock': True},
            {'product_id': 'f_jutti_1', 'category_name': 'Footwear', 'product_name': 'Handcrafted Juttis', 'selling_price': 499, 'color': 'Gold', 'in_stock': True},

            # Bags (Western & Ethnic)
            {'product_id': 'b_bag_1', 'category_name': 'Handbags', 'product_name': 'Structured Shoulder Bag', 'selling_price': 299, 'color': 'Beige', 'in_stock': True},
            {'product_id': 'b_potli_1', 'category_name': 'Handbags', 'product_name': 'Embroidered Velvet Potli Bag', 'selling_price': 249, 'color': 'Pink', 'in_stock': True},

            # Accessories
            {'product_id': 'a_jhumka_1', 'category_name': 'Accessories', 'product_name': 'Kundan Floral Jhumkas', 'selling_price': 199, 'color': 'Gold', 'in_stock': True},
        ]

    def test_western_outfit_generation(self):
        """Assembles valid Western looks respecting budget."""
        outfits = OutfitCompatibilityEngine.assemble_outfits(
            candidate_items=self.catalog,
            budget=2500,
            fashion_direction='Western',
            max_results=3
        )
        self.assertGreater(len(outfits), 0)
        for out in outfits:
            self.assertEqual(out['fashion_direction'], 'Western')
            self.assertLessEqual(out['total_price'], 2500)
            self.assertGreaterEqual(out['remaining_budget'], 0)

    def test_ethnic_outfit_generation(self):
        """Assembles valid Ethnic looks with Kurti/Palazzo or Saree."""
        outfits = OutfitCompatibilityEngine.assemble_outfits(
            candidate_items=self.catalog,
            budget=2500,
            fashion_direction='Ethnic',
            max_results=3
        )
        self.assertGreater(len(outfits), 0)
        for out in outfits:
            self.assertEqual(out['fashion_direction'], 'Ethnic')
            self.assertLessEqual(out['total_price'], 2500)

    def test_indo_western_fusion_generation(self):
        """Generates Indo-Western fusion looks combining ethnic and western pieces."""
        outfits = OutfitCompatibilityEngine.assemble_outfits(
            candidate_items=self.catalog,
            budget=2500,
            fashion_direction='Indo-Western',
            max_results=3
        )
        self.assertGreater(len(outfits), 0)
        for out in outfits:
            self.assertEqual(out['fashion_direction'], 'Indo-Western')
            self.assertLessEqual(out['total_price'], 2500)

    def test_dresses_and_jumpsuits_generation(self):
        """Generates One-Piece dress and jumpsuit outfits without separate top/bottom."""
        outfits = OutfitCompatibilityEngine.assemble_outfits(
            candidate_items=self.catalog,
            budget=2500,
            fashion_direction='Dresses & Jumpsuits',
            max_results=3
        )
        self.assertGreater(len(outfits), 0)
        for out in outfits:
            self.assertEqual(out['fashion_direction'], 'Dresses & Jumpsuits')
            # One piece check
            slots = [get_slot_for_item(it) for it in out['items']]
            self.assertEqual(slots.count(SLOT_ONE_PIECE), 1)
            self.assertEqual(slots.count(SLOT_TOP), 0)
            self.assertEqual(slots.count(SLOT_BOTTOM), 0)
            self.assertLessEqual(out['total_price'], 2500)

    def test_surprise_me_diversity(self):
        """Surprise Me returns multiple diverse categories within budget."""
        outfits = OutfitCompatibilityEngine.assemble_outfits(
            candidate_items=self.catalog,
            budget=3000,
            fashion_direction='Surprise Me',
            max_results=6
        )
        self.assertGreater(len(outfits), 1)
        found_dirs = {out['fashion_direction'] for out in outfits}
        self.assertGreater(len(found_dirs), 1, "Surprise Me should return varied categories")

