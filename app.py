import streamlit as st
import pandas as pd
import os

from engine.state_manager import load_state, save_state, reset_daily_if_needed, update_streak
from engine.risk_engine import calculate_risk_plan
from engine.behavior_engine import calculate_behavior_metrics
from engine.scenario_engine import score_scenarios, recommended_action
from engine.statistics_engine import compute_statistics
from engine.logger import log_trade

DATA_DIR = "data"
LOG_FILE = os.path.join(DATA_DIR, "trade_log.csv")

st.set_page_config(layout="centered")
st.title("📱 Futures Behavior Engine")

state = load_state()
state = reset_daily_if_needed(state)

tab1, tab2, tab3 = st.tabs(["Analyze", "Trade Log", "Statistics"])

# ======================================
# TAB 1 — ANALYZE
# ======================================
with tab1:

    st.subheader("Account Snapshot")

    col1, col2, col3 = st.columns(3)
    col1.metric("Equity", f"${round(state['equity'], 2)}")
    col2.metric("Daily Loss", f"${round(state['daily_loss'], 2)}")
    col3.metric("Streak", state["current_streak"])

    st.divider()

    mode = st.radio("Execution Profile", ["Intraday", "Scalping"])

    pair = st.text_input("Pair", "BTCUSDT")
    trend = st.selectbox("Trend", ["Uptrend", "Downtrend"])
    entry = st.number_input("Entry", 0.0)
    sl = st.number_input("Stop Loss", 0.0)
    tp = st.number_input("Take Profit", 0.0)
    funding = st.number_input("Funding Rate (%)", 0.0)
    oi_trend = st.selectbox("OI Trend", ["Rising", "Falling", "Flat"])
    overextended = st.checkbox("Overextended Move?")

    if st.button("Analyze"):

        behavior = calculate_behavior_metrics(
            trend, funding, oi_trend, overextended)
        scenarios = score_scenarios(
            trend, funding, oi_trend, overextended, mode)

        st.subheader("Market Overview")
        st.write(behavior)

        st.subheader("Scenario Ranking")

        for s in scenarios:
            st.markdown(f"### {s['name']} ({s['confidence']})")
            st.progress(int(s["probability"]))
            st.write(f"Probability: {round(s['probability'], 1)}%")
            st.write(s["reason"])
            st.divider()

        primary = scenarios[0]

        st.subheader("Recommended Action")
        st.info(recommended_action(primary))

        risk = calculate_risk_plan(
            state["equity"],
            state["risk_percent"],
            state["leverage"],
            entry,
            sl,
            tp
        )

        if risk:
            st.subheader("Risk Plan")
            st.write(risk)

            r_input = st.number_input(
                "Enter R-Multiple after trade closes", 0.0)

            if st.button("Close Trade"):

                equity_new = state["equity"] + (risk["risk_amount"] * r_input)

                if r_input < 0:
                    state["daily_loss"] += abs(risk["risk_amount"] * r_input)

                state["equity"] = equity_new
                update_streak(state, r_input)
                save_state(state)

                log_trade(
                    pair, mode, primary["name"], primary["probability"], r_input, equity_new)

                st.success(f"Equity Updated → ${round(equity_new, 2)}")

# ======================================
# TAB 2 — TRADE LOG
# ======================================
with tab2:
    if os.path.exists(LOG_FILE):
        df = pd.read_csv(LOG_FILE)
        st.dataframe(df)
        st.download_button("Download CSV", df.to_csv(
            index=False), "trade_log.csv")
    else:
        st.write("No trades yet.")

# ======================================
# TAB 3 — STATISTICS
# ======================================
with tab3:
    if os.path.exists(LOG_FILE):
        df = pd.read_csv(LOG_FILE)

        stats = compute_statistics(df)

        if stats:
            st.metric("Total Trades", stats["total"])
            st.metric("Winrate (%)", round(stats["winrate"], 2))
            st.metric("Average R", round(stats["avg_r"], 2))
            st.metric("Expectancy", round(stats["expectancy"], 2))

            st.subheader("Scenario Breakdown (Avg R)")
            st.write(stats["scenario_breakdown"])

            st.subheader("Probability Bucket Breakdown (Avg R)")
            st.write(stats["probability_breakdown"])

            df["Cumulative_R"] = df["R"].cumsum()
            st.line_chart(df["Cumulative_R"])
