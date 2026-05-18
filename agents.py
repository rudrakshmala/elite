import os
from dotenv import load_dotenv
import yfinance as yf
from crewai import Agent, LLM
from crewai.tools import tool

load_dotenv()  # Load keys from .env

# --- 🚀 LLM CONFIGURATION ---
# Fast LLM for data gathering (low cost, fast responses)
fast_llm = LLM(
    model="groq/llama-3.1-8b-instant",
    temperature=0.1,
    max_retries=3
)

# Quality LLM for final decisions (higher accuracy)
quality_llm = LLM(
    model="groq/llama-3.3-70b-versatile",
    temperature=0.1,
    max_retries=3
)

# --- 🛠️ TOOLS ---
@tool("live_stock_data_tool")
def live_stock_data_tool(ticker: str) -> str:
    """Fetches live price and volume for a given stock ticker."""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d")
        
        if hist.empty:
            return f"Data currently unavailable for {ticker}."
            
        price = hist['Close'].iloc[-1]
        volume = int(hist['Volume'].iloc[-1])
        
        return f"Ticker: {ticker} | Last Price: ${price:.2f} | Volume: {volume}"
    except Exception as e:
        return f"Error fetching data for {ticker}: {e}"

@tool("market_news_tool")
def market_news_tool(ticker: str) -> str:
    """
    Fetches the most recent financial news for a specific stock ticker.
    Use this to check for earnings reports, lawsuits, or major announcements.
    Input MUST be a single valid stock ticker symbol (e.g., 'V', 'MA').
    """
    try:
        stock = yf.Ticker(ticker)
        news_items = stock.news
        
        if not news_items:
            return f"No recent financial news found for {ticker}."

        news_summary = f"--- Recent News for {ticker} ---\n"
        for item in news_items[:5]: 
            title = item.get('title', 'No Title')
            publisher = item.get('publisher', 'Unknown Publisher')
            link = item.get('link', 'No Link')
            
            news_summary += f"\n📰 **{title}** ({publisher})\n   Link: {link}\n"
            
        return news_summary

    except Exception as e:
        return f"Error fetching news for {ticker}: {str(e)}."

# --- 🤖 DATA GATHERING AGENTS (using fast_llm) ---
bull_analyst = Agent(
    role='Bull Analyst',
    goal='Argue FOR the execution of the {ticker_1}/{ticker_2} pair trade.',
    backstory="""You are an expert at identifying mean-reversion opportunities. 
    Your job is to prove that the current Z-score of {z_score} is a massive 
    opportunity and that the spread will inevitably close.""",
    verbose=True,
    allow_delegation=False,
    llm=fast_llm
)

bear_analyst = Agent(
    role='Bear Analyst',
    goal='Find concrete reasons NOT to trade the pair: overvaluation, weak volume, negative catalysts, correlation breakdown risks, or unfavorable risk/reward.',
    backstory="""You are a skeptical contrarian who always looks for the downside. 
    Your job is to challenge every trade and surface risks others might miss.""",
    verbose=True,
    allow_delegation=False,
    tools=[live_stock_data_tool, market_news_tool],
    llm=fast_llm
)

news_analyst = Agent(
    role='News Analyst',
    goal='Check for breaking news, earnings reports, or impending catalysts that could break a correlation.',
    backstory="""You are an expert at identifying risk and fundamental shifts in the market.""",
    verbose=True,
    allow_delegation=False,
    tools=[market_news_tool],
    llm=fast_llm
)

quant_analyst = Agent(
    role='Senior Quantitative Analyst',
    goal='Analyze live price and volume data to confirm mean-reversion setups.',
    backstory="""You are a master of statistical arbitrage and quantitative finance.""",
    verbose=True,
    allow_delegation=False,
    tools=[live_stock_data_tool],
    llm=fast_llm
)

# --- 🏆 FINAL DECISION AGENT (using quality_llm) ---
cio_agent = Agent(
    role='Chief Investment Officer',
    goal='Make the final TRADE or SKIP decision by weighing quant data, news summaries, and the Bear Analyst\'s objections. Output strict JSON only.',
    backstory="""You are a ruthless hedge fund manager who only takes high-probability mean-reversion trades. 
    You must always consider the Bear Analyst\'s concerns before approving any trade.""",
    verbose=True,
    allow_delegation=False,
    llm=quality_llm
)
