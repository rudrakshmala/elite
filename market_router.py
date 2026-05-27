"""
market_router.py — Time-Aware Market Router
==============================================
Automatically selects the correct market adapter based on IST time.

Schedule (Asia/Kolkata IST):
  09:15 AM – 03:30 PM  →  Indian NSE (Day Mode)
  06:00 PM – 02:00 AM  →  Forex Market (Night Mode)
  Other times           →  Cooldown / Sleep
"""

import datetime

try:
    import pytz
    IST = pytz.timezone('Asia/Kolkata')
except ImportError:
    # Fallback: use UTC+5:30 offset if pytz not installed
    IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))


def get_ist_now():
    """Get current time in IST."""
    try:
        return datetime.datetime.now(IST)
    except Exception:
        # Fallback for systems without pytz
        return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30)))


def get_active_market_name() -> str:
    """
    Returns which market is active right now based on IST time.
    Returns: 'indian', 'forex', or 'cooldown'
    """
    now = get_ist_now()
    current_time = now.time()

    # Indian Market: 09:15 AM – 03:30 PM IST
    indian_open = datetime.time(9, 15)
    indian_close = datetime.time(15, 30)

    # Forex Market: 06:00 PM – 02:00 AM IST (next day)
    forex_open = datetime.time(18, 0)
    forex_close_midnight = datetime.time(23, 59, 59)
    forex_close_morning = datetime.time(2, 0)

    if indian_open <= current_time <= indian_close:
        return "indian"
    elif current_time >= forex_open or current_time <= forex_close_morning:
        return "forex"
    else:
        return "cooldown"


def get_active_adapter():
    """
    Returns the correct adapter instance based on current IST time.
    Returns None during cooldown periods.
    """
    market = get_active_market_name()

    if market == "indian":
        from indian_market_adapter import IndianMarketAdapter
        return IndianMarketAdapter()
    elif market == "forex":
        from forex_market_adapter import ForexMarketAdapter
        return ForexMarketAdapter()
    else:
        return None


def get_next_session_info() -> dict:
    """
    Returns info about the current/next trading session.
    Useful for display in the CLI and dashboard.
    """
    now = get_ist_now()
    current_time = now.time()
    market = get_active_market_name()

    if market == "indian":
        close_time = datetime.time(15, 30)
        remaining = datetime.datetime.combine(now.date(), close_time) - datetime.datetime.combine(now.date(), current_time)
        return {
            "active": True,
            "market": "Indian NSE",
            "emoji": "🇮🇳",
            "closes_at": "03:30 PM IST",
            "remaining_minutes": int(remaining.total_seconds() / 60),
        }
    elif market == "forex":
        return {
            "active": True,
            "market": "Global Forex",
            "emoji": "🌍",
            "closes_at": "02:00 AM IST",
            "remaining_minutes": None,  # Complex to calc across midnight
        }
    else:
        # Calculate time until next session
        indian_open = datetime.time(9, 15)
        forex_open = datetime.time(18, 0)

        if current_time < indian_open:
            next_market = "Indian NSE"
            next_emoji = "🇮🇳"
            next_time = "09:15 AM IST"
            delta = datetime.datetime.combine(now.date(), indian_open) - datetime.datetime.combine(now.date(), current_time)
        elif current_time < forex_open:
            next_market = "Global Forex"
            next_emoji = "🌍"
            next_time = "06:00 PM IST"
            delta = datetime.datetime.combine(now.date(), forex_open) - datetime.datetime.combine(now.date(), current_time)
        else:
            next_market = "Indian NSE"
            next_emoji = "🇮🇳"
            next_time = "09:15 AM IST (Tomorrow)"
            delta = datetime.timedelta(hours=12)  # Approximate

        return {
            "active": False,
            "market": "Cooldown",
            "emoji": "💤",
            "next_session": next_market,
            "next_emoji": next_emoji,
            "opens_at": next_time,
            "wait_minutes": int(delta.total_seconds() / 60),
        }


def print_session_status():
    """Print a nice status banner for the current session."""
    info = get_next_session_info()

    if info["active"]:
        print(f"\n   {info['emoji']} ACTIVE: {info['market']}")
        print(f"   ⏰ Closes at {info['closes_at']}")
        if info.get("remaining_minutes"):
            print(f"   ⏳ {info['remaining_minutes']} minutes remaining")
    else:
        print(f"\n   {info['emoji']} COOLDOWN — No active market right now")
        print(f"   ⏭️  Next: {info.get('next_emoji', '')} {info.get('next_session', 'Unknown')}")
        print(f"   🕐 Opens at {info.get('opens_at', 'Unknown')}")
        wait = info.get('wait_minutes', 0)
        if wait:
            hours, mins = divmod(wait, 60)
            print(f"   ⏳ Wait: {hours}h {mins}m")
