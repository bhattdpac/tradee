# This module will contain the logic for the Risk Management Engine.
from config import RISK_LIMITS
import datetime

class RiskManager:
    """
    Manages and enforces trading risk rules.
    This is a stateful class designed to be instantiated once per session.
    """
    def __init__(self, portfolio_value: float):
        """
        Initializes the RiskManager.
        :param portfolio_value: The starting value of the portfolio.
        """
        self.portfolio_value = portfolio_value
        self.limits = RISK_LIMITS
        
        # State variables
        self.open_trades = []
        self.pnl_today = 0.0
        self.current_exposure = 0.0

    def check_trade_violation(self, amount_to_risk: float, trade_value: float):
        """
        Checks if a potential new trade violates any predefined risk rules.
        
        :param amount_to_risk: The potential loss for the new trade.
        :param trade_value: The total value of the new position (e.g., position_size * entry_price).
        :return: A list of violation messages. An empty list means the trade is compliant.
        """
        violations = []

        # Rule 1: Check risk per trade
        max_risk_per_trade = self.portfolio_value * self.limits.get("risk_per_trade", 0.01)
        if amount_to_risk > max_risk_per_trade:
            violations.append(
                f"Trade risk (${amount_to_risk:.2f}) exceeds the max risk per trade limit (${max_risk_per_trade:.2f})."
            )

        # Rule 2: Check daily loss limit
        max_daily_loss = self.portfolio_value * self.limits.get("daily_loss_limit", 0.02)
        if abs(self.pnl_today) + amount_to_risk > max_daily_loss:
            violations.append(
                f"Potential loss from this trade would exceed the max daily loss limit (${max_daily_loss:.2f})."
            )
            
        # Rule 3: Check max exposure
        max_exposure = self.portfolio_value * self.limits.get("max_exposure", 0.10)
        if self.current_exposure + trade_value > max_exposure:
            violations.append(
                f"This trade would increase exposure to ${self.current_exposure + trade_value:.2f}, exceeding the max exposure limit of ${max_exposure:.2f}."
            )

        return violations

    def add_trade(self, ticker: str, trade_plan: dict):
        """
        Adds a new open trade to the manager's state.
        :param ticker: The ticker symbol for the trade.
        :param trade_plan: The dictionary of trade details from calculate_trade_plan.
        """
        trade_id = f"{ticker}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        trade_value = trade_plan['position_size'] * trade_plan['entry_price']

        trade = {
            "ID": trade_id,
            "Ticker": ticker,
            "Type": trade_plan['trade_type'],
            "Entry": trade_plan['entry_price'],
            "Stop": trade_plan['stop_loss'],
            "Target": trade_plan['target'],
            "Size": trade_plan['position_size'],
            "Value": trade_value,
            "Risk": trade_plan['amount_to_risk'],
            "OpenTime": datetime.datetime.now()
        }
        self.open_trades.append(trade)
        self.current_exposure += trade_value

    def close_trade(self, trade_id: str, pnl: float):
        """
        Closes a trade and updates the P&L.
        """
        trade_to_close = next((t for t in self.open_trades if t["ID"] == trade_id), None)
        if trade_to_close:
            self.current_exposure -= trade_to_close["Value"]
            self.pnl_today += pnl
            self.open_trades = [t for t in self.open_trades if t["ID"] != trade_id]

    def get_state(self):
        """Returns the current state of the risk manager."""
        return {
            "pnl_today": self.pnl_today,
            "open_trades_count": len(self.open_trades),
            "current_exposure": self.current_exposure
        }
    
    def get_open_trades_df(self):
        """Returns the list of open trades as a pandas DataFrame."""
        if not self.open_trades:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.open_trades)
        # Format for better display
        df['OpenTime'] = df['OpenTime'].dt.strftime('%Y-%m-%d %H:%M:%S')
        return df[['ID', 'Ticker', 'Type', 'Entry', 'Size', 'Value', 'Risk', 'OpenTime']]

# Need to add entry_price, stop_loss, target to the trade_plan dict in trade_planner.py
# I will do that in the next step.
