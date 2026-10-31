import json
import os
import hashlib
import hmac
from typing import Dict, Any

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")

DEFAULT_CONFIG = {
    "app_name": "Minimal DSA Tracker",
    "trip_name": "3 Months DSA Learning Trip",
    "trip_start_date": "2026-10-31",
    "trip_duration_days": 90,
    "trip_target_problems": 150,
    "trip_manifesto": "Master core Data Structures & Algorithms, solve 150+ high-yield LeetCode problems, and build strong problem-solving intuition through active revision.",
    "leetcode_username": "",
    "auth_enabled": True,
    "auth_pin_hash": hashlib.sha256("1234".encode()).hexdigest(),
    "session_secret": "dsa-tracker-secret-key-2026"
}

def load_config() -> Dict[str, Any]:
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Fill any missing keys with defaults
            for k, v in DEFAULT_CONFIG.items():
                if k not in data:
                    data[k] = v
            return data
    except Exception as e:
        print(f"Error reading config: {e}")
        return DEFAULT_CONFIG.copy()

def save_config(new_config: Dict[str, Any]) -> bool:
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(new_config, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

def hash_pin(pin: str) -> str:
    return hashlib.sha256(pin.strip().encode()).hexdigest()

def verify_pin(pin: str) -> bool:
    cfg = load_config()
    if not cfg.get("auth_enabled", True):
        return True
    return hash_pin(pin) == cfg.get("auth_pin_hash")

def generate_session_token() -> str:
    cfg = load_config()
    secret = cfg.get("session_secret", "dsa-tracker-secret-key-2026")
    pin_hash = cfg.get("auth_pin_hash", "")
    token = hmac.new(secret.encode(), pin_hash.encode(), hashlib.sha256).hexdigest()
    return token

def verify_session_token(token: str) -> bool:
    cfg = load_config()
    if not cfg.get("auth_enabled", True):
        return True
    expected = generate_session_token()
    return hmac.compare_digest(token or "", expected)
