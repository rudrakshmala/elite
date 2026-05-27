"""
startup_manager.py — Interactive Startup Manager
===================================================
CLI entry point that lets the user choose the trading environment.
This is a NEW entry point — it does NOT replace app.py or any existing file.

Usage:
    python startup_manager.py

Options:
    1. 🇮🇳 Indian Market (Day Mode)   — NSE stocks via Upstox Sandbox
    2. 🌍 Forex Market (Night Mode)   — Currency pairs via Alpaca Paper
    3. 🔄 Auto-Shift (Clock Mode)     — Time-aware IST-based switching
    4. 🇺🇸 Original US Mode (Legacy)  — Your existing EliteBot, unchanged
"""

import time
import sys


def print_banner():
    """Print the startup menu."""
    print("\n")
    print("╔══════════════════════════════════════════════╗")
    print("║      🦅 ELITE-BOT STARTUP MANAGER           ║")
    print("║      Time-Aware Dual-Market Architecture     ║")
    print("╠══════════════════════════════════════════════╣")
    print("║                                              ║")
    print("║   1. 🇮🇳 Indian Market  (Day Mode)           ║")
    print("║      NSE Stocks • Upstox Sandbox • ₹ INR     ║")
    print("║                                              ║")
    print("║   2. 🌍 Forex Market   (Night Mode)          ║")
    print("║      Currency Pairs • Alpaca Paper • $ USD   ║")
    print("║                                              ║")
    print("║   3. 🔄 Auto-Shift     (Clock Mode)          ║")
    print("║      IST Time-Based • Auto Switch Markets    ║")
    print("║                                              ║")
    print("║   4. 🇺🇸 Original US   (Legacy Mode)         ║")
    print("║      US Stocks • Alpaca Paper • Unchanged    ║")
    print("║                                              ║")
    print("║   5. ❌ Exit                                  ║")
    print("║                                              ║")
    print("╚══════════════════════════════════════════════╝")


def run_indian_mode():
    """Launch the Indian Market bot."""
    print("\n🇮🇳 Starting Indian Market Mode...")
    print("   📊 Market: NSE (National Stock Exchange)")
    print("   ⏰ Hours: 09:15 AM – 03:30 PM IST")
    print("   💱 Currency: ₹ INR")
    print("   🔑 Broker: Upstox Sandbox (Paper Trading)")
    print("")

    from dual_market_bot import DualMarketBot
    bot = DualMarketBot(market="indian")
    bot.run()


def run_forex_mode():
    """Launch the Forex Market bot."""
    print("\n🌍 Starting Forex Market Mode...")
    print("   📊 Market: Global Forex (Major Pairs)")
    print("   ⏰ Hours: 06:00 PM – 02:00 AM IST")
    print("   💱 Currency: $ USD / Pips")
    print("   🔑 Broker: Alpaca Paper (Existing Keys)")
    print("")

    from dual_market_bot import DualMarketBot
    bot = DualMarketBot(market="forex")
    bot.run()


def run_auto_shift():
    """Launch the Auto-Shift mode — follows IST clock automatically."""
    from market_router import get_active_adapter, get_active_market_name, print_session_status

    print("\n🔄 Starting Auto-Shift Mode...")
    print("   ℹ️  The bot will automatically switch between markets:")
    print("   🇮🇳 09:15 AM – 03:30 PM IST  →  Indian NSE")
    print("   🌍 06:00 PM – 02:00 AM IST  →  Global Forex")
    print("   💤 Other times              →  Cooldown / Sleep")
    print("")

    while True:
        print_session_status()

        adapter = get_active_adapter()

        if adapter is None:
            # Cooldown — no market open
            market = get_active_market_name()
            print("   💤 No market active. Sleeping for 5 minutes...")
            time.sleep(300)  # Check every 5 minutes
            continue

        # Market is active — launch the bot with the correct adapter
        print(f"\n   🚀 Launching {adapter.market_name} bot...")

        from dual_market_bot import DualMarketBot
        try:
            bot = DualMarketBot(adapter=adapter, market=get_active_market_name())
            bot.run()
        except KeyboardInterrupt:
            print("\n   ⏹️ Bot interrupted by user.")
            break
        except Exception as e:
            print(f"   ❌ Bot error: {e}")
            print("   ⏳ Restarting in 60 seconds...")
            time.sleep(60)


def run_legacy_mode():
    """Launch the original US market bot — completely unchanged."""
    print("\n🇺🇸 Starting Legacy US Mode...")
    print("   ℹ️  Running the original EliteBot (elite_trader_ai.py)")
    print("   ⚠️  This is your existing bot — zero modifications.")
    print("")

    from elite_trader_ai import EliteBot
    bot = EliteBot()
    bot.run()


def main():
    """Main entry point."""
    while True:
        print_banner()
        choice = input("\n  ➤ Select mode (1-5): ").strip()

        if choice == "1":
            run_indian_mode()
        elif choice == "2":
            run_forex_mode()
        elif choice == "3":
            run_auto_shift()
        elif choice == "4":
            run_legacy_mode()
        elif choice == "5":
            print("\n👋 Goodbye! Happy Trading!")
            sys.exit(0)
        else:
            print("\n   ❌ Invalid choice. Please enter 1, 2, 3, 4, or 5.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Elite-Bot shutting down gracefully.")
