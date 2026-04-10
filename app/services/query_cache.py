import hashlib
import json
import time

_CACHE = {}

def build_cache_key(question: str, top_k: int) -> str:
    raw = json.dumps(
        {"question": question.strip().lower(), "top_k": top_k},
        sort_keys=True,
    )
    return hashlib.sha256(raw.encode()).hexdigest()

def get_cached_answer(question: str, top_k: int):
    key = build_cache_key(question, top_k)
    item = _CACHE.get(key)
    if not item:
        return None
    if time.time() > item["expires_at"]:
        _CACHE.pop(key, None)
        return None
    return item["value"]

def set_cached_answer(question: str, top_k: int, value, ttl_seconds: int = 3600):
    key = build_cache_key(question, top_k)
    _CACHE[key] = {
        "value": value,
        "expires_at": time.time() + ttl_seconds,
    }
