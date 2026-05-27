"""
agent_context.py — Dynamic CrewAI Context Injection
=====================================================
Injects market-specific context into CrewAI task descriptions
WITHOUT modifying any agent definitions in crew_trader.py.

This is called at TASK CREATION time — the agents (Bull, Bear, 
Quant, CIO) remain exactly as defined in crew_trader.py.
"""

from market_adapter import BaseMarketAdapter


def inject_market_context(base_description: str, adapter: BaseMarketAdapter) -> str:
    """
    Appends market-specific context to any CrewAI task description.
    
    Example:
        Original: "Check live price/volume for RELIANCE.NS and TCS.NS"
        After:    "Check live price/volume for RELIANCE.NS and TCS.NS
                   
                   MARKET CONTEXT: You are analyzing the INDIAN STOCK MARKET (NSE).
                   Focus on: SEBI regulations, RBI monetary policy..."
    
    This does NOT touch crew_trader.py agents — it only enriches task descriptions.
    """
    context = adapter.get_crew_context()
    return f"{base_description}\n\nMARKET CONTEXT: {context}"


def get_market_specific_cio_prompt(adapter: BaseMarketAdapter, 
                                     context_str: str, 
                                     type_str: str, 
                                     technicals: dict) -> str:
    """
    Build the CIO (Chief Investment Officer) task description 
    with market-specific context injected.
    
    Uses the SAME JSON output format as crew_trader.py's CIO task.
    """
    import json
    
    is_pair = "pair" in type_str.lower()
    
    base_prompt = f"""Review the Quant's math, the Analyst's news, and the Bear's risks for {context_str}.
    Strategy: {type_str}.
    Technicals: {json.dumps(technicals)}
    
    Decide: BUY, SELL, or WAIT.
    {"BUY/SELL = Open the spread trade" if is_pair else "BUY/SELL = Long/Short the individual stock"}.
    
    Output JSON only:
    {{
        "signal_strength": 0.0 to 1.0,
        "confidence": 0 to 100,
        "strategy_type": "{"pair" if is_pair else "single"}",
        "bull_case": "...",
        "bear_case": "...",
        "final_action": "BUY/SELL/WAIT"
    }}"""
    
    return inject_market_context(base_prompt, adapter)


def build_enriched_crew_tasks(adapter: BaseMarketAdapter, 
                                ticker_a: str, 
                                ticker_b: str = None, 
                                technicals: dict = None):
    """
    Build CrewAI tasks with market-specific context injected.
    Returns task descriptions (strings) — NOT Task objects.
    
    This keeps crew_trader.py completely untouched while
    adding Indian/Forex awareness to the AI reasoning.
    """
    is_pair = ticker_b is not None
    context_str = f"{ticker_a}/{ticker_b}" if is_pair else ticker_a
    type_str = "MEAN-REVERSION PAIR" if is_pair else "SINGLE-TICKER MOMENTUM"
    
    # Quant task description
    if is_pair:
        quant_desc = f"Check live price/volume for {ticker_a} and {ticker_b}. Current Z-score: {technicals.get('z_score')}. Does the spread support mean-reversion?"
    else:
        quant_desc = f"Check live price/volume for {ticker_a}. Current RSI: {technicals.get('rsi')}. Is the stock overextended or breaking out?"
    
    # News task description
    if is_pair:
        news_desc = f"Check financial news for {ticker_a} and {ticker_b}. Look for catalysts that could break their correlation."
    else:
        news_desc = f"Check financial news for {ticker_a}. Is there any reason (earnings, rumors, etc) behind this price movement?"
    
    # Bear task description
    if is_pair:
        bear_desc = f"Find reasons NOT to trade the {ticker_a}/{ticker_b} pair. Look for divergence risk or negative catalysts."
    else:
        bear_desc = f"Find reasons NOT to trade {ticker_a}. Is it a pump-and-dump? Is the signal fake?"
    
    # Inject market context into all descriptions
    enriched_quant = inject_market_context(quant_desc, adapter)
    enriched_news = inject_market_context(news_desc, adapter)
    enriched_bear = inject_market_context(bear_desc, adapter)
    enriched_cio = get_market_specific_cio_prompt(adapter, context_str, type_str, technicals or {})
    
    return {
        "quant": enriched_quant,
        "news": enriched_news,
        "bear": enriched_bear,
        "cio": enriched_cio,
    }
