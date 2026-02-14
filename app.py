import streamlit as st
import pandas as pd
import os
import sys
sys.path.append(os.path.dirname(__file__))

from engine.state_manager import load_state, save_state, reset_daily_if_needed, update_streak
from engine.regime_engine import calculate_regime
from engine.directional_engine import calculate_direction
from engine.execution_engine import generate_execution_plan
from engine.risk_engine import calculate_risk
from engine.statistics_engine import compute_stats
from engine.logger import log_trade

DATA_DIR = "data"
LOG_FILE = os.path.join(DATA_DIR, "trade_log.csv")

st.set_page_config(layout="centered")
st.title("📱 Futures Institutional Engine")

# =========================
# LOAD STATE
# =========================
state = load_state()
state = reset_daily_if_needed(state)

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "execution_plan" not in st.session_state:
    st.session_state.execution_plan = None
if "risk_plan" not in st.session_state:
    st.session_state.risk_plan = None

tab1, tab2, tab3 = st.tabs(["Analyze", "Trade Log", "Statistics"])

# =========================
# TAB 1 — ANALYZE
# =========================
with tab1:

    st.subheader("Account Snapshot")
    col1, col2, col3 = st.columns(3)
    col1.metric("Equity", f"${round(state['equity'],2)}")
    col2.metric("Daily Loss", f"${round(state['daily_loss'],2)}")
    col3.metric("Streak", state["current_streak"])

    st.divider()

    # INPUTS
    pair = st.text_input("Pair", "BTCUSDT")
    execution = st.radio("Execution Profile", ["Intraday", "Scalping"])

    trend = st.selectbox("Trend", ["Uptrend", "Downtrend"])
    last_hl = st.number_input("Last HL (or LH)", value=0.0)
    last_hh = st.number_input("Last HH (or LL)", value=0.0)

    funding = st.number_input("Funding Rate (%)", value=0.0)
    oi_trend = st.selectbox("OI Trend", ["Rising", "Falling", "Flat"])
    rsi = st.number_input("RSI (10)", value=50.0)

    st.divider()

    # =========================
    # ANALYZE BUTTON
    # =========================
    if st.button("Analyze"):

        regime = calculate_regime(funding, oi_trend, rsi)
        direction = calculate_direction(trend, regime)

        execution_plan = generate_execution_plan(
            trend,
            last_hl,
            last_hh,
            regime["heat_score"]
        )

        risk_plan = calculate_risk(
            state["equity"],
            state["risk_percent"],
            state["leverage"],
            execution_plan["entry"],
            execution_plan["sl"],
            execution_plan["tp"]
        )

        st.session_state.analysis_result = {
            "regime": regime,
            "direction": direction
        }

        st.session_state.execution_plan = execution_plan
        st.session_state.risk_plan = risk_plan

    # =========================
    # DISPLAY RESULTS
    # =========================
    if st.session_state.analysis_result:

        regime = st.session_state.analysis_result["regime"]
        execution_plan = st.session_state.execution_plan
        risk_plan = st.session_state.risk_plan

        st.subheader("Market Regime")
        st.write(regime)

        st.subheader("Execution Plan")
        st.write(execution_plan)

        if risk_plan:
            st.subheader("Risk Plan (1% / 5x)")
            st.write(risk_plan)

            r_input = st.number_input("R-Multiple Result", value=0.0)

            if st.button("Save Trade"):

                pnl = risk_plan["risk_amount"] * r_input
                new_equity = state["equity"] + pnl

                if r_input < 0:
                    state["daily_loss"] += abs(pnl)

                state["equity"] = new_equity
                update_streak(state, r_input)
                save_state(state)

                log_trade(
                    pair,
                    regime["phase"],
                    r_input,
                    new_equity
                )

                st.success(f"Trade Saved. Equity → ${round(new_equity,2)}")

# =========================
# TAB 2 — TRADE LOG
# =========================
with tab2:
    if os.path.exists(LOG_FILE):
        df = pd.read_csv(LOG_FILE)
        st.dataframe(df)
        st.download_button("Download CSV", df.to_csv(index=False), "trade_log.csv")
    else:
        st.write("No Trade Logs Yet.")

# =========================
# TAB 3 — STATISTICS
# =========================
with tab3:
    if os.path.exists(LOG_FILE):
        df = pd.read_csv(LOG_FILE)
        stats = compute_stats(df)

        if stats:
            st.metric("Total Trades", stats["total"])
            st.metric("Winrate (%)", round(stats["winrate"],2))
            st.metric("Average R", round(stats["avg_r"],2))
            st.metric("Expectancy", round(stats["expectancy"],2))

            df["Cumulative_R"] = df["R"].cumsum()
            st.line_chart(df["Cumulative_R"])
    else:
        st.write("No Statistics Yet.")
