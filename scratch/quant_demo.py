"""
Quant Brain Dynamic Demo Runner
--------------------------------
Simulates a real trading analysis session for all pairs in PAIRS_UNIVERSE
using live data from Yahoo Finance.

Validates:
1. Kalman Filter dynamic hedge ratio and spread z-score.
2. GARCH(1,1) volatility regime gating.
3. Hidden Markov Model global market regime detection.
4. Kelly Criterion sizer with historical analysis.
5. Macro and micro news/sentiment evaluation.
"""
import os
import sys

# Append root to path
sys.path.insert(0, r"d:\Elite-bot")


from quant.quant_brain import get_quant_signal

PAIRS = [
    ("KO", "PEP"), 
    ("XOM", "CVX"), 
    ("JPM", "BAC"), 
    ("MSFT", "AAPL")
]

print("="*60)
print("     🦅 ELITE-BOT QUANT BRAIN REAL-TIME SIGNAL RUNNER 🦅     ")
print("="*60)

for sym_a, sym_b in PAIRS:
    print(f"\n🔬 Analyzing pair: {sym_a} vs {sym_b} ...")
    try:
        # Generate simulated signals using current real market data
        sig = get_quant_signal(sym_a, sym_b, base_z_score=1.8)
        
        print(f"  ├─ [DECISION] Approved: {sig.approved}")
        print(f"  ├─ [REGIME]   Market Regime: {sig.regime} (confidence: {sig.regime_prob:.0%})")
        print(f"  ├─ [VOLATILITY] Forecasted: {sig.forecasted_vol:.1%} | GARCH Gate: {'PASS' if sig.volatility_ok else 'FAIL'}")
        print(f"  ├─ [SIZING]   Optimal Kelly Fraction: {sig.kelly_fraction:.1%} of budget")
        print(f"  ├─ [SPREAD]   Kalman Dynamic Hedge Ratio: {sig.hedge_ratio:.4f}")
        print(f"  ├─ [SENTIMENT] Net News Sentiment: {sig.sentiment_score:+.2f} | CNN Fear/Greed: {sig.fear_greed}/100")
        print(f"  └─ [EXPLANATION] {sig.reason}")
    except Exception as e:
        print(f"  ❌ Error analyzing {sym_a}/{sym_b}: {e}")

print("\n" + "="*60)
print("✅ Real-time simulation finished successfully.")
print("="*60)
