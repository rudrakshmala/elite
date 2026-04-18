import os
from dotenv import load_dotenv

load_dotenv() # Load keys from .env
API_KEY = os.getenv("ALPACA_API_KEY", "PASTE_YOUR_API_KEY_HERE")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY", "PASTE_YOUR_SECRET_KEY_HERE")

# This URL tells the bot to use the "Paper" (Fake Money) server
# DO NOT CHANGE THIS unless you are ready to lose real money
BASE_URL = "https://paper-api.alpaca.markets/v2"

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