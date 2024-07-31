from datetime import date
import os
import json

import httpx

from .shared import PLUGIN_CACHE_FOLDER

ANMA_URL = r"https://cdn.jsdelivr.net/gh/NoPlagiarism/AnMaSearchTerms@master/all.min.json"
ANMA_CACHE_FILE = os.path.join(PLUGIN_CACHE_FOLDER, "anma_data.json") if PLUGIN_CACHE_FOLDER else None
DAYS_CACHE_ALIVE = 7

def check_cache():
    if PLUGIN_CACHE_FOLDER is None:
        return
    if not os.path.exists(PLUGIN_CACHE_FOLDER):
        os.makedirs(PLUGIN_CACHE_FOLDER)
    if not os.path.exists(ANMA_CACHE_FILE):
        return False
    try:
        with open(ANMA_CACHE_FILE, mode="r", encoding="utf-8") as f:
            raw_data = json.load(f)
    except Exception:
        return False
    if "data" not in raw_data:
        return False
    try:
        dt = date.fromisoformat(raw_data["data"])
        return (date.today() - dt).days >= DAYS_CACHE_ALIVE
    except Exception:
        return False

def load_cache():
    if check_cache():
        with open(ANMA_CACHE_FILE, mode="r", encoding="utf-8") as f:
            return json.load(f)["data"]

def get_anma_data():
    if check_cache():
        return load_cache()
    
    resp = httpx.get(ANMA_URL, headers={"User-Agent": "ShikiFlow"})
    data = resp.json()
    
    # Cache
    if PLUGIN_CACHE_FOLDER is not None:
        with open(ANMA_CACHE_FILE, mode="w+", encoding="utf-8") as f:
            json.dump({"date": date.today().isoformat(), "data": data}, f)
    
    return data
