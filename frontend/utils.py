# frontend/utils.py
import requests
import os
from typing import List, Dict

BACKEND = os.getenv("BACKEND_URL", "http://localhost:8000")

def fetch_expenses_from_backend(expense_date):
    r = requests.get(f"{BACKEND}/expenses/{expense_date}")
    r.raise_for_status()
    return r.json()

def push_expenses_to_backend(expense_date, items: List[Dict]):
    r = requests.post(f"{BACKEND}/expenses/{expense_date}", json=items)
    r.raise_for_status()
    return r.json()

def get_analytics_from_backend(start_date, end_date):
    url = f"{BACKEND}/analytics/"
    payload = {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat()
    }
    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json()