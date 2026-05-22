# services/etl_service.py
# ETL = Extract → Transform → Load

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from database.db_connection import get_connection
from api.fetch_products import fetch_fakestore_products, fetch_dummyjson_products
from api.fetch_users    import fetch_fakestore_users, fetch_jsonplaceholder_users, fetch_fakestore_carts


# ══════════════════════════════════════════════════════════
#   TRANSFORM  —  Raw API data → clean database-ready dict
# ══════════════════════════════════════════════════════════

def clean_fakestore_product(p):
    """FakeStore product ko clean karo"""
    return {
        "id":           p.get("id"),
        "title":        str(p.get("title", ""))[:255],
        "price":        round(float(p.get("price") or 0), 2),
        "category":     str(p.get("category", "")).lower().strip(),
        "rating":       p.get("rating", {}).get("rate", 0),
        "rating_count": p.get("rating", {}).get("count", 0),
        "source_api":   "fakestoreapi",
    }

def clean_dummyjson_product(p):
    """DummyJSON product ko clean karo — ID 1000 se shuru hogi clash avoid karne ke liye"""
    return {
        "id":           p.get("id", 0) + 1000,
        "title":        str(p.get("title", ""))[:255],
        "price":        round(float(p.get("price") or 0), 2),
        "category":     str(p.get("category", "")).lower().strip(),
        "rating":       p.get("rating", 0),
        "rating_count": p.get("stock", 0),
        "source_api":   "dummyjson",
    }

def clean_fakestore_user(u):
    """FakeStore user ko clean karo"""
    name = u.get("name", {})
    addr = u.get("address", {})
    full_name = f"{name.get('firstname', '')} {name.get('lastname', '')}".strip()
    return {
        "id":       u.get("id"),
        "username": u.get("username", full_name),
        "email":    u.get("email", "").lower(),
        "phone":    str(u.get("phone", ""))[:50],
        "city":     addr.get("city", ""),
    }

def clean_jsonplaceholder_user(u):
    """JSONPlaceholder user ko clean karo — ID 100 se shuru hogi"""
    return {
        "id":       u.get("id", 0) + 100,
        "username": u.get("username", ""),
        "email":    u.get("email", "").lower(),
        "phone":    str(u.get("phone", ""))[:50],
        "city":     u.get("address", {}).get("city", ""),
    }


# ══════════════════════════════════════════════════════════
#   LOAD  —  Clean data → MySQL tables
# ══════════════════════════════════════════════════════════

def load_products(conn, products):
    """Products table mein insert karo"""
    cursor = conn.cursor()
    sql = """
        INSERT INTO products (id, title, price, category, rating, rating_count, source_api)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            price        = VALUES(price),
            rating       = VALUES(rating),
            rating_count = VALUES(rating_count)
    """
    count = 0
    for p in products:
        try:
            cursor.execute(sql, (
                p["id"], p["title"], p["price"],
                p["category"], p["rating"],
                p["rating_count"], p["source_api"]
            ))
            count += 1
        except Exception as e:
            print(f"Product ID {p.get('id')} skip: {e}")

    conn.commit()
    cursor.close()
    print(f"{count} products save ho gaye")
    return count


def load_users(conn, users):
    """Users table mein insert karo"""
    cursor = conn.cursor()
    sql = """
        INSERT INTO users (id, username, email, phone, city)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            email = VALUES(email),
            phone = VALUES(phone)
    """
    count = 0
    for u in users:
        try:
            cursor.execute(sql, (
                u["id"], u["username"], u["email"],
                u["phone"], u["city"]
            ))
            count += 1
        except Exception as e:
            print(f"User ID {u.get('id')} skip: {e}")

    conn.commit()
    cursor.close()
    print(f"{count} users save ho gaye")
    return count


def load_orders(conn, carts):
    """Carts ko orders table mein insert karo"""
    cursor = conn.cursor()
    sql = """
        INSERT INTO orders (id, user_id, total_price, products_count, source_api)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            total_price = VALUES(total_price)
    """
    count = 0
    for cart in carts:
        items = cart.get("products", [])
        total = round(sum(
            float(i.get("price", 0)) * int(i.get("quantity", 1))
            for i in items
        ), 2)
        try:
            cursor.execute(sql, (
                cart.get("id"),
                cart.get("userId"),
                total,
                len(items),
                "fakestoreapi"
            ))
            count += 1
        except Exception as e:
            print(f"Order ID {cart.get('id')} skip: {e}")

    conn.commit()
    cursor.close()
    print(f"{count} orders save ho gaye")
    return count


def save_etl_log(conn, table_name, status, records):
    """ETL run ka log save karo"""
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO etl_logs (table_name, status, records) VALUES (%s, %s, %s)",
        (table_name, status, records)
    )
    conn.commit()
    cursor.close()


# ══════════════════════════════════════════════════════════
#   MAIN PIPELINE  —  Sab kuch ek saath chalao
# ══════════════════════════════════════════════════════════

def run_etl():
    start_time = datetime.now()
    print("\n" + "="*52)
    print("ETL PIPELINE SHURU HO RAHA HAI")
    print(f"{start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*52)

    conn = get_connection()
    total = {"products": 0, "users": 0, "orders": 0}

    # ── Step 1: Products ──────────────────────────────────
    print("\n[1/3] PRODUCTS")
    fs_products  = [clean_fakestore_product(p) for p in fetch_fakestore_products()]
    dj_products  = [clean_dummyjson_product(p) for p in fetch_dummyjson_products()]
    all_products = fs_products + dj_products
    total["products"] = load_products(conn, all_products)
    save_etl_log(conn, "products", "success", total["products"])

    # ── Step 2: Users ─────────────────────────────────────
    print("\n[2/3] USERS")
    fs_users   = [clean_fakestore_user(u)       for u in fetch_fakestore_users()]
    jp_users   = [clean_jsonplaceholder_user(u) for u in fetch_jsonplaceholder_users()]
    all_users  = fs_users + jp_users
    total["users"] = load_users(conn, all_users)
    save_etl_log(conn, "users", "success", total["users"])

    # ── Step 3: Orders ────────────────────────────────────
    print("\n[3/3] ORDERS")
    carts = fetch_fakestore_carts()
    total["orders"] = load_orders(conn, carts)
    save_etl_log(conn, "orders", "success", total["orders"])

    conn.close()

    end_time = datetime.now()
    duration = round((end_time - start_time).total_seconds(), 1)

    print("\n" + "="*52)
    print("ETL COMPLETE!")
    print(f"   Products : {total['products']}")
    print(f"   Users    : {total['users']}")
    print(f"   Orders   : {total['orders']}")
    print(f"   Time     : {duration} seconds")
    print("="*52 + "\n")

    return total
