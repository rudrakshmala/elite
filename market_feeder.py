import yfinance as yf
import pandas as pd
import ta # <--- The new stable library
import time

def get_data(symbol, period="1y", interval="1d"):
    print(f"Fetching data for {symbol}...")
    
    # 1. Fetch Data with retry logic for rate limiting
    max_retries = 3
    retry_delay = 30  # seconds
    
    for attempt in range(max_retries):
        try:
            df = yf.download(
                symbol, 
                period=period, 
                interval=interval, 
                progress=False, 
                multi_level_index=False,
                rate_limit_retry=True
            )
            break  # Success, exit retry loop
        except yf.utils.yfRateLimitError:
            if attempt < max_retries - 1:
                print(f"⚠️ Rate limit hit. Waiting {retry_delay}s before retry {attempt + 1}/{max_retries}...")
                time.sleep(retry_delay)
            else:
                print(f"❌ Failed after {max_retries} retries. Rate limited.")
                return None
        except Exception as e:
            # For non-rate-limit errors, try without multi_level_index
            if attempt == 0:
                try:
                    df = yf.download(
                        symbol, 
                        period=period, 
                        interval=interval, 
                        progress=False,
                        rate_limit_retry=True
                    )
                    break
                except yf.utils.yfRateLimitError:
                    if attempt < max_retries - 1:
                        print(f"⚠️ Rate limit hit. Waiting {retry_delay}s before retry {attempt + 1}/{max_retries}...")
                        time.sleep(retry_delay)
                    else:
                        print(f"❌ Failed after {max_retries} retries. Rate limited.")
                        return None
                except Exception:
                    print(f"Error: {e}")
                    return None
            else:
                print(f"Error: {e}")
                return None
    
    if df.empty:
        print("Error: No data found.")
        return None

    # 2. Add Elite Indicators using 'ta' library
    
    # RSI (Relative Strength Index) - Momentum
    # We use the built-in class to calculate it and add it as a column
    rsi_indicator = ta.momentum.RSIIndicator(close=df["Close"], window=14)
    df["RSI"] = rsi_indicator.rsi()
    
    # ATR (Average True Range) - Volatility (Risk Management)
    atr_indicator = ta.volatility.AverageTrueRange(high=df["High"], low=df["Low"], close=df["Close"], window=14)
    df["ATR"] = atr_indicator.average_true_range()
    
    # SMA (Simple Moving Average) - Trend
    sma_indicator = ta.trend.SMAIndicator(close=df["Close"], window=200)
    df["SMA_200"] = sma_indicator.sma_indicator()

    # 3. Clean up (Remove empty rows from the start where indicators are calculating)
    df.dropna(inplace=True)
    
    return df

# --- TEST AREA ---
if __name__ == "__main__":
    symbol = "BTC-USD"
    data = get_data(symbol)
    
    if data is not None:
        print("\nSUCCESS! Data downloaded and indicators calculated.")
        
        last_row = data.iloc[-1]
        print(f"Latest Price: ${last_row['Close']:.2f}")
        print(f"Current RSI: {last_row['RSI']:.2f}")
        print(f"Current Volatility (ATR): {last_row['ATR']:.2f}")
        
        print("\nLast 5 rows of your data:")
        print(data.tail())
    else:
        print("Failed to get data.")
