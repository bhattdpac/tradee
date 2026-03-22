# This module will contain the logic for the Alert System.
import datetime

class AlertManager:
    """
    Manages price alerts for different tickers.
    This is a stateful class designed to be instantiated once per session.
    """
    def __init__(self):
        self.alerts = []

    def add_alert(self, ticker: str, condition: str, target_price: float):
        """
        Adds a new price alert.
        :param ticker: The ticker symbol to monitor.
        :param condition: 'above' or 'below'.
        :param target_price: The price level for the alert.
        """
        alert_id = f"{ticker}_{len(self.alerts)}_{datetime.datetime.now().strftime('%S')}"
        alert = {
            "id": alert_id,
            "ticker": ticker.upper(),
            "condition": condition,
            "target_price": target_price,
            "created_at": datetime.datetime.now(),
            "triggered": False,
            "triggered_at": None
        }
        self.alerts.append(alert)

    def check_alerts(self, ticker: str, current_price: float):
        """
        Checks all active alerts for a given ticker against its current price.
        Marks alerts as triggered if the condition is met.
        
        :param ticker: The ticker symbol to check.
        :param current_price: The current price of the ticker.
        :return: A list of newly triggered alert messages.
        """
        newly_triggered_messages = []
        for alert in self.alerts:
            # Check only for the relevant ticker and if the alert hasn't been triggered yet
            if alert['ticker'] == ticker.upper() and not alert['triggered']:
                condition_met = False
                if alert['condition'] == 'above' and current_price > alert['target_price']:
                    condition_met = True
                    message = f"📈 ALERT: {ticker} has risen above your target of {alert['target_price']}! Current price: {current_price}"
                elif alert['condition'] == 'below' and current_price < alert['target_price']:
                    condition_met = True
                    message = f"📉 ALERT: {ticker} has fallen below your target of {alert['target_price']}! Current price: {current_price}"

                if condition_met:
                    alert['triggered'] = True
                    alert['triggered_at'] = datetime.datetime.now()
                    newly_triggered_messages.append(message)
        
        return newly_triggered_messages

    def get_active_alerts(self):
        """Returns a list of all non-triggered alerts."""
        return [a for a in self.alerts if not a['triggered']]

    def get_triggered_alerts(self):
        """Returns a list of all triggered alerts."""
        return [a for a in self.alerts if a['triggered']]
