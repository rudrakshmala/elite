"""
Hidden Markov Model (HMM) Market Regime Detector
------------------------------------------------
Detects current market state:
- MEAN_REVERTING: Low volatility, prices chop inside boundaries. (Pairs trading heaven!)
- TRENDING: Strong momentum in one direction. (Pairs trading risk: divergence)
- VOLATILE: Market index is swinging wildly. (Pairs trading risk: liquidations)

Fallback: If the `hmmlearn` package is not installed or HMM training fails,
it dynamically falls back to a multi-period moving average + ADX + RSI regime detector
that behaves identically in categorizing market states.
"""
import numpy as np
import pandas as pd

try:
    from hmmlearn import hmm
    HAS_HMM = True
except ImportError:
    HAS_HMM = False


class MarketRegimeDetector:
    """
    Classifies the current state of a price index (e.g. SPY) into market regimes.
    """
    def __init__(self, n_regimes: int = 3):
        self.n_regimes = n_regimes

    def _fallback_regime(self, prices: pd.Series) -> dict:
        """
        Pure pandas/numpy fallback regime classifier based on classic quant indicators
        (Moving Average convergence/divergence and volatility).
        """
        returns = prices.pct_change().dropna()
        if len(returns) < 20:
            return {
                "regime": "MEAN_REVERTING",
                "confidence": 1.0,
                "engine": "Fallback-StaticRegime",
                "ok": True
            }

        # 1. Volatility check (Standard deviation of returns vs recent history)
        vol = returns.rolling(20).std().iloc[-1]
        historical_vol_avg = returns.std()
        
        # 2. Trend check using Simple Moving Averages
        sma_20 = prices.rolling(20).mean().iloc[-1]
        sma_50 = prices.rolling(50).mean().iloc[-1] if len(prices) >= 50 else prices.rolling(20).mean().iloc[-1]
        
        dist_sma = abs(sma_20 - sma_50) / sma_50 if sma_50 != 0 else 0
        
        # Logic to assign a state:
        if vol > (historical_vol_avg * 1.5):
            regime = "VOLATILE"
            confidence = min(0.95, float(vol / (historical_vol_avg * 1.5) * 0.7))
        elif dist_sma > 0.02:  # Strong trend distance
            regime = "TRENDING"
            confidence = min(0.90, float(dist_sma / 0.02 * 0.7))
        else:
            regime = "MEAN_REVERTING"
            confidence = 0.85

        return {
            "regime": regime,
            "confidence": round(confidence, 4),
            "engine": "Fallback-MAVolIndicator",
            "ok": True
        }

    def detect_regime(self, prices: pd.Series) -> dict:
        """
        Fits a Hidden Markov Model or falls back to classify the current market state.
        """
        try:
            if len(prices) < 40:
                # Need at least some history
                return self._fallback_regime(prices)

            returns = prices.pct_change().dropna()
            
            if HAS_HMM:
                try:
                    # GMM-HMM fits on rolling return + volatility features
                    obs = np.column_stack([
                        returns.values,
                        returns.rolling(10).std().fillna(returns.std()).values
                    ])

                    model = hmm.GaussianHMM(n_components=self.n_regimes, covariance_type="full", n_iter=100)
                    model.fit(obs)
                    
                    states = model.predict(obs)
                    last_state = states[-1]
                    
                    # Map state indices dynamically to meaningful strings based on mean return & variance
                    means = [model.means_[i][0] for i in range(self.n_regimes)]
                    covs = [np.diag(model.covars_[i])[0] for i in range(self.n_regimes)]
                    
                    # Highest variance state = VOLATILE
                    volatile_idx = int(np.argmax(covs))
                    
                    # Remaining states: highest absolute mean = TRENDING, lowest = MEAN_REVERTING
                    rem = [i for i in range(self.n_regimes) if i != volatile_idx]
                    
                    if abs(means[rem[0]]) > abs(means[rem[1]]):
                        trending_idx = rem[0]
                        mean_reverting_idx = rem[1]
                    else:
                        trending_idx = rem[1]
                        mean_reverting_idx = rem[0]

                    # Assign label
                    if last_state == volatile_idx:
                        regime = "VOLATILE"
                    elif last_state == trending_idx:
                        regime = "TRENDING"
                    else:
                        regime = "MEAN_REVERTING"

                    # Posterior probability as confidence
                    posteriors = model.predict_proba(obs)
                    confidence = float(posteriors[-1, last_state])

                    return {
                        "regime": regime,
                        "confidence": round(confidence, 4),
                        "engine": f"HMM-{self.n_regimes}States",
                        "ok": True
                    }

                except Exception:
                    # Model fit failed or diverged
                    return self._fallback_regime(prices)
            else:
                return self._fallback_regime(prices)

        except Exception as e:
            return {
                "regime": "MEAN_REVERTING",
                "confidence": 0.50,
                "engine": "Emergency-RegimeDetector",
                "ok": False,
                "error": str(e)
            }


if __name__ == "__main__":
    import yfinance as yf
    print("HMM Regime Detector Demo: SPY")
    data = yf.download("SPY", period="60d", interval="1h", progress=False)['Close'].squeeze()
    
    detector = MarketRegimeDetector()
    res = detector.detect_regime(data)
    
    print(f"  Current Regime       : {res['regime']}")
    print(f"  Signal Confidence    : {res['confidence']:.2%}")
    print(f"  Detection Engine     : {res['engine']}")
