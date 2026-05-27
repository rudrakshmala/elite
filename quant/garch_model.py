"""
GARCH(1,1) Volatility Forecasting Gate
---------------------------------------
Fits a Generalized Autoregressive Conditional Heteroskedasticity model
on recent historical returns to predict the volatility of the spread or asset.

Provides the following risk tiers:
- GREEN: Forecasted volatility is low/normal. Trade at 100% of sizing.
- YELLOW: Volatility is elevated. Trade at 50% sizing (risk-reduced mode).
- RED: Volatility is extremely high. Skip the trade completely (safety lock).

Fallback: If the `arch` package is not installed or the model fails to converge,
it gracefully falls back to a robust exponential rolling standard deviation (EWMA).
"""
import numpy as np
import pandas as pd

# Try to import arch, but don't crash if missing
try:
    from arch import arch_model
    HAS_ARCH = True
except ImportError:
    HAS_ARCH = False


class GarchVolModel:
    """
    Fits and forecasts volatility using GARCH(1,1) with dynamic robust fallback.
    """
    def __init__(self, green_threshold: float = 0.20, red_threshold: float = 0.35):
        """
        green_threshold: Annualized vol <= 20% is Green
        red_threshold: Annualized vol >= 35% is Red (Skip)
        Anything in between is Yellow (Half size)
        """
        self.green_threshold = green_threshold
        self.red_threshold = red_threshold

    def _fallback_vol(self, returns: pd.Series) -> float:
        """
        Fallback volatility metric: Annualized Exponentially Weighted Moving Standard Deviation.
        Very robust, never fails to converge.
        """
        # Exponential rolling std dev (decay factor span of 20 periods)
        ewma_std = returns.ewm(span=20).std().iloc[-1]
        
        # Annualization factor: Assumes hourly data (252 days * 6.5 hours = 1638 trading hours)
        # Or if daily data, sqrt(252). We'll assume a robust generic hourly scale: sqrt(1638).
        # Let's check sample frequency or use a robust standard generic scale.
        # Default multiplier for annualized vol:
        # Assuming ~ hourly signals. Let's use 1638.
        annualized_factor = np.sqrt(1638)
        
        # Safe clipping
        val = float(ewma_std * annualized_factor)
        if np.isnan(val) or np.isinf(val):
            # Safe baseline standard deviation
            return float(returns.std() * np.sqrt(252))
        return val

    def predict_volatility(self, series: pd.Series) -> dict:
        """
        Fits a GARCH(1,1) model and returns forecasted volatility and risk tier.
        """
        try:
            # 1. Compute percentage returns
            returns = series.pct_change().dropna()
            
            # If data is empty or too short, return green baseline
            if len(returns) < 20:
                return {
                    "forecasted_vol": 0.15,
                    "tier": "GREEN",
                    "scale_factor": 1.0,
                    "model_used": "baseline",
                    "ok": True
                }

            # Pre-scaling returns for numeric stability (GARCH struggles with small decimals)
            scaled_returns = returns * 100.0

            forecasted_vol_ann = 0.0
            model_used = "GARCH(1,1)"

            if HAS_ARCH:
                try:
                    # GARCH(1,1) is the standard volatility model used in quant funds
                    model = arch_model(scaled_returns, vol='Garch', p=1, q=1, dist='Normal', show_warning=False)
                    res = model.fit(disp='off', show_warning=False)
                    
                    # 1-step ahead forecast
                    forecast = res.forecast(horizon=1)
                    
                    # GARCH variance is returned scaled (* 100^2), we scale it back
                    next_var = forecast.variance.iloc[-1].values[0] / 10000.0
                    
                    # Convert to annualized volatility (assuming hourly)
                    forecasted_vol_ann = np.sqrt(next_var) * np.sqrt(1638)
                    
                    # Fallback check for NaN or infinite outputs
                    if np.isnan(forecasted_vol_ann) or np.isinf(forecasted_vol_ann):
                        raise ValueError("Invalid volatility output")
                except Exception:
                    # Inner fallback: model did not converge
                    forecasted_vol_ann = self._fallback_vol(returns)
                    model_used = "Fallback-EWMA (Convergence failure)"
            else:
                forecasted_vol_ann = self._fallback_vol(returns)
                model_used = "Fallback-EWMA (arch package not installed)"

            # Determine risk tier and position sizing scale factor
            if forecasted_vol_ann >= self.red_threshold:
                tier = "RED"
                scale_factor = 0.0
            elif forecasted_vol_ann >= self.green_threshold:
                tier = "YELLOW"
                scale_factor = 0.5
            else:
                tier = "GREEN"
                scale_factor = 1.0

            return {
                "forecasted_vol": round(forecasted_vol_ann, 4),
                "tier": tier,
                "scale_factor": scale_factor,
                "model_used": model_used,
                "ok": True
            }

        except Exception as e:
            return {
                "forecasted_vol": 0.20,
                "tier": "GREEN",
                "scale_factor": 1.0,
                "model_used": "Emergency Baseline",
                "ok": False,
                "error": str(e)
            }


if __name__ == "__main__":
    # Demo code to run and test self
    import yfinance as yf
    print("GARCH Volatility Gate Demo: SPY")
    data = yf.download("SPY", period="30d", interval="1h", progress=False)['Close'].squeeze()
    
    garch = GarchVolModel()
    res = garch.predict_volatility(data)
    
    print(f"  Forecasted Volatility (Ann): {res['forecasted_vol']:.2%}")
    print(f"  Volatility Risk Tier       : {res['tier']}")
    print(f"  Position Sizing Factor     : {res['scale_factor']}")
    print(f"  Model Engine Used          : {res['model_used']}")
