# services/analytics_service.py
# Database se KPIs nikalo

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_connection import get_connection


def get_total_products():
    """Kitne products hain total?"""
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM products")
    result = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return result


def get_total_users():
    """Kitne users hain?"""
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    result = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return result


def get_total_orders():
    """Kitne orders hain?"""
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM orders")
    result = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return result


def get_total_revenue():
    """Saare orders ka total revenue"""
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ROUND(SUM(total_price), 2) FROM orders")
    result = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return float(result or 0)


def get_category_stats():
    """Har category mein products count aur price stats"""
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            category,
            COUNT(*)             AS total_products,
            ROUND(AVG(price), 2) AS avg_price,
            ROUND(MIN(price), 2) AS min_price,
            ROUND(MAX(price), 2) AS max_price
        FROM products
        GROUP BY category
        ORDER BY total_products DESC
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [
        {
            "category":       r[0],
            "total_products": r[1],
            "avg_price":      float(r[2]),
            "min_price":      float(r[3]),
            "max_price":      float(r[4]),
        }
        for r in rows
    ]


def get_top_rated_products(limit=10):
    """Sabse zyada rating wale products"""
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT title, category, price, rating, rating_count
        FROM products
        WHERE rating > 0
        ORDER BY rating DESC, rating_count DESC
        LIMIT %s
    """, (limit,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [
        {
            "title":        r[0],
            "category":     r[1],
            "price":        float(r[2]),
            "rating":       float(r[3]),
            "rating_count": r[4],
        }
        for r in rows
    ]


def get_price_ranges():
    """Price range mein products ki count"""
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            CASE
                WHEN price < 20  THEN 'Under $20'
                WHEN price < 50  THEN '$20 to $50'
                WHEN price < 100 THEN '$50 to $100'
                ELSE 'Above $100'
            END AS price_range,
            COUNT(*) AS count
        FROM products
        GROUP BY price_range
        ORDER BY count DESC
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [{"range": r[0], "count": r[1]} for r in rows]


def get_source_wise_count():
    """Kaun se API se kitne products aaye"""
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT source_api, COUNT(*) AS count
        FROM products
        GROUP BY source_api
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [{"source": r[0], "count": r[1]} for r in rows]


def get_all_kpis():
    """Ek baar mein saare KPIs"""
    return {
        "total_products": get_total_products(),
        "total_users":    get_total_users(),
        "total_orders":   get_total_orders(),
        "total_revenue":  get_total_revenue(),
        "category_stats": get_category_stats(),
        "top_rated":      get_top_rated_products(10),
        "price_ranges":   get_price_ranges(),
        "source_stats":   get_source_wise_count(),
    }
