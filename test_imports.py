"""Quick test to verify all new modules import correctly."""
import sys
import os
import io

# Force UTF-8 output on Windows so emoji prints don't crash
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
os.environ['PYTHONIOENCODING'] = 'utf-8'

errors = []
passed = 0

# Test 1
try:
    from market_adapter import BaseMarketAdapter
    passed += 1
    print(f"[PASS] 1/8 market_adapter.py")
except Exception as e:
    errors.append(f"[FAIL] 1/8 market_adapter.py: {e}")
    print(errors[-1])

# Test 2
try:
    from indian_market_adapter import IndianMarketAdapter
    adapter = IndianMarketAdapter()
    pairs = adapter.get_pairs_universe()
    passed += 1
    print(f"[PASS] 2/8 indian_market_adapter.py ({len(pairs)} pairs)")
except Exception as e:
    errors.append(f"[FAIL] 2/8 indian_market_adapter.py: {e}")
    print(errors[-1])

# Test 3
try:
    from forex_market_adapter import ForexMarketAdapter
    adapter = ForexMarketAdapter()
    pairs = adapter.get_pairs_universe()
    passed += 1
    print(f"[PASS] 3/8 forex_market_adapter.py ({len(pairs)} pairs)")
except Exception as e:
    errors.append(f"[FAIL] 3/8 forex_market_adapter.py: {e}")
    print(errors[-1])

# Test 4
try:
    from market_router import get_active_market_name
    market = get_active_market_name()
    passed += 1
    print(f"[PASS] 4/8 market_router.py (Current market: {market})")
except Exception as e:
    errors.append(f"[FAIL] 4/8 market_router.py: {e}")
    print(errors[-1])

# Test 5
try:
    from agent_context import inject_market_context, build_enriched_crew_tasks
    passed += 1
    print("[PASS] 5/8 agent_context.py")
except Exception as e:
    errors.append(f"[FAIL] 5/8 agent_context.py: {e}")
    print(errors[-1])

# Test 6
try:
    from dual_market_bot import DualMarketBot
    passed += 1
    print("[PASS] 6/8 dual_market_bot.py")
except Exception as e:
    errors.append(f"[FAIL] 6/8 dual_market_bot.py: {e}")
    print(errors[-1])

# Test 7
try:
    import config
    token = config.UPSTOX_ACCESS_TOKEN
    trail = config.TRAILING_STOP_PCT
    risk = config.POSITION_RISK_PCT
    passed += 1
    print(f"[PASS] 7/8 config.py (TRAIL={trail}%, RISK={risk}%)")
except Exception as e:
    errors.append(f"[FAIL] 7/8 config.py: {e}")
    print(errors[-1])

# Test 8: Verify legacy modules still import
try:
    from elite_trader_ai import EliteBot
    from crew_trader import evaluate_opportunity
    from rl_brain import QLearningAgent
    passed += 1
    print("[PASS] 8/8 LEGACY (elite_trader_ai, crew_trader, rl_brain)")
except Exception as e:
    errors.append(f"[FAIL] 8/8 LEGACY: {e}")
    print(errors[-1])

print(f"\n{'='*50}")
print(f"RESULT: {passed}/8 passed, {len(errors)} failed")
if errors:
    for e in errors:
        print(f"  {e}")
    sys.exit(1)
else:
    print("ALL TESTS PASSED")
    sys.exit(0)
