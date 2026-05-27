"""
Kalman Filter — Dynamic Hedge Ratio for Pairs Trading
------------------------------------------------------
Replaces the static price ratio (price_A / price_B) with a
Kalman-filtered rolling hedge ratio that adapts to changing
market microstructure in real-time.

Key insight: A static ratio assumes the relationship between
two stocks never changes. Kalman Filter knows it always does.

Renaissance Medallion uses adaptive hedge ratios. This is why.
"""
import numpy as np
import pandas as pd


class KalmanHedgeFilter:
    """
    Online Kalman Filter estimating the dynamic hedge ratio β between two assets.

    State vector: [β, α]  (hedge ratio + intercept)
    Observation:  price_A = β * price_B + α + noise

    Parameters
    ----------
    delta : float
        Process noise scaling. Higher = faster adaptation (more reactive).
        Lower = smoother (more stable). Default 1e-4 is institutional standard.
    vt : float
        Observation noise variance. Default 1e-3.
    """

    def __init__(self, delta: float = 1e-4, vt: float = 1e-3):
        self.delta = delta
        self.vt = vt

        # State: [β (hedge ratio), α (intercept)]
        self.theta = np.zeros(2)

        # State covariance (uncertainty in our estimate)
        self.P = np.zeros((2, 2))

        # Process noise covariance
        self.W = (delta / (1 - delta)) * np.eye(2)

        self.is_initialized = False
        self._hedge_history = []

    def update(self, price_a: float, price_b: float) -> dict:
        """
        Update filter with one new observation.
        Returns current hedge ratio, intercept, and spread.
        """
        # Observation vector: [price_b, 1]
        F = np.array([price_b, 1.0])

        if not self.is_initialized:
            # Warm-start: naive ratio
            self.theta[0] = price_a / price_b if price_b != 0 else 1.0
            self.theta[1] = 0.0
            self.P = np.eye(2) * 1.0
            self.is_initialized = True

        # --- PREDICT ---
        # State transition: theta stays same (random walk prior)
        # P_pred = P + W
        P_pred = self.P + self.W

        # --- UPDATE ---
        # Innovation (prediction error)
        y_pred = F @ self.theta
        innovation = price_a - y_pred

        # Innovation variance S = F P F^T + vt
        S = float(F @ P_pred @ F.T) + self.vt

        # Kalman Gain K = P F^T / S
        K = (P_pred @ F.T) / S

        # Update state estimate
        self.theta = self.theta + K * innovation

        # Update covariance (Joseph form for numerical stability)
        I_KF = np.eye(2) - np.outer(K, F)
        self.P = I_KF @ P_pred

        hedge_ratio = float(self.theta[0])
        intercept = float(self.theta[1])
        spread = price_a - hedge_ratio * price_b - intercept

        self._hedge_history.append(hedge_ratio)

        return {
            "hedge_ratio": hedge_ratio,
            "intercept": intercept,
            "spread": spread,
        }

    def fit_series(self, prices_a: pd.Series, prices_b: pd.Series) -> pd.DataFrame:
        """
        Fit the entire price history, returning a DataFrame with
        hedge_ratio, intercept, spread, and z_score columns.
        """
        results = []
        for pa, pb in zip(prices_a.values, prices_b.values):
            r = self.update(float(pa), float(pb))
            results.append(r)

        df = pd.DataFrame(results, index=prices_a.index)

        # Compute rolling z-score of the spread (20-period)
        window = min(20, len(df) // 2)
        df["spread_mean"] = df["spread"].rolling(window).mean()
        df["spread_std"] = df["spread"].rolling(window).std()
        df["z_score"] = (df["spread"] - df["spread_mean"]) / df["spread_std"].replace(0, np.nan)

        return df


def get_kalman_signal(prices_a: pd.Series, prices_b: pd.Series,
                      z_threshold: float = 1.5) -> dict:
    """
    High-level function: fits Kalman filter on price history,
    returns the current dynamic hedge ratio and z-score signal.

    Parameters
    ----------
    prices_a, prices_b : pd.Series — aligned price series
    z_threshold : float — z-score level to trigger BUY/SELL signal

    Returns
    -------
    dict with keys:
        hedge_ratio   — current dynamic hedge ratio
        z_score       — current Kalman spread z-score
        signal        — "BUY_PAIR" / "SELL_PAIR" / "HOLD"
        spread_series — full spread history (for charting)
    """
    try:
        kf = KalmanHedgeFilter()
        df = kf.fit_series(prices_a, prices_b)

        last = df.iloc[-1]
        z = last["z_score"]
        hedge = last["hedge_ratio"]

        if pd.isna(z):
            signal = "HOLD"
        elif z < -z_threshold:
            signal = "BUY_PAIR"
        elif z > z_threshold:
            signal = "SELL_PAIR"
        else:
            signal = "HOLD"

        return {
            "hedge_ratio": round(hedge, 4),
            "z_score": round(float(z), 4) if not pd.isna(z) else 0.0,
            "signal": signal,
            "spread_series": df["spread"],
            "ok": True,
        }

    except Exception as e:
        return {
            "hedge_ratio": 1.0,
            "z_score": 0.0,
            "signal": "HOLD",
            "spread_series": None,
            "ok": False,
            "error": str(e),
        }


# ── Quick demo ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import yfinance as yf

    print("Kalman Filter Demo: JPM vs BAC")
    data = yf.download(["JPM", "BAC"], period="30d", interval="1h", progress=False)["Close"].dropna()
    result = get_kalman_signal(data["JPM"], data["BAC"])
    print(f"  Hedge Ratio : {result['hedge_ratio']}")
    print(f"  Z-Score     : {result['z_score']}")
    print(f"  Signal      : {result['signal']}")
