# This is the main entry point for the Tradee Streamlit web application.

import streamlit as st
from data_fetcher.yfinance_client import YFinanceClient
from modules.market_regime import get_market_regime
from modules.options_engine import find_option_walls
from modules.risk_manager import RiskManager
from modules.alert_manager import AlertManager
from config import TICKERS
import pandas as pd

# --- Page Configuration ---
st.set_page_config(
    page_title="Tradee Decision-Support System",
    page_icon="📊",
    layout="wide"
)

# --- Initialize Managers in Session State ---
if 'risk_manager' not in st.session_state:
    st.session_state.risk_manager = RiskManager(portfolio_value=10000.0)
if 'alert_manager' not in st.session_state:
    st.session_state.alert_manager = AlertManager()


# --- Sidebar ---
st.sidebar.title("Controls")
selected_ticker = st.sidebar.selectbox("Select a Ticker", TICKERS)

st.sidebar.title("Risk Manager Status")
rm_state = st.session_state.risk_manager.get_state()
st.sidebar.metric("Today's P&L", f"${rm_state['pnl_today']:.2f}")
st.sidebar.metric("Open Trades", rm_state['open_trades_count'])
st.sidebar.metric("Current Exposure", f"${rm_state['current_exposure']:.2f}")

st.sidebar.title("Alerts")
with st.sidebar.form("alert_form"):
    st.write("Set a new price alert:")
    alert_ticker = st.text_input("Ticker", value=selected_ticker)
    alert_condition = st.radio("Condition", ("Rises Above", "Falls Below"))
    alert_price = st.number_input("Target Price", min_value=0.01)
    submitted_alert = st.form_submit_button("Set Alert")

    if submitted_alert:
        condition_map = {"Rises Above": "above", "Falls Below": "below"}
        st.session_state.alert_manager.add_alert(
            ticker=alert_ticker,
            condition=condition_map[alert_condition],
            target_price=alert_price
        )
        st.success(f"Alert set for {alert_ticker}!")

st.sidebar.write("Active Alerts:")
active_alerts = st.session_state.alert_manager.get_active_alerts()
if not active_alerts:
    st.sidebar.info("No active alerts.")
else:
    for alert in active_alerts:
        st.sidebar.text(f"- {alert['ticker']}: {alert['condition']} {alert['target_price']}")


# --- Main Application ---
st.title(f"📊 Tradee Analysis for: {selected_ticker}")

