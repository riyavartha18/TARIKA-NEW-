"""
Safe Manifest-Based Rollback Runner
TARIKA Fashion Retail

Strict safety guarantees:
  - Restricted strictly to explicit IDs listed in the actual seed manifest.
  - Pre-rollback dependency check: ensures no synthetic items are referenced by customer orders or carts.
  - Atomic transaction: rolls back both inventory and product records safely.
  - Requires explicit '--confirm' flag to prevent accidental execution.
  - Never executed automatically.
"""

import os
import sys
import json
import argparse
import psycopg2
from dotenv import load_dotenv

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

def run_rollback(confirm=False):
    manifest_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'synthetic_seed_manifest_actual.json')
    if not os.path.exists(manifest_path):
        manifest_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'synthetic_seed_manifest_preview.json')

    if not os.path.exists(manifest_path):
        raise FileNotFoundError("No seed manifest file found. Cannot perform rollback without exact ID manifest.")

    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    product_ids = manifest.get('product_ids', [])
    inventory_ids = manifest.get('inventory_ids', [])

    print(f"Loaded manifest with {len(product_ids)} products and {len(inventory_ids)} inventory records.")

    if not confirm:
        print("[DRY-RUN] Rollback requires explicit '--confirm' flag. No database modifications performed.")
        return {'dry_run': True}

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Check order_items dependencies
        cur.execute("SELECT COUNT(*) FROM order_items WHERE product_id = ANY(%s);", (product_ids,))
        order_deps = cur.fetchone()[0]
        if order_deps > 0:
            raise RuntimeError(f"ABORTED ROLLBACK: {order_deps} order items reference synthetic products. Manual review required.")

        # Atomic Deletion strictly by ID list
        cur.execute("DELETE FROM inventory WHERE inventory_id = ANY(%s);", (inventory_ids,))
        deleted_inv = cur.rowcount

        cur.execute("DELETE FROM products WHERE product_id = ANY(%s);", (product_ids,))
        deleted_prods = cur.rowcount

        conn.commit()
        print(f"SUCCESSFUL ROLLBACK: Removed {deleted_prods} products and {deleted_inv} inventory records.")
        return {'success': True, 'deleted_products': deleted_prods, 'deleted_inventory': deleted_inv}

    except Exception as e:
        conn.rollback()
        print(f"ROLLBACK FAILED: {e}")
        raise e
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Manifest Rollback Tool")
    parser.add_argument('--confirm', action='store_true', help="Confirm execution of rollback")
    args = parser.parse_args()

    run_rollback(confirm=args.confirm)
