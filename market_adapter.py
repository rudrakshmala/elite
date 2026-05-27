"""
market_adapter.py — Strategy Pattern Base Interface
=====================================================
Abstract class that all market adapters must implement.
This wraps the existing yfinance + broker logic WITHOUT touching
any Z-Score math, RL brain, or CrewAI agent definitions.
"""

from abc import ABC, abstractmethod
import yfinance as yf
import pandas as pd


class BaseMarketAdapter(ABC):
    """
    Abstract interface for market-specific data + execution.
    Each adapter provides its own:
        - Ticker universe (pairs)
        - Price fetching
        - Z-Score calculation (reuses the SAME math formula)
        - Order execution via its broker SDK
        - CrewAI context string for dynamic prompt injection
    """

    @property
    @abstractmethod
    def market_name(self) -> str:
        """Human-readable market name, e.g. 'Indian NSE' or 'Global Forex'."""
        ...

    @property
    @abstractmethod
    def currency_symbol(self) -> str:
        """Currency symbol for display, e.g. '₹' or '$'."""
        ...

    @abstractmethod
    def get_pairs_universe(self) -> list:
        """Return list of (ticker_a, ticker_b) tuples for this market."""
        ...

    @abstractmethod
    def get_single_universe(self) -> list:
        """Return list of single tickers for momentum scanning."""
        ...

    @abstractmethod
    def get_price(self, symbol: str) -> float:
        """Fetch the latest price for a symbol."""
        ...

    @abstractmethod
    def submit_order(self, symbol: str, qty, side: str, **kwargs) -> bool:
        """
        Place an order via the market's broker.
        side: 'BUY' or 'SELL'
        Returns True if order placed successfully.
        """
        ...

    @abstractmethod
    def get_positions(self) -> list:
        """Return list of open positions."""
        ...

    @abstractmethod
    def close_all_positions(self) -> bool:
        """Close all open positions. Returns True on success."""
        ...

    @abstractmethod
    def get_buying_power(self) -> float:
        """Return available buying power / cash in the account."""
        ...

    @abstractmethod
    def get_crew_context(self) -> str:
        """
        Return market-specific context string for CrewAI prompt injection.
        This does NOT modify agent definitions — it's appended to task descriptions.
        """
        ...

    # ═══════════════════════════════════════════════════════════════
    # SHARED MATH — Identical Z-Score formula used across all markets
    # This is the SAME calculation from elite_trader_ai.py, untouched.
    # ═══════════════════════════════════════════════════════════════

    def calculate_z_score(self, sym_a: str, sym_b: str, window: int = 20):
        """
        Z-Score calculation — REUSES the exact same math from elite_trader_ai.py.
        No modifications to the rolling window, threshold, or signal logic.
        """
        try:
            data_a = yf.download(sym_a, period="5d", interval="1h", progress=False)['Close'].squeeze()
            data_b = yf.download(sym_b, period="5d", interval="1h", progress=False)['Close'].squeeze()

            df = pd.DataFrame({sym_a: data_a, sym_b: data_b}).dropna()
            if len(df) < window:
                return None, "HOLD"

            df['ratio'] = df[sym_a] / df[sym_b]
            mean = df['ratio'].rolling(window=window).mean()
            std = df['ratio'].rolling(window=window).std()
            df['z_score'] = (df['ratio'] - mean) / std

            last_z = df['z_score'].iloc[-1]

            signal = "HOLD"
            if last_z < -1.5:
                signal = "BUY_PAIR"
            elif last_z > 1.5:
                signal = "SELL_PAIR"

            return last_z, signal
        except Exception:
            return None, "HOLD"

    # ═══════════════════════════════════════════════════════════════
    # UNIVERSAL RISK MANAGEMENT — Percentage-based (works for ₹ and $)
    # ═══════════════════════════════════════════════════════════════

    def calculate_risk_pct(self, entry_price: float, current_price: float) -> float:
        """
        Calculate P&L as a percentage — universal for INR, USD, pips.
        Returns: percentage change (e.g., 2.5 means +2.5%)
        """
        if entry_price <= 0:
            return 0.0
        return ((current_price - entry_price) / entry_price) * 100.0

    def calculate_trailing_stop_price(self, entry_price: float, trail_pct: float = 2.0) -> float:
        """
        Calculate trailing stop price based on percentage.
        trail_pct: e.g., 2.0 means stop at 2% below entry.
        """
        return entry_price * (1 - trail_pct / 100.0)

    def calculate_fees_pct(self, fee_rate: float = 0.001) -> float:
        """
        Fee as a percentage of trade value.
        Default 0.1% per side (same as config.FEE_PER_SIDE).
        """
        return fee_rate * 100.0

    def calculate_position_size(self, buying_power: float, price: float,
                                 risk_pct: float = 10.0) -> int:
        """
        Calculate position size using percentage of buying power.
        risk_pct: percentage of buying power to use (e.g., 10 = 10%).
        Returns integer quantity.
        """
        if price <= 0:
            return 0
        budget = buying_power * (risk_pct / 100.0)
        import math
        return math.floor(budget / price)
