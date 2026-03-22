# Tradee: A Quantitative Decision-Support System

Tradee is a professional trading decision-support system designed to provide actionable, data-driven insights for quantitative traders. It extends a basic market intelligence terminal with a suite of powerful analytical engines to enhance decision-making and risk management.

This system is built with a modular Python architecture and leverages publicly available financial data via the `yfinance` library.

---

## Key Features & Modules

The system is composed of the following integrated modules:

### 1. Market Regime Detection
This module classifies the current market environment to provide high-level context for strategic decisions.
- **Regimes:** Trend Up, Trend Down, Range-Bound, Volatile, Breakout
- **Indicators:** Utilizes a combination of price behavior, volatility metrics (e.g., ATR), and momentum indicators (e.g., RSI, MACD).

### 2. Options Intelligence Engine
Computes actionable signals from option chain data to identify key price levels and market sentiment.
- **Signals:**
    - Put/Call Walls
    - Support and Resistance from Open Interest (OI)
    - OI Concentration Zones
    - Max Pain Drift
    - Dominant Writer Analysis

### 3. Risk Management Engine
Monitors real-time risk exposure to enforce trading discipline and protect capital.
- **Tracked Metrics:**
    - Daily Loss Limit
    - Risk Per Trade
    - Total Exposure
    - Account Drawdown
- **Functionality:** Provides real-time warnings when predefined risk limits are approached or breached.

### 4. Trade Planner
A calculation tool to formalize trade ideas and assess their viability before execution.
- **Calculations:**
    - Entry Price
    - Stop Loss
    - Target Price
    - Risk-Reward Ratio
    - Position Size

### 5. Active Trade Monitor
Tracks open positions in real-time to provide a clear overview of ongoing trades.

### 6. Alert System
Generates timely alerts for critical market events, allowing traders to react quickly.
- **Alert Triggers:**
    - Price level breaks (support/resistance)
    - Volatility spikes
    - Custom indicator-based events

---

## Technology Stack

- **Programming Language:** Python 3.x
- **Data Source:** `yfinance` for stock and options data.
- **Core Libraries:**
    - `pandas` for data manipulation and analysis.
    - `numpy` for numerical operations.
    - `matplotlib` / `plotly` for charting (optional).
    - `flask` / `streamlit` for the user interface (optional).

---

## Project Architecture

The system is designed with a modular architecture to ensure separation of concerns and ease of development. Each engine (Market Regime, Options, Risk) operates as a distinct module that can be developed, tested, and maintained independently.

```
tradee/
│
├── data_fetcher/
│   └── yfinance_client.py    # Handles all communication with the yfinance API
│
├── modules/
│   ├── market_regime.py      # Regime detection logic
│   ├── options_engine.py     # Options chain analysis
│   ├── risk_manager.py       # Risk calculation and monitoring
│   ├── trade_planner.py      # Trade planning calculations
│   └── ...
│
├── main.py                     # Main application entry point
├── config.py                   # Configuration (tickers, risk limits, etc.)
└── requirements.txt            # Project dependencies
```

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Pip (Python package installer)

### Installation

1.  **Clone the repository (or create the project directory):**
    ```bash
    git clone https://your-repo-url/tradee.git
    cd tradee
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

---

## Usage

To run the application, execute the main script:

```bash
python main.py
```
