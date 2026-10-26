"""
Safe Synthetic Seed Runner & Verification
TARIKA Fashion Retail

Strict safety guarantees:
  - Atomic transaction: all 115 records succeed together or none are committed.
  - Zero overwrites: pre-flight check validates that no product_id or SKU collides with existing records.
  - Foreign key verification: validates categories, manufacturers, and warehouses before any insert.
  - Generates immutable manifest of actual inserted IDs.
  - Dry-run mode by default: requires explicit '--execute' flag to perform database writes.
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone
import psycopg2
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from catalog.synthetic_indian_catalog import generate_synthetic_catalog_records

def get_db_connection():
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    load_dotenv(env_path)
    return psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )

def run_seed(dry_run=True):
    products, inventory = generate_synthetic_catalog_records()
    print(f"Loaded {len(products)} synthetic products and {len(inventory)} inventory records.")

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Pre-flight 1: Check for SKU collisions
        proposed_skus = [p['sku'] for p in products]
        cur.execute("SELECT sku FROM products WHERE sku = ANY(%s);", (proposed_skus,))
        conflicting_skus = [r[0] for r in cur.fetchall()]
        if conflicting_skus:
            raise RuntimeError(f"ABORTED: Found {len(conflicting_skus)} conflicting SKUs in database: {conflicting_skus}")

        # Pre-flight 2: Check for Product ID collisions
        proposed_pids = [p['product_id'] for p in products]
        cur.execute("SELECT product_id FROM products WHERE product_id = ANY(%s);", (proposed_pids,))
        conflicting_pids = [r[0] for r in cur.fetchall()]
        if conflicting_pids:
            raise RuntimeError(f"ABORTED: Found {len(conflicting_pids)} conflicting product IDs in database: {conflicting_pids}")

        # Pre-flight 3: Check for Inventory ID collisions
        proposed_inv_ids = [inv['inventory_id'] for inv in inventory]
        cur.execute("SELECT inventory_id FROM inventory WHERE inventory_id = ANY(%s);", (proposed_inv_ids,))
        conflicting_inv_ids = [r[0] for r in cur.fetchall()]
        if conflicting_inv_ids:
            raise RuntimeError(f"ABORTED: Found {len(conflicting_inv_ids)} conflicting inventory IDs in database: {conflicting_inv_ids}")

        # Pre-flight 4: Verify Foreign Keys
        cat_ids = list({p['category_id'] for p in products})
        cur.execute("SELECT category_id FROM categories WHERE category_id = ANY(%s);", (cat_ids,))
        found_cats = {r[0] for r in cur.fetchall()}
        missing_cats = set(cat_ids) - found_cats
        if missing_cats:
            raise RuntimeError(f"ABORTED: Missing category IDs in database: {missing_cats}")

        mfg_ids = list({p['manufacturer_id'] for p in products})
        cur.execute("SELECT manufacturer_id FROM manufacturers WHERE manufacturer_id = ANY(%s);", (mfg_ids,))
        found_mfgs = {r[0] for r in cur.fetchall()}
        missing_mfgs = set(mfg_ids) - found_mfgs
        if missing_mfgs:
            raise RuntimeError(f"ABORTED: Missing manufacturer IDs in database: {missing_mfgs}")

        wh_ids = list({inv['warehouse_id'] for inv in inventory})
        cur.execute("SELECT warehouse_id FROM warehouses WHERE warehouse_id = ANY(%s);", (wh_ids,))
        found_whs = {r[0] for r in cur.fetchall()}
        missing_whs = set(wh_ids) - found_whs
        if missing_whs:
            raise RuntimeError(f"ABORTED: Missing warehouse IDs in database: {missing_whs}")

        print("Pre-flight validation passed: 0 collisions, 100% valid foreign keys.")

        if dry_run:
            print("[DRY-RUN] No database modifications were performed. Pass '--execute' to perform writes.")
            return {
                'success': True,
                'dry_run': True,
                'products_count': len(products),
                'inventory_count': len(inventory)
            }

        # Atomic Execution
        now_str = datetime.now(timezone.utc).isoformat()
        product_rows = [
            (
                p['product_id'], p['product_name'], p['category_id'], p['manufacturer_id'],
                p['sku'], p['description'], p['gender'], p['color'], p['size'], p['material'],
                p['cost_price'], p['base_price'], p['selling_price'], p['launch_date'],
                p['is_active'], now_str, now_str
            )
            for p in products
        ]

        insert_prod_sql = """
        INSERT INTO products (
            product_id, product_name, category_id, manufacturer_id,
            sku, description, gender, color, size, material,
            cost_price, base_price, selling_price, launch_date,
            is_active, created_at, updated_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        cur.executemany(insert_prod_sql, product_rows)

        inv_rows = [
            (
                inv['inventory_id'], inv['product_id'], inv['warehouse_id'],
                inv['stock_quantity'], inv['reorder_level'], inv['last_restock_date']
            )
            for inv in inventory
        ]

        insert_inv_sql = """
        INSERT INTO inventory (
            inventory_id, product_id, warehouse_id,
            stock_quantity, reorder_level, last_restock_date
        ) VALUES (%s, %s, %s, %s, %s, %s);
        """
        cur.executemany(insert_inv_sql, inv_rows)

        conn.commit()
        print(f"SUCCESS: Inserted {len(product_rows)} products and {len(inv_rows)} inventory items.")

        # Save actual manifest
        manifest_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'synthetic_seed_manifest_actual.json')
        manifest_data = {
            'executed_at': now_str,
            'total_products': len(products),
            'total_inventory_items': len(inventory),
            'product_ids': proposed_pids,
            'skus': proposed_skus,
            'inventory_ids': proposed_inv_ids,
        }
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest_data, f, indent=2)
        print(f"Saved execution manifest to: {manifest_path}")

        return {
            'success': True,
            'dry_run': False,
            'products_count': len(products),
            'inventory_count': len(inventory),
            'manifest_path': manifest_path
        }

    except Exception as e:
        conn.rollback()
        print(f"FAILED: Transaction rolled back. Reason: {e}")
        raise e
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Synthetic Indian Fashion Catalog Seed Runner")
    parser.add_argument('--execute', action='store_true', help="Perform live database writes (default is dry-run)")
    args = parser.parse_args()

    run_seed(dry_run=not args.execute)
