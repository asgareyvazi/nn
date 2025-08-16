# File: utils.py
# Purpose: Shared helpers (time/str/validation), small formatting utils reused across modules.

from datetime import datetime

def hhmm_to_str(h: int, m: int) -> str:
    h = max(0, min(23, int(h))); m = max(0, min(59, int(m)))
    return f"{h:02d}:{m:02d}:00"

def parse_hhmmss(s: str):
    if not s: return (0, 0, 0)
    try:
        parts = [int(p) for p in s.split(":")]
        if len(parts) == 2: parts.append(0)
        return parts[0], parts[1], parts[2]
    except Exception:
        return (0, 0, 0)

def minutes_between(a: str, b: str) -> int:
    ah, am, _ = parse_hhmmss(a); bh, bm, _ = parse_hhmmss(b)
    a_min = ah*60 + am; b_min = bh*60 + bm
    if b_min < a_min: b_min += 24*60
    return max(0, b_min - a_min)

def now_utc_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"
