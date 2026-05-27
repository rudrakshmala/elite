"""
forex_market_adapter.py — Global Forex Market Adapter
=======================================================
Data:      yfinance with =X suffix (free forex data)
Execution: Alpaca Paper Account (same keys you already have!)
Context:   Global macroeconomic data, Federal Reserve, ECB, currency inflation

NOTE: Uses your EXISTING Alpaca API keys from config.py — no new keys needed!
"""

import math
import yfinance as yf
import config
from market_adapter import BaseMarketAdapter


class ForexMarketAdapter(BaseMarketAdapter):
    """
    Adapter for Global Forex market.
    - Uses =X suffix for yfinance forex data (e.g., EURUSD=X)
    - Executes via Alpaca paper account (same keys as US stocks)
    - CrewAI context focused on global macro, Fed, ECB, inflation
    """

    def __init__(self):
        self._client = None
        self._init_alpaca()

    def _init_alpaca(self):
        """Initialize Alpaca client with existing config keys."""
        try:
            from alpaca.trading.client import TradingClient
            api_key = getattr(config, 'API_KEY', '')
            secret_key = getattr(config, 'SECRET_KEY', '')
            if api_key and secret_key:
                self._client = TradingClient(api_key, secret_key, paper=True)
                print("   ✅ Alpaca connected for Forex execution (Paper Mode)")
            else:
                print("   ⚠️ Alpaca keys not set. Forex execution disabled.")
        except Exception as e:
            print(f"   ⚠️ Alpaca init failed: {e}")
            self._client = None

    # ── Properties ──

    @property
    def market_name(self) -> str:
        return "Global Forex"

    @property
    def currency_symbol(self) -> str:
        return "$"

    # ── Ticker Universe ──

    def get_pairs_universe(self) -> list:
        """
        Forex currency pairs for statistical arbitrage.
        Uses yfinance =X format for free forex data.
        These are CORRELATED currency pairs — perfect for Z-Score mean-reversion.
        """
        return [
            ("EURUSD=X", "GBPUSD=X"),      # European Majors (highly correlated)
            ("USDJPY=X", "USDCHF=X"),      # Safe Haven pair
            ("AUDUSD=X", "NZDUSD=X"),      # Oceanic twins (very high correlation)
            ("EURJPY=X", "GBPJPY=X"),      # Yen crosses
            ("EURGBP=X", "EURCHF=X"),      # Euro crosses
            ("USDCAD=X", "USDNOK=X"),      # Commodity currencies
            ("GBPCHF=X", "GBPJPY=X"),      # Sterling crosses
            ("AUDJPY=X", "NZDJPY=X"),      # Risk-on Yen crosses
        ]

    def get_single_universe(self) -> list:
        """Major forex pairs for momentum scanning."""
        return [
            "EURUSD=X", "GBPUSD=X", "USDJPY=X", "USDCHF=X",
            "AUDUSD=X", "NZDUSD=X", "USDCAD=X", "EURGBP=X",
            "EURJPY=X", "GBPJPY=X", "AUDJPY=X", "EURAUD=X",
            "EURCHF=X", "GBPCHF=X", "GBPAUD=X", "CADJPY=X",
        ]

    # ── Data Methods ──

    def get_price(self, symbol: str) -> float:
        """Fetch latest forex price from yfinance (=X tickers)."""
        try:
            df = yf.download(symbol, period="1d", interval="1m", progress=False)
            if not df.empty:
                return float(df['Close'].iloc[-1].squeeze())
        except Exception as e:
            print(f"      ⚠️ FX price fetch failed for {symbol}: {e}")
        return 0.0

    # ── Execution Methods (Alpaca Paper) ──
    # Note: Alpaca doesn't natively trade spot FX, but supports
    # fractional shares. For real forex, you'd use OANDA/IG.
    # Here we use Alpaca paper for simulation + logging.

    def submit_order(self, symbol: str, qty, side: str, **kwargs) -> bool:
        """
        Submit order via Alpaca.
        For forex, we simulate by logging the trade since Alpaca 
        doesn't support spot FX directly. The paper account tracks it.
        """
        if not self._client:
            print(f"      ⚠️ Alpaca not connected. Simulating {side} {qty} {symbol}")
            return False

        try:
            from alpaca.trading.requests import MarketOrderRequest
            from alpaca.trading.enums import OrderSide, TimeInForce

            # Clean up the forex symbol for Alpaca
            # Alpaca uses symbols like "EUR/USD" not "EURUSD=X"
            clean_symbol = symbol.replace("=X", "")
            # Convert EURUSD -> EUR/USD format
            if len(clean_symbol) == 6:
                clean_symbol = f"{clean_symbol[:3]}/{clean_symbol[3:]}"

            order_side = OrderSide.BUY if side.upper() == "BUY" else OrderSide.SELL

            self._client.submit_order(MarketOrderRequest(
                symbol=clean_symbol,
                qty=qty,
                side=order_side,
                time_in_force=TimeInForce.GTC
            ))
            print(f"      ✅ Alpaca FX Order: {side} {qty} {clean_symbol}")
            return True
        except Exception as e:
            # Forex orders may fail on Alpaca paper — log but don't crash
            print(f"      ⚠️ FX order logged (Alpaca may not support spot FX): {e}")
            print(f"      📝 SIMULATED: {side} {qty} {symbol}")
            return False

    def get_positions(self) -> list:
        """Get open positions from Alpaca."""
        if not self._client:
            return []
        try:
            positions = self._client.get_all_positions()
            return [{
                "symbol": p.symbol,
                "qty": float(p.qty),
                "side": str(p.side),
                "unrealized_pl": float(p.unrealized_pl),
                "current_price": float(p.current_price),
            } for p in positions]
        except Exception:
            return []

    def close_all_positions(self) -> bool:
        """Close all positions via Alpaca."""
        if not self._client:
            return False
        try:
            self._client.close_all_positions(cancel_orders=True)
            print("      ✂️ All Forex positions closed")
            return True
        except Exception as e:
            print(f"      ❌ Error closing FX positions: {e}")
            return False

    def get_buying_power(self) -> float:
        """Get buying power from Alpaca account."""
        if not self._client:
            return 0.0
        try:
            return float(self._client.get_account().buying_power)
        except Exception:
            return 0.0

    # ── CrewAI Context ──

    def get_crew_context(self) -> str:
        return (
            "You are analyzing the GLOBAL FOREX MARKET. "
            "Focus on: Global macroeconomic data, Federal Reserve interest rate decisions, "
            "ECB monetary policy, Bank of Japan interventions, "
            "currency inflation rates across major economies, "
            "Non-Farm Payrolls (NFP), CPI/PPI data releases, "
            "geopolitical tensions affecting safe-haven currencies (JPY, CHF, USD), "
            "commodity prices (oil, gold) impact on AUD, CAD, NOK, "
            "and carry trade dynamics. "
            "All analysis should consider pip-based risk management. "
            "Active trading hours: 6:00 PM to 2:00 AM IST (overlaps with London/NY sessions)."
        )
