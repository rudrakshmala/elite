import time
import math
import os
import datetime
import json
import re
import yfinance as yf
import pandas as pd
import ta
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
import config

# --- 🧠 SMART CREW AI ---
from crew_trader import evaluate_smart_opportunity

# --- ⚙️ CONFIG ---
SMART_UNIVERSE = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA", "JPM", "V", "WMT", 
    "MA", "PG", "UNH", "HD", "BAC", "XOM", "DIS", "ADBE", "NFLX", "COST", 
    "CRM", "AVGO", "CSCO", "ORCL", "ACN", "LMT", "RTX", "KO", "PEP", "F", "GM"
]

PAIRS_UNIVERSE = [
    ("KO", "PEP"), ("XOM", "CVX"), ("JPM", "BAC"), 
    ("F", "GM"), ("MSFT", "AAPL"), ("V", "MA"), 
    ("LMT", "RTX"), ("GOOGL", "META")
]

class SmartBot:
    def __init__(self):
        self.client = TradingClient(config.API_KEY, config.SECRET_KEY, paper=True)
        self.blacklist_file = "blacklist.json"
        print("--- 🧠 ELITE SMART AGENT INITIALIZED ---")

    def get_blacklist(self):
        if not os.path.exists(self.blacklist_file):
            return []
        try:
            with open(self.blacklist_file, "r") as f:
                return json.load(f).get("frozen_tickers", [])
        except:
            return []

    def get_price(self, sym):
        try:
            df = yf.download(sym, period="1d", interval="1m", progress=False)
            return float(df['Close'].iloc[-1].squeeze()) if not df.empty else 0.0
        except: return 0.0

    def scan_for_opportunities(self):
        frozen = self.get_blacklist()
        opportunities = []

        # 1. SCAN SINGLE TICKERS (Momentum/Trend)
        print(f"   🔎 Scanning {len(SMART_UNIVERSE)} tickers for Momentum...")
        for sym in SMART_UNIVERSE:
            if sym in frozen: continue
            try:
                df = yf.download(sym, period="5d", interval="1h", progress=False)
                if len(df) < 30: continue
                
                # Tech Indicators
                rsi = ta.momentum.RSIIndicator(close=df["Close"], window=14).rsi().iloc[-1]
                sma200 = ta.trend.SMAIndicator(close=df["Close"], window=200 if len(df) >= 200 else 20).sma_indicator().iloc[-1]
                last_price = df["Close"].iloc[-1]

                if rsi < 30: # Oversold
                    opportunities.append({
                        "type": "single", "ticker_a": sym, "side": "BUY",
                        "technicals": {"rsi": round(rsi, 2), "price": round(last_price, 2), "setup": "oversold"}
                    })
                elif rsi > 70: # Overbought
                    opportunities.append({
                        "type": "single", "ticker_a": sym, "side": "SELL",
                        "technicals": {"rsi": round(rsi, 2), "price": round(last_price, 2), "setup": "overbought"}
                    })
            except: continue

        # 2. SCAN PAIRS (Mean Reversion)
        print(f"   🔎 Scanning {len(PAIRS_UNIVERSE)} pairs for Mean-Reversion...")
        for sym_a, sym_b in PAIRS_UNIVERSE:
            if sym_a in frozen or sym_b in frozen: continue
            try:
                data_a = yf.download(sym_a, period="5d", interval="1h", progress=False)['Close']
                data_b = yf.download(sym_b, period="5d", interval="1h", progress=False)['Close']
                df = pd.DataFrame({"a": data_a, "b": data_b}).dropna()
                
                df['ratio'] = df['a'] / df['b']
                z = (df['ratio'] - df['ratio'].rolling(20).mean()) / df['ratio'].rolling(20).std()
                last_z = z.iloc[-1]

                if abs(last_z) > 1.8:
                    side = "BUY_PAIR" if last_z < 0 else "SELL_PAIR"
                    opportunities.append({
                        "type": "pair", "ticker_a": sym_a, "ticker_b": sym_b,
                        "side": side, "technicals": {"z_score": round(last_z, 2), "type": "pair"}
                    })
            except: continue

        return opportunities

    def run(self):
        while True:
            print(f"\n[{time.strftime('%H:%M:%S')}] --- SMART SCAN CYCLE ---")
            opps = self.scan_for_opportunities()
            
            if not opps:
                print("   💤 No technical setups found. Resting 2 mins...")
                time.sleep(120)
                continue

            # Pick the "Scariest" or "Strongest" opportunity (e.g. highest absolute Z or extreme RSI)
            # For now, just take the first one found that looks strong
            for opp in opps:
                ticker_a = opp["ticker_a"]
                ticker_b = opp.get("ticker_b")
                
                print(f"   🎯 Potential Trigger: {ticker_a} {f'/ {ticker_b}' if ticker_b else ''}")
                
                try:
                    crew_output = evaluate_smart_opportunity(ticker_a, ticker_b, opp["technicals"])
                    # Parse simplified decision
                    decision_str = str(crew_output).upper()
                    
                    if '"FINAL_ACTION": "BUY"' in decision_str or '"FINAL_ACTION": "SELL"' in decision_str:
                        print(f"   🚀 AI APPROVED: Executing {opp['type']} trade!")
                        
                        # EXECUTION LOGIC
                        cash = float(self.client.get_account().buying_power)
                        budget = cash * 0.10 # Use 10%
                        
                        if opp["type"] == "single":
                            side = OrderSide.BUY if '"FINAL_ACTION": "BUY"' in decision_str else OrderSide.SELL
                            price = self.get_price(ticker_a)
                            qty = math.floor(budget / price) if price > 0 else 0
                            if qty > 0:
                                self.client.submit_order(MarketOrderRequest(symbol=ticker_a, qty=qty, side=side, time_in_force=TimeInForce.GTC))
                        else:
                            # Pair execution logic
                            side_a = OrderSide.BUY if opp["side"] == "BUY_PAIR" else OrderSide.SELL
                            side_b = OrderSide.SELL if opp["side"] == "BUY_PAIR" else OrderSide.BUY
                            price_a = self.get_price(ticker_a)
                            price_b = self.get_price(ticker_b)
                            qty_a = math.floor((budget/2) / price_a) if price_a > 0 else 0
                            qty_b = math.floor((budget/2) / price_b) if price_b > 0 else 0
                            if qty_a > 0 and qty_b > 0:
                                self.client.submit_order(MarketOrderRequest(symbol=ticker_a, qty=qty_a, side=side_a, time_in_force=TimeInForce.GTC))
                                self.client.submit_order(MarketOrderRequest(symbol=ticker_b, qty=qty_b, side=side_b, time_in_force=TimeInForce.GTC))

                        print("   ✅ Trade Sent. Entering cooldown...")
                        time.sleep(300) # 5 min cooldown
                        break
                    else:
                        print("   ✋ AI said WAIT. Continuing scan.")
                except Exception as e:
                    print(f"   ❌ Smart Engine Error: {e}")

            time.sleep(60)

if __name__ == "__main__":
    SmartBot().run()
