from datetime import datetime, date
from typing import Optional, Tuple

def get_today_str() -> str:
    return date.today().strftime("%Y-%m-%d")

def calculate_days_since(date_str: Optional[str]) -> int:
    if not date_str:
        return 999
    try:
        past = datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
        today = date.today()
        diff = (today - past).days
        return max(0, diff)
    except Exception:
        return 999

def get_urgency_tier(days: int) -> Tuple[str, str]:
    """
    Returns (tier_code, label)
    tier_code: 'fresh' | 'due_soon' | 'due' | 'overdue'
    """
    if days <= 3:
        return "fresh", "Fresh (< 4 days)"
    elif days <= 7:
        return "due_soon", "Due Soon (4-7 days)"
    elif days <= 14:
        return "due", "Revision Due (8-14 days)"
    else:
        return "overdue", "Overdue (> 14 days)"
