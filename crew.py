import time
import logging
from crewai import Task, Crew, Process
from agents import (
    bull_analyst,
    bear_analyst,
    news_analyst,
    quant_analyst,
    cio_agent
)

# --- 🛡️ RATE LIMIT RETRY WRAPPER ---
def retry_on_rate_limit(func, max_retries=3, wait_seconds=15):
    """
    Wrapper function to retry crew.kickoff() on rate limit errors.
    Waits `wait_seconds` between retries, up to `max_retries` attempts.
    """
    for attempt in range(1, max_retries + 1):
        try:
            return func()
        except Exception as e:
            error_msg = str(e).lower()
            # Check if it's a rate limit error
            if any(keyword in error_msg for keyword in ['rate limit', 'too many requests', '429', 'quota']):
                if attempt < max_retries:
                    print(f"\n⚠️ Rate limit hit. Retrying in {wait_seconds}s (Attempt {attempt}/{max_retries})...")
                    time.sleep(wait_seconds)
                    continue
                else:
                    print(f"\n❌ Rate limit error after {max_retries} retries: {e}")
                    raise
            else:
                # Non-rate-limit error, re-raise immediately
                raise

# --- 🚀 EXECUTION ENGINE ---
def evaluate_opportunity(sym_a, sym_b, z_score):
    """
    Assembles the Crew and evaluates a trading opportunity.
    Uses dual LLM strategy:
    - fast_llm for data gathering agents (quant, analyst, bear)
    - quality_llm for final decision (CIO)
    """
    print(f"\n📢 Assembling the Crew to evaluate {sym_a}/{sym_b} (Z: {z_score})")

    # --- 📊 QUANT TASK (Data Gathering) ---
    task_quant = Task(
        description=f'''Use your tool to check the live price and volume for {sym_a} and {sym_b}. 
        The current Z-score is {z_score}. Write a brief summary on whether the live data supports a mean-reversion opportunity.''',
        expected_output='A brief summary of live price and volume data, and whether it supports a trade.',
        agent=quant_analyst
    )

    # --- 📰 NEWS TASK (Data Gathering) ---
    task_news = Task(
        description=f'''Use your market_news_tool to search for recent financial news for the tickers {sym_a} and {sym_b}. 
        CRITICAL: You must use the tool twice—once for {sym_a} and once for {sym_b}. 
        Are there impending earnings reports, lawsuits, or major announcements that make this trade dangerous?''',
        expected_output='A summary of any recent news or catalysts for both stocks, and an assessment of the fundamental risk.',
        agent=news_analyst
    )

    # --- 🐻 BEAR TASK (Risk Analysis) ---
    task_bear = Task(
        description=f'''Use your tools to find reasons NOT to trade {sym_a}/{sym_b}. 
        Check live price/volume for both tickers and news for both. Look for: thin volume, negative catalysts, 
        stretched valuations, correlation breakdown risks, or any factor that argues AGAINST this mean-reversion setup.
        Be thorough and skeptical—your job is to find what could go wrong.''',
        expected_output='A concise list of bearish concerns and reasons to skip this trade.',
        agent=bear_analyst
    )

    # --- 🏆 CIO DECISION TASK (Final Decision - Uses Quality LLM) ---
    task_cio = Task(
        description=f'''You are the final decision maker. Review the Quant's math, the Analyst's news summary, 
        and CRITICALLY the Bear Analyst's concerns for {sym_a} vs {sym_b}. 
        You MUST weigh the Bear Analyst's objections before deciding.
        
        Direction: Z-score is {z_score}. Negative Z means the spread is cheap → mean reversion = BUY. 
        Positive Z means the spread is expensive → mean reversion = SELL. Only output BUY or SELL if confident.
        
        Your output MUST be a valid JSON object only—no extra text, no markdown. Use this exact schema:
        {{
            "signal_strength": 0.0 to 1.0,
            "confidence": 0 to 100,
            "bull_case_summary": "1-2 sentences summarizing why this trade could work",
            "bear_case_summary": "1-2 sentences summarizing the main risks and Bear Analyst concerns",
            "final_action": "BUY" or "SELL" or "WAIT"
        }}''',
        expected_output='A strict JSON object with signal_strength, confidence, bull_case_summary, bear_case_summary, and final_action.',
        agent=cio_agent,
        context=[task_quant, task_news, task_bear]
    )

    # --- 🤖 CREATE CREW (max_rpm=5) ---
    trading_crew = Crew(
        agents=[quant_analyst, news_analyst, bear_analyst, cio_agent],
        tasks=[task_quant, task_news, task_bear, task_cio],
        process=Process.sequential,
        verbose=True,
        max_rpm=5  # Rate limit protection
    )

    # --- ⚡ EXECUTE WITH RETRY WRAPPER ---
    def kickoff_with_retry():
        return trading_crew.kickoff()
    
    result = retry_on_rate_limit(kickoff_with_retry, max_retries=3, wait_seconds=15)
    return result
