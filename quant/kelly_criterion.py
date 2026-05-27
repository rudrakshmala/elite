"""
Kelly Criterion Position Sizer
------------------------------
Reads Elite-Bot's local transaction and trade journals to dynamically optimize
position sizes instead of using a hardcoded risk multiplier (e.g. static 10%).

Formula:
  Kelly Fraction (f*) = p - (q / b)
  Where:
    p = probability of winning (Win Rate)
    q = probability of losing (1 - p)
    b = win-to-loss ratio (avg profit size / avg loss size)

Applying standard Quant risk mitigation, we default to Half-Kelly (0.5 * f*)
to avoid tail-risk drawdowns and smooth out volatility.
"""
import os
import re
import numpy as np


class KellySizer:
    """
    Parses trade histories to calculate dynamic Kelly fractions.
    """
    def __init__(self, journal_path: str = "trade_journal.txt", 
                 max_fraction: float = 0.20, default_fraction: float = 0.10):
        self.journal_path = journal_path
        self.max_fraction = max_fraction
        self.default_fraction = default_fraction

    def _parse_trade_history(self) -> list:
        """
        Parses trade_journal.txt or fallback logs to extract past profit values.
        """
        pnl_records = []
        
        # Check standard trade journal
        if os.path.exists(self.journal_path):
            try:
                with open(self.journal_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        
                        # Handle Date|PnL style log formats
                        # Example: 2026-05-27|152.50
                        # Example: 2026-05-27|-85.20
                        if "|" in line:
                            parts = line.split("|")
                            if len(parts) >= 2:
                                try:
                                    pnl_records.append(float(parts[1]))
                                except ValueError:
                                    pass
            except Exception:
                pass

        # Try fallback: trade_journal.txt / daily_journal.txt / etc.
        # Parse numbers out of generic strings if standard parsing fails
        if not pnl_records and os.path.exists("trade_journal.txt"):
            try:
                with open("trade_journal.txt", "r", encoding="utf-8") as f:
                    text = f.read()
                    # Find all numbers prefixed with + or - signs or just dollar amounts
                    matches = re.findall(r"[-+]?\d*\.\d+|\d+", text)
                    pnl_records = [float(x) for x in matches]
            except Exception:
                pass
                
        return pnl_records

    def calculate_kelly_fraction(self) -> dict:
        """
        Processes history metrics and calculates dynamic Half-Kelly sizer.
        """
        try:
            records = self._parse_trade_history()
            
            # If we don't have enough trading history (min 5 trades), use default sizing
            if len(records) < 5:
                return {
                    "kelly_fraction": self.default_fraction,
                    "win_rate": 0.50,
                    "win_loss_ratio": 1.0,
                    "total_trades": len(records),
                    "is_dynamic": False,
                    "reason": "Insufficient trade history (<5 trades)"
                }

            pnls = np.array(records)
            
            wins = pnls[pnls > 0]
            losses = pnls[pnls < 0]

            # 1. Win Rate (p)
            win_count = len(wins)
            total_count = len(pnls)
            win_rate = win_count / total_count if total_count > 0 else 0.50
            loss_rate = 1.0 - win_rate

            # 2. Win/Loss Ratio (b)
            avg_win = np.mean(wins) if len(wins) > 0 else 1.0
            avg_loss = abs(np.mean(losses)) if len(losses) > 0 else 1.0
            
            # Prevent division by zero
            win_loss_ratio = avg_win / avg_loss if avg_loss > 0 else 1.0

            # 3. Kelly Formula: f* = p - (q / b)
            if win_loss_ratio > 0:
                kelly_raw = win_rate - (loss_rate / win_loss_ratio)
            else:
                kelly_raw = self.default_fraction

            # Apply standard institutional safety filter: Half-Kelly
            half_kelly = kelly_raw * 0.5

            # Clip/Limit the output to prevent excessive leverage
            # Min 5% (0.05), Max user threshold (e.g. 20%)
            kelly_fraction = float(np.clip(half_kelly, 0.05, self.max_fraction))
            
            # If Kelly calculations yield negative values (due to poor performance),
            # trigger defensive state: Minimum size of 5% to survive drawdown.
            if half_kelly <= 0:
                kelly_fraction = 0.05
                reason = "Defensive mode (poor strategy performance, reducing size to 5%)"
            else:
                reason = f"Half-Kelly dynamic optimization active (Raw Kelly: {kelly_raw:.1%})"

            return {
                "kelly_fraction": round(kelly_fraction, 4),
                "win_rate": round(win_rate, 2),
                "win_loss_ratio": round(win_loss_ratio, 2),
                "total_trades": total_count,
                "is_dynamic": True,
                "reason": reason
            }

        except Exception as e:
            return {
                "kelly_fraction": self.default_fraction,
                "win_rate": 0.50,
                "win_loss_ratio": 1.0,
                "total_trades": 0,
                "is_dynamic": False,
                "error": str(e),
                "reason": "Emergency fallback due to error"
            }


if __name__ == "__main__":
    print("Kelly Sizer Demo")
    # Simulate a typical high-performance strategy history:
    # 7 wins (avg $150), 3 losses (avg -$70)
    simulated_history = "2026-05-27|150.00\n2026-05-27|120.00\n2026-05-27|-70.00\n2026-05-27|180.00\n2026-05-27|-65.00\n2026-05-27|140.00\n2026-05-27|160.00\n2026-05-27|-80.00\n2026-05-27|110.00\n2026-05-27|130.00"
    
    # Save a temp file for demo validation
    with open("temp_trade_journal.txt", "w") as tf:
        tf.write(simulated_history)
        
    sizer = KellySizer(journal_path="temp_trade_journal.txt")
    res = sizer.calculate_kelly_fraction()
    
    print(f"  Win Rate             : {res['win_rate']:.0%}")
    print(f"  Win/Loss Profit Ratio: {res['win_loss_ratio']}")
    print(f"  Calculated Size %    : {res['kelly_fraction']:.1%}")
    print(f"  Sizer Reason         : {res['reason']}")
    
    # Cleanup temp demo file
    if os.path.exists("temp_trade_journal.txt"):
        os.remove("temp_trade_journal.txt")
