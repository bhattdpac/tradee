# This file will contain the configuration for the Tradee application.
# For example, tickers, risk limits, etc.

TICKERS = [
    "RELIANCE.NS",
    "TCS.NS",
    "HDFCBANK.NS",
    "INFY.NS"
]

RISK_LIMITS = {
    "daily_loss_limit": 0.02,  # 2% of portfolio
    "risk_per_trade": 0.005, # 0.5% of portfolio
    "max_exposure": 0.10,    # Max 10% of portfolio value can be in open trades
}
