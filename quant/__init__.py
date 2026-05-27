"""
Elite-Bot Quant Brain — Institutional-Grade Signal Layer
---------------------------------------------------------
Modules:
  kalman_filter    → Dynamic hedge ratio (replaces static price ratio)
  garch_model      → Volatility regime gate (Green/Yellow/Red)
  hmm_regime       → Market regime detection (HMM)
  kelly_criterion  → Optimal position sizing from trade history
  sentiment_engine → News + Fear & Greed sentiment signal
  quant_brain      → Master orchestrator producing QuantSignal
"""
from .quant_brain import QuantBrain, QuantSignal, get_quant_signal

__all__ = ["QuantBrain", "QuantSignal", "get_quant_signal"]