if selected_ticker:
    with st.spinner(f"Fetching data for {selected_ticker}..."):
        try:
            # --- 1. Data Fetching & Alert Check ---
            client = YFinanceClient(selected_ticker)
            info = client.get_info()
            current_price = info.get('previousClose') # Using previous close as a proxy for current price

            if current_price:
                triggered_messages = st.session_state.alert_manager.check_alerts(selected_ticker, current_price)
                for message in triggered_messages:
                    st.success(message)
                    st.balloons()

            hist_data = client.get_historical_data(period="2y", interval="1d")
            
            st.header(f"{info.get('longName', selected_ticker)}")
            st.caption(f"Current Price: ${current_price:.2f} | Sector: {info.get('sector', 'N/A')} | Industry: {info.get('industry', 'N/A')}")

            if hist_data.empty:
                st.error("Could not fetch historical data. The ticker may be invalid or delisted.")
            else:
                # --- 2. Market Regime Analysis ---
                st.subheader("Market Regime")
                regime, volatility_pct = get_market_regime(hist_data)
                
                col1, col2 = st.columns(2)
                col1.metric("Current Regime", regime)
                col2.metric("Volatility (ATR %)", f"{volatility_pct}%")

                # --- 3. Options Intelligence Analysis ---
                st.subheader("Options Intelligence")
                expirations = client.ticker.options
                if not expirations:
                    st.info("No options data available for this ticker.")
                else:
                    selected_expiry = st.selectbox("Select an Expiration Date", expirations)
                    if selected_expiry:
                        calls, puts = client.get_options_chain(selected_expiry)
                        
                        walls = find_option_walls(calls, puts)
                        if walls:
                            cw = walls['call_wall']
                            pw = walls['put_wall']
                            
                            col1, col2 = st.columns(2)
                            col1.metric(
                                label=f"Call Wall (Resistance)",
                                value=f"{cw['strike']}",
                                help=f"Highest Call OI: {cw['oi']:,}"
                            )
                            col2.metric(
                                label=f"Put Wall (Support)",
                                value=f"{pw['strike']}",
                                help=f"Highest Put OI: {pw['oi']:,}"
                            )
                        else:
                            st.warning("Could not determine Put/Call walls (insufficient Open Interest).")
                
                # --- 4. Active Trade Monitor ---
                st.subheader("Active Trade Monitor")
                open_trades_df = st.session_state.risk_manager.get_open_trades_df()
                if open_trades_df.empty:
                    st.info("No open trades.")
                else:
                    st.dataframe(open_trades_df, use_container_width=True)

                # --- 5. Trade Planner & Risk Check ---
                st.subheader("Trade Planner")
                with st.form(key="trade_planner_form"):
                    st.write("Enter your trade parameters to calculate position size and risk-reward.")
                    
                    # Inputs
                    col1, col2 = st.columns(2)
                    with col1:
                        portfolio_value = st.number_input("Portfolio Value ($)", min_value=1.0, value=10000.0, step=1000.0)
                        # Update RM portfolio value when user changes it
                        if portfolio_value != st.session_state.risk_manager.portfolio_value:
                            st.session_state.risk_manager.portfolio_value = portfolio_value
                        
                        risk_percent = st.number_input("Risk per Trade (%)", min_value=0.1, max_value=100.0, value=1.0, step=0.5)
                    with col2:
                        entry_price = st.number_input("Entry Price", min_value=0.01, value=float(info.get('previousClose', 100.0)))
                        stop_loss_price = st.number_input("Stop-Loss Price", min_value=0.01, value=float(info.get('previousClose', 100.0) * 0.98))
                        target_price = st.number_input("Target Price", min_value=0.01, value=float(info.get('previousClose', 100.0) * 1.05))

                    # Submit Button
                    submitted = st.form_submit_button("Calculate & Check Risk")

                    if submitted:
                        from modules.trade_planner import calculate_trade_plan
                        plan = calculate_trade_plan(
                            entry=entry_price,
                            stop_loss=stop_loss_price,
                            target=target_price,
                            portfolio_value=portfolio_value,
                            risk_percent=risk_percent
                        )
                        # Store the plan in session state to access it after the form is cleared
                        st.session_state.last_plan = plan

                # Display results and execute button outside the form
                if 'last_plan' in st.session_state and st.session_state.last_plan:
                    plan = st.session_state.last_plan
                    if isinstance(plan, str):
                        st.error(plan)
                        st.session_state.last_plan = None # Clear the plan after displaying error
                    else:
                        st.write(f"**Calculated Plan for a {plan['trade_type']} Trade:**")
                        res_col1, res_col2, res_col3 = st.columns(3)
                        res_col1.metric("Position Size (Shares)", f"{plan['position_size']:.2f}")
                        res_col2.metric("Risk/Reward Ratio", f"1 : {plan['risk_reward_ratio']:.2f}")
                        res_col3.metric("Amount at Risk", f"${plan['amount_to_risk']:.2f}")
                        
                        res_col1.metric("Potential Profit", f"${plan['potential_profit']:.2f}", delta_color="normal")
                        res_col2.metric("Potential Loss", f"${plan['potential_loss']:.2f}", delta_color="inverse")

                        # Perform Risk Check
                        st.write("**Pre-Trade Risk Check:**")
                        trade_value = plan['position_size'] * entry_price
                        violations = st.session_state.risk_manager.check_trade_violation(
                            amount_to_risk=plan['amount_to_risk'],
                            trade_value=trade_value
                        )

                        if not violations:
                            st.success("✅ TRADE APPROVED: Compliant with all risk rules.")
                            if st.button("Execute Mock Trade"):
                                st.session_state.risk_manager.add_trade(ticker=selected_ticker, trade_plan=plan)
                                st.success(f"Trade {st.session_state.risk_manager.open_trades[-1]['ID']} executed and added to monitor.")
                                st.session_state.last_plan = None # Clear plan after execution
                                st.experimental_rerun()
                        else:
                            for violation in violations:
                                st.warning(f"⚠️ VIOLATION: {violation}")
                            st.session_state.last_plan = None # Clear plan if violations exist


        except Exception as e:
            st.error(f"An error occurred while analyzing {selected_ticker}: {e}")

else:
    st.info("Please select a ticker from the sidebar to begin analysis.")

# To run this application:
# 1. Make sure you have installed the requirements: pip install -r requirements.txt
# 2. Run the command in your terminal: streamlit run main.py