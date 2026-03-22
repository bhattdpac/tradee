# Handles all communication with the yfinance API
import yfinance as yf
import pandas as pd

class YFinanceClient:
    def __init__(self, ticker):
        self.ticker = yf.Ticker(ticker)

    def get_historical_data(self, period="1y", interval="1d"):
        """
        Fetches historical price data.
        :param period: Data period (e.g., "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max")
        :param interval: Data interval (e.g., "1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo")
        :return: Pandas DataFrame with historical data
        """
        return self.ticker.history(period=period, interval=interval)

    def get_options_chain(self, date=None):
        """
        Fetches the options chain for a specific expiration date.
        :param date: Expiration date in 'YYYY-MM-DD' format. If None, fetches for the next available date.
        :return: A tuple of (calls, puts) DataFrames.
        """
        if date:
            return self.ticker.option_chain(date)
        else:
            # If no date is specified, get the first available expiration date
            expirations = self.ticker.options
            if expirations:
                return self.ticker.option_chain(expirations[0])
            else:
                return pd.DataFrame(), pd.DataFrame() # Return empty dataframes if no options

    def get_info(self):
        """
        Fetches general information about the ticker.
        :return: Dictionary with ticker info.
        """
        return self.ticker.info

if __name__ == '__main__':
    # Example usage
    client = YFinanceClient("NIFTYBEES.NS") # Using Nifty Bees as an example for Nifty 50

    # Get historical data
    hist_data = client.get_historical_data(period="1mo", interval="1d")
    print("--- Historical Data ---")
    print(hist_data.tail())

    # Get info
    info = client.get_info()
    print("\n--- Ticker Info ---")
    print(f"Symbol: {info.get('symbol')}")
    print(f"Long Name: {info.get('longName')}")
    print(f"Previous Close: {info.get('previousClose')}")

    # Note: Options data for indices like '^NSEI' might not be available directly.
    # You often need to use specific futures/options tickers or look at ETFs.
    # For demonstration, let's try with a stock that has options.
    stock_client = YFinanceClient("RELIANCE.NS")
    expirations = stock_client.ticker.options
    if expirations:
        print(f"\n--- Options for RELIANCE.NS ---")
        print(f"Available expiration dates: {expirations[:5]}")
        calls, puts = stock_client.get_options_chain(expirations[0])
        print("\n--- Sample Call Options ---")
        print(calls.head())
        print("\n--- Sample Put Options ---")
        print(puts.head())
    else:
        print("\n--- No options data available for RELIANCE.NS ---")
