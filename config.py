# config.py
import os

# ELITE TRADER - TAURIC RISK PROTOCOL
RISK_CONFIG = {
    "HARD_STOP_LOSS": -100.00,      # Kill switch (Instant Liquidation)
    "SOFT_STOP_LOSS": -75.00,       # Warning (Reduce position size by 50%)
    "DAILY_PROFIT_TARGET": 1000.00, # Lock-in (Stop trading for the day)
    "MAX_SECTOR_EXPOSURE": 0.25     # Max 25% of capital in one sector
}

# Top-level aliases for elite_trader_ai
DAILY_PROFIT_TARGET = RISK_CONFIG["DAILY_PROFIT_TARGET"]
DAILY_STOP_LOSS = RISK_CONFIG["HARD_STOP_LOSS"]

# Fee-Aware Trading (0.1% per side; 4 sides = Entry+Exit for both tickers)
FEE_PER_SIDE = 0.001

# --- Universal Risk Management (Percentage-Based) ---
# These work for both ₹ (INR) and $ (USD) / pips
TRAILING_STOP_PCT = 2.0       # 2% trailing stop-loss
POSITION_RISK_PCT = 10.0      # Max 10% of buying power per trade
FEE_PCT = 0.1                 # 0.1% fee per side

def __getattr__(name):
    if name == "API_KEY":
        return os.environ.get("ALPACA_API_KEY", "PKIVON6P3CB46V4DMNTOARVZC7")
    elif name == "SECRET_KEY":
        return os.environ.get("ALPACA_SECRET_KEY", "AzWsCd7mZ8sYWtkMGuv6o4JC5yQRkeW6on244w1aesp1")
    elif name == "BASE_URL":
        paper = os.environ.get("ALPACA_PAPER", "true").lower() == "true"
        return "https://paper-api.alpaca.markets/v2" if paper else "https://api.alpaca.markets/v2"
    elif name == "UPSTOX_ACCESS_TOKEN":
        return os.environ.get("UPSTOX_ACCESS_TOKEN", "")
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")