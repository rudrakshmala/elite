import streamlit as st
import plotly.graph_objects as go
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time
import os

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(layout="wide", page_title="Elite AI Terminal", page_icon="⚡")

# ==========================================
# 2. INJECT TRADINGVIEW "DEEP DARK" CSS
# ==========================================
st.markdown("""
    <style>
    /* Main background */
    .stApp { background-color: #131722; color: #d1d4dc; }
    /* Panel backgrounds */
    div[data-testid="stVerticalBlock"] > div { background-color: #1E222D; padding: 1rem; border-radius: 8px; }
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. LIVE DATA FETCHING
# ==========================================
@st.cache_data(ttl=5) # Cache clears every 5 seconds for live market updates
def load_data(ticker):
    try:
        # Fetching the last 1 day of data, at 1-minute intervals
        df = yf.download(ticker, period="1d", interval="1m")
        return df
    except Exception as e:
        return pd.DataFrame()

ticker = "LMT"
df = load_data(ticker)

# ==========================================
# 4. THE UI GRID SYSTEM
# ==========================================
st.title("⚡ Elite-Bot Terminal")

# Main Split: Chart vs Metrics
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader(f"{ticker} Live Chart (1m timeframe)")
    
    if not df.empty:
        # Build the TradingView-style Candlestick Chart
        fig = go.Figure(data=[go.Candlestick(
            x=df.index,
            open=df['Open'].squeeze(), high=df['High'].squeeze(),
            low=df['Low'].squeeze(), close=df['Close'].squeeze(),
            increasing_line_color='#26A69A', # TV Bullish Mint
            decreasing_line_color='#EF5350'  # TV Bearish Red
        )])
        
        # Style the chart to match the UI
        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='#131722',
            plot_bgcolor='#131722',
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis_rangeslider_visible=False, 
            xaxis=dict(showgrid=True, gridcolor='#2B2B43'),
            yaxis=dict(showgrid=True, gridcolor='#2B2B43', side='right') 
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Waiting for market data...")

with col2:
    st.subheader("Live Metrics")
    
    # Toggle to pause the auto-refresh so you can zoom in on charts without them resetting
    auto_refresh = st.toggle("🟢 Live Data Sync", value=True)
    
    # Calculate live price action dynamically
    if not df.empty and len(df) > 1:
        current_price = float(df['Close'].iloc[-1].squeeze())
        prev_price = float(df['Close'].iloc[-2].squeeze())
        price_diff = current_price - prev_price
        st.metric(label=f"{ticker} Last Price", value=f"${current_price:.2f}", delta=f"${price_diff:.2f}")
    else:
        st.metric(label=f"{ticker} Last Price", value="Loading...")

    st.metric(label="LMT/RTX Z-Score", value="-1.59", delta="-0.12", delta_color="inverse")
    st.metric(label="Bot Status", value="Scanning 🔭")
    
    st.markdown("---")
    st.subheader("Watchlist")
    st.markdown("""
    * 🟢 **TSLA** (Trend)
    * 🔴 **LMT/RTX** (Mean Rev)
    * ⚪ **AAPL** (Scanning...)
    """)

# ==========================================
# 5. BOTTOM TERMINAL (Real Live Logs)
# ==========================================
st.markdown("---")
st.subheader("🤖 AI Agent Terminal Logs")

def get_live_logs():
    log_file = 'bot_memory.log'
    if os.path.exists(log_file):
        with open(log_file, 'r') as file:
            # Grab the last 15 actions the bot took
            lines = file.readlines()[-15:]
            return "".join(lines) if lines else "Log file is empty. Waiting for AI..."
    else:
        return f"Waiting for bot to boot up and create '{log_file}' file...\nMake sure your main bot script has logging enabled!"

st.code(get_live_logs(), language="bash")

# ==========================================
# 6. THE HEARTBEAT (Auto-Refresh)
# ==========================================
if auto_refresh:
    time.sleep(5)  # Wait 5 seconds
    st.rerun()     # Force Streamlit to rebuild the page and fetch fresh data