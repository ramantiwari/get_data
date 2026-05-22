# api/fetch_users.py

import requests
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import FAKESTORE_URL, JSONPLACEHOLDER

# ──────────────────────────────────────────────────────────
def fetch_fakestore_users():
    """
    FakeStore API se users fetch karo
    URL: https://fakestoreapi.com/users
    """
    print("FakeStore se users fetch ho rahe hain...")
    try:
        response = requests.get(f"{FAKESTORE_URL}/users", timeout=10)
        response.raise_for_status()
        users = response.json()
        print(f"{len(users)} users mile")
        return users
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return []


# ──────────────────────────────────────────────────────────
def fetch_jsonplaceholder_users():
    """
    JSONPlaceholder se users fetch karo
    URL: https://jsonplaceholder.typicode.com/users
    """
    print("JSONPlaceholder se users fetch ho rahe hain...")
    try:
        response = requests.get(f"{JSONPLACEHOLDER}/users", timeout=10)
        response.raise_for_status()
        users = response.json()
        print(f"{len(users)} users mile")
        return users
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return []


# ──────────────────────────────────────────────────────────
def fetch_fakestore_carts():
    """
    FakeStore se carts fetch karo (yahi hamare orders honge)
    URL: https://fakestoreapi.com/carts
    """
    print("FakeStore se carts fetch ho rahe hain...")
    try:
        response = requests.get(f"{FAKESTORE_URL}/carts", timeout=10)
        response.raise_for_status()
        carts = response.json()
        print(f"{len(carts)} carts mile")
        return carts
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return []
