# api/fetch_products.py

import requests
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import FAKESTORE_URL, DUMMYJSON_URL

# ──────────────────────────────────────────────────────────
def fetch_fakestore_products():
    """
    FakeStore API se saare products fetch karo
    URL: https://fakestoreapi.com/products
    Returns: list of product dicts
    """
    print("FakeStore se products fetch ho rahe hain...")
    try:
        response = requests.get(f"{FAKESTORE_URL}/products", timeout=10)
        response.raise_for_status()           # 4xx/5xx pe error throw karo
        products = response.json()
        print(f"{len(products)} products mile")
        return products

    except requests.exceptions.ConnectionError:
        print("Internet connection check karo")
        return []
    except requests.exceptions.Timeout:
        print("Request timeout ho gayi")
        return []
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return []


# ──────────────────────────────────────────────────────────
def fetch_dummyjson_products():
    """
    DummyJSON API se products fetch karo — pagination ke saath
    URL: https://dummyjson.com/products?limit=30&skip=0
    Returns: list of product dicts
    """
    print("DummyJSON se products fetch ho rahe hain...")
    all_products = []
    skip  = 0
    limit = 30        # ek baar mein 30 products

    while True:
        try:
            url= f"{DUMMYJSON_URL}/products?limit={limit}&skip={skip}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data  = response.json()
            batch = data.get("products", [])

            if not batch:
                break                         # aur koi product nahi

            all_products.extend(batch)
            print(f"{skip // limit + 1}. page: {len(batch)} products")

            skip += limit
            if skip >= data.get("total", 0):
                break                         # sabhi pages aa gaye

        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            break

    print(f"Total {len(all_products)} products mile")
    return all_products
