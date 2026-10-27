"""
Operation A: Digital Wardrobe Table Creation & Verification
TARIKA Fashion Retail

Executes the additive DDL for wardrobe_items and verifies table structure and constraints.
"""

import os
import psycopg2
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(env_path)

conn = psycopg2.connect(
    dbname=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT')
)
cur = conn.cursor()

try:
    print("Executing Operation A: Creating wardrobe_items table and index...")
    ddl_sql = """
    CREATE TABLE IF NOT EXISTS wardrobe_items (
        id BIGSERIAL PRIMARY KEY,
        customer_id TEXT NOT NULL,
        item_name VARCHAR(255) NOT NULL,
        category VARCHAR(100) NOT NULL,
        subcategory VARCHAR(100),
        primary_color VARCHAR(100) NOT NULL,
        secondary_color VARCHAR(100),
        style_tag VARCHAR(100) NOT NULL DEFAULT 'Casual',
        occasion VARCHAR(100) NOT NULL DEFAULT 'Casual',
        season VARCHAR(100) DEFAULT 'All Season',
        material VARCHAR(100),
        image_url TEXT,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
    );

    CREATE INDEX IF NOT EXISTS idx_wardrobe_customer ON wardrobe_items(customer_id);
    """
    cur.execute(ddl_sql)
    conn.commit()
    print("Operation A DDL executed successfully.")

    # Verification 1: Table exists
    cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'wardrobe_items');")
    table_exists = cur.fetchone()[0]
    print(f"Table 'wardrobe_items' exists: {table_exists}")
    if not table_exists:
        raise RuntimeError("Verification failed: wardrobe_items table does not exist after creation.")

    # Verification 2: Columns
    cur.execute("SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = 'wardrobe_items' ORDER BY ordinal_position;")
    cols = cur.fetchall()
    print(f"Columns verified ({len(cols)} columns):")
    for c in cols:
        print(f"  {c[0]} ({c[1]}, nullable={c[2]})")

    # Verification 3: Indexes
    cur.execute("SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'wardrobe_items';")
    indexes = cur.fetchall()
    print("Indexes verified:")
    for idx in indexes:
        print(f"  {idx[0]}: {idx[1]}")

    # Verification 4: Row count
    cur.execute("SELECT COUNT(*) FROM wardrobe_items;")
    count = cur.fetchone()[0]
    print(f"Initial row count in wardrobe_items: {count}")

    print("\nOPERATION A VERIFIED SUCCESSFULLY.")

except Exception as e:
    conn.rollback()
    print(f"OPERATION A FAILED: {e}")
    raise e
finally:
    cur.close()
    conn.close()
