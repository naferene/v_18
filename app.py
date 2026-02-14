import streamlit as st
import pandas as pd
import os

from engine.state_manager import load_state, save_state, reset_daily_if_needed, update_streak
from engine.behavior_engine import calculate_behavior
from engine.scenario_engine import score_scenarios
from engine.risk_engine import calculate_risk
from engine.statistics_engine import compute_stats
from engine.logger import log_trade

DATA_DIR = "data"
LOG_FILE = os.path.join(DATA_DIR, "trade_log.csv")

st.set_page_config(layout="centered")
st.title("📱 Futures Behavior Engine")

# =========================
# LOAD STATE
# =========================
state = load_state()
state = reset_daily_if_needed(state)

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

    # -------- USER INPUT --------
    pair = st.text_input("Pair", "BTCUSDT")
    execution = st.radio("Execution Profile", ["Intraday", "Scalping"])

    trend = st.selectbox("Trend", ["Uptrend", "Downtrend"])
    last_hl = st.number_input("Last HL (or LH for Downtrend)", value=0.0)
    last_hh = st.number_input("Last HH (or LL for Downtrend)", value=0.0)

    funding = st.number_input("Funding Rate (%)", value=0.0)
    oi_trend = st.selectbox("OI Trend", ["Rising", "Falling", "Flat"])
    rsi = st.number_input("RSI Value", value=50.0)

    if st.button("Analyze"):

        # =========================
        # BEHAVIOR ENGINE
        # =========================
        behavior = calculate_behavior(trend, funding, oi_trend, rsi)

        st.subheader("Market Overview")
        st.write({
            "Market Phase": behavior["phase"],
            "Heat Score": behavior["heat"],
            "Crowding Risk": behavior["crowding"],
            "Squeeze Risk": behavior["squeeze"],
            "RSI Status": behavior["rsi_status"]
        })

        # =========================
        # SCENARIO ENGINE
        # =========================
        scenarios = score_scenarios(trend, funding, oi_trend, rsi)

        st.subheader("Scenario Ranking")

        for s in scenarios:
            st.markdown(f"### {s['name']} ({s['confidence']})")
            st.progress(int(s["probability"]))
            st.write(f"Probability: {round(s['probability'],1)}%")
            st.write(s["reason"])
            st.divider()

        primary = scenarios[0]

        # =========================
        # DYNAMIC ENTRY LOGIC (HEAT ADJUSTED)
        # =========================
        heat = behavior["heat"]

        if heat <= 40:
            entry_low_pct = 0.001
            entry_high_pct = 0.0025
            sl_pct = 0.0025
            tp_ext = 0.0
        elif heat <= 70:
            entry_low_pct = 0.002
            entry_high_pct = 0.004
            sl_pct = 0.004
            tp_ext = 0.005
        else:
            entry_low_pct = 0.003
            entry_high_pct = 0.006
            sl_pct = 0.006
            tp_ext = 0.01

        if trend == "Uptrend":
            entry_low = last_hl * (1 + entry_low_pct)
            entry_high = last_hl * (1 + entry_high_pct)
            sl = last_hl * (1 - sl_pct)
            tp1 = last_hh
            tp2 = last_hh * (1 + tp_ext)
        else:
            entry_low = last_hl * (1 - entry_high_pct)
            entry_high = last_hl * (1 - entry_low_pct)
            sl = last_hl * (1 + sl_pct)
            tp1 = last_hh
            tp2 = last_hh * (1 - tp_ext)

        midpoint = (entry_low + entry_high) / 2

        st.subheader("Top Scenario Execution Plan")
        st.write({
            "Entry Zone": f"{round(entry_low,6)} – {round(entry_high,6)}",
            "Midpoint Entry": round(midpoint,6),
            "Stop Loss": round(sl,6),
            "Take Profit 1": round(tp1,6),
            "Take Profit 2": round(tp2,6)
        })

        # =========================
        # RISK ENGINE
        # =========================
        risk = calculate_risk(
            state["equity"],
            state["risk_percent"],
            state["leverage"],
            midpoint,
            sl,
            tp1
        )

        if risk:
            st.subheader("Risk Plan (1% Model)")
            st.write({
                "Risk Amount": round(risk["risk_amount"],2),
                "Position Size": round(risk["position_size"],2),
                "Notional": round(risk["notional"],2),
                "Margin Required": round(risk["margin"],2),
                "Potential Profit": round(risk["potential_profit"],2),
                "R:R": round(risk["rr"],2),
                "Warnings": risk["warnings"]
            })

        # =========================
        # RECOMMENDED ACTION
        # =========================
        st.subheader("Recommended Action")
        if primary["name"] == "Pullback Continuation":
            st.info("Pullback preferred; avoid chasing breakout at resistance.")
        elif primary["name"] == "Liquidity Flush":
            st.info("Short-term liquidity sweep possible; counter-trend risk elevated.")
        else:
            st.info("Breakout viable but extension risk present.")

        # =========================
        # BEHAVIORAL GUARDRAIL
        # =========================
        st.subheader("Behavioral Guardrail")
        st.write(f"Invalidation Level: {round(sl,6)}")
        st.write("Floating PnL is NOT a valid exit reason.")
        if state["current_streak"] <= -2:
            st.warning("Consecutive losses detected. Consider conservative execution.")

        # =========================
        # CLOSE TRADE
        # =========================
        st.subheader("Close Trade")

        r_input = st.number_input("Enter R-Multiple", value=0.0)

        if st.button("Update Equity"):

            equity_new = state["equity"] + (risk["risk_amount"] * r_input)

            if r_input < 0:
                state["daily_loss"] += abs(risk["risk_amount"] * r_input)

            state["equity"] = equity_new
            update_streak(state, r_input)
            save_state(state)

            log_trade(pair, primary["name"], primary["probability"], r_input, equity_new)

            st.success(f"Equity Updated → ${round(equity_new,2)}")

# =========================
# TAB 2 — TRADE LOG
# =========================
with tab2:
    if os.path.exists(LOG_FILE):
        df = pd.read_csv(LOG_FILE)
        st.dataframe(df)
        st.download_button("Download CSV", df.to_csv(index=False), "trade_log.csv")
    else:
        st.write("No trades logged yet.")

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

            st.subheader("Scenario Breakdown (Avg R)")
            st.write(stats["scenario_breakdown"])

            st.subheader("Probability Bucket Breakdown (Avg R)")
            st.write(stats["probability_breakdown"])

            df["Cumulative_R"] = df["R"].cumsum()
            st.line_chart(df["Cumulative_R"])
    else:
        st.write("No statistics yet.")
