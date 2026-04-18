🦅 Elite-Bot: Multi-Asset AI Trading Architecture
Python FastAPI Streamlit CrewAI

📌 Overview
Elite-Bot is an event-driven, full-stack algorithmic trading platform designed for autonomous execution across Forex (MetaTrader 5) and Cryptocurrency (Alpaca) markets.

Moving beyond simple static scripts, this project utilizes a decoupled microservice architecture. It pairs a high-speed quantitative statistical arbitrage engine (Z-score math) with advanced Large Language Models (LLMs) via CrewAI to act as a multimodal "trading committee," validating mathematical signals against broader market context before execution.

⚙️ System Architecture
The system is split into an asynchronous backend and a real-time reactive frontend, allowing the trading engines to scan markets continuously without blocking the user interface.

[ Streamlit Dashboard ] (Frontend / UI)
       │      ▲
 (POST /start)│ (GET /telemetry) Live PnL & Status
       ▼      │
[ FastAPI Controller ] (Backend Hub on Port 8080)
       │
       ├─────────────────────────────────┐
       ▼                                 ▼
[ Crypto Engine Thread ]          [ Forex Engine Thread ]
  • Z-Score Math Scanner            • MetaTrader 5 API
  • Alpaca API Execution            • CrewAI Validation
  • CrewAI Validation               • Dynamic Trailing Stops
