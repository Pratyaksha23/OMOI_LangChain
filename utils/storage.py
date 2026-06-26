import json
import os
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE_PATH = os.path.join(BASE_DIR, "data", "journal_entries.json")

def clear_entries():
    if os.path.exists(FILE_PATH):
        os.remove(FILE_PATH)

def load_entries():
    if not os.path.exists(FILE_PATH):
        return []
    with open(FILE_PATH, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_entry(entry):
    entries = load_entries()
    entry["date"] = datetime.now().strftime("%Y-%m-%d")
    entry["timestamp"] = datetime.now().isoformat()
    entries.append(entry)
    with open(FILE_PATH, "w") as f:
        json.dump(entries, f, indent=4)

def get_entries_by_date_range(start_date, end_date):
    entries = load_entries()
    return [e for e in entries if start_date <= e.get("date", "") <= end_date]

def get_last_n_days(n=7):
    today = datetime.now().date()
    start = today - timedelta(days=n - 1)
    return get_entries_by_date_range(start.isoformat(), today.isoformat())

def get_entries_for_day(date_str):
    return get_entries_by_date_range(date_str, date_str)

def get_last_entry_time():
    """Returns the most recent timestamp across all entries, or None if empty."""
    entries = load_entries()
    timestamps = [e.get("timestamp") for e in entries if e.get("timestamp")]
    if not timestamps:
        return None
    return max(timestamps)   # ISO strings sort correctly as strings

def can_add_entry():
    """
    Returns (allowed: bool, message: str | None).
    message is only set when allowed is False, explaining time remaining.
    """
    last_time = get_last_entry_time()
    if last_time is None:
        return True, None

    last_dt = datetime.fromisoformat(last_time)
    elapsed = datetime.now() - last_dt

    if elapsed < timedelta(hours=24):
        remaining = timedelta(hours=24) - elapsed
        hours = int(remaining.total_seconds() // 3600)
        minutes = int((remaining.total_seconds() % 3600) // 60)
        return False, f"You can write your next entry in {hours}h {minutes}m."

    return True, None