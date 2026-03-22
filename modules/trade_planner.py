# This module will contain the logic for the Trade Planner.

def calculate_trade_plan(entry, stop_loss, target, portfolio_value, risk_percent):
    """
    Calculates position size and risk-reward based on trade parameters.

    :param entry: The entry price for the trade.
    :param stop_loss: The stop-loss price for the trade.
    :param target: The target price for the trade.
    :param portfolio_value: The total value of the trading portfolio.
    :param risk_percent: The percentage of the portfolio to risk on this single trade.
    :return: A dictionary with the calculated trade plan, or an error string.
    """
    if entry <= 0 or stop_loss <= 0 or target <= 0 or portfolio_value <= 0:
        return "Prices and portfolio value must be positive."
    if risk_percent <= 0 or risk_percent > 100:
        return "Risk percentage must be between 0 and 100."
    if entry == stop_loss:
        return "Entry and Stop Loss cannot be the same."

    # Determine if it's a long or short trade
    is_long = entry > stop_loss

    if is_long:
        if target <= entry:
            return "Target price must be above entry for a long trade."
        risk_per_share = entry - stop_loss
        reward_per_share = target - entry
    else: # Short trade
        if target >= entry:
            return "Target price must be below entry for a short trade."
        risk_per_share = stop_loss - entry
        reward_per_share = entry - target

    # Calculations
    risk_reward_ratio = reward_per_share / risk_per_share
    amount_to_risk = (risk_percent / 100) * portfolio_value
    position_size = amount_to_risk / risk_per_share
    
    potential_profit = position_size * reward_per_share
    potential_loss = amount_to_risk # This is the same as position_size * risk_per_share

    return {
        "entry_price": entry,
        "stop_loss": stop_loss,
        "target": target,
        "trade_type": "Long" if is_long else "Short",
        "position_size": round(position_size, 2),
        "risk_reward_ratio": round(risk_reward_ratio, 2),
        "potential_profit": round(potential_profit, 2),
        "potential_loss": round(potential_loss, 2),
        "amount_to_risk": round(amount_to_risk, 2)
    }