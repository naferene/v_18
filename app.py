import streamlit as st
import pandas as pd
import os
import sys
sys.path.append(os.path.dirname(__file__))


from engine.directional_engine import calculate_directional_score
from engine.regime_engine import detect_regime
from engine.execution_engine import generate_execution_plan
from engine.risk_engine import calculate_risk
from engine.state_manager import load_state, save_state, reset_daily_if_needed
from engine.logger import log_trade
from engine.statistics_engine import compute_stats

DATA_DIR = "data"
LOG_FILE = os.path.join(DATA_DIR, "trade_log.csv")

st.set_page_config(layout="centered")
st.title("📱 Mini Institutional Futures Engine")

state = load_state()
state = reset_daily_if_needed(state)

tab1, tab2, tab3 = st.tabs(["Analyze", "Trade Log", "Statistics"])

# ==============================
# TAB 1 — ANALYZE
# ==============================
with tab1:

    st.subheader("Account Snapshot")
    st.metric("Equity", f"${round(state['equity'],2)}")
    st.metric("Leverage", f"{state['leverage']}x")

    st.divider()

    # ===== INPUT =====
    pair = st.text_input("Pair", "BTCUSDT")
    execution = st.radio("Execution", ["Intraday", "Scalping"])
    price = st.number_input("Current Price", value=0.0)

    st.subheader("Structure")
    trend = st.selectbox("Trend", ["Uptrend", "Downtrend"])
    hl = st.number_input("Last HL / LH", value=0.0)
    hh = st.number_input("Last HH / LL", value=0.0)
    break_confirmed = st.checkbox("Break Confirmed")

    st.subheader("Positioning")
    funding = st.number_input("Funding (%)", value=0.0)
    oi_trend = st.selectbox("OI Trend", ["Rising", "Falling", "Flat"])
    ls_ratio = st.number_input("L/S Ratio", value=1.0)

    st.subheader("Context")
    rsi = st.number_input("RSI (10)", value=50.0)
    high_24 = st.number_input("24h High", value=0.0)
    low_24 = st.number_input("24h Low", value=0.0)
    change_24 = st.number_input("24h % Change", value=0.0)
    volume_24 = st.number_input("24h Volume (USDT)", value=0.0)

    st.subheader("Micro Confirmation")
    micro = st.selectbox("Confirmation Strength", ["None", "Weak", "Strong"])

    if st.button("Analyze"):

        data = {
            "trend": trend,
            "price": price,
            "hl": hl,
            "hh": hh,
            "break_confirmed": break_confirmed,
            "funding": funding,
            "oi_trend": oi_trend,
            "ls_ratio": ls_ratio,
            "rsi": rsi,
            "high_24": high_24,
            "low_24": low_24,
            "micro": micro
        }

        score, breakdown = calculate_directional_score(data)

        if score >= 70:
            verdict = "🟢 GO"
        elif score >= 60:
            verdict = "🟡 Conditional"
        else:
            verdict = "🔴 NO-GO"

        regime = detect_regime(volume_24, change_24, oi_trend, funding)
        plan = generate_execution_plan(data)
        risk = calculate_risk(
            state["equity"],
            (plan["entry_low"] + plan["entry_high"]) / 2,
            plan["sl"],
            plan["tp1"],
            leverage=state["leverage"],
            risk_percent=state["risk_percent"]
        )

        st.subheader("Result")
        st.metric("Composite Score", f"{score} / 100")
        st.markdown(f"### {verdict}")
        st.write("Regime:", regime)

        st.subheader("Execution Plan")
        st.write({
            "Entry Zone": f"{round(plan['entry_low'],6)} – {round(plan['entry_high'],6)}",
            "Stop": round(plan["sl"],6),
            "TP1": round(plan["tp1"],6)
        })

        if risk:
            st.subheader("Risk Plan (5x)")
            st.write({
                "Risk": round(risk["risk_amount"],2),
                "Position Size": round(risk["position_size"],2),
                "Margin": round(risk["margin"],2),
                "R:R": round(risk["rr"],2)
            })

        with st.expander("Advanced Breakdown"):
            st.write(breakdown)

        if st.button("Save Trade"):
            log_trade({
                "Pair": pair,
                "Score": score,
                "Verdict": verdict,
                "Regime": regime,
                "R": 0
            })
            st.success("Trade Saved")

        st.subheader("Close Trade")
        r_value = st.number_input("R Multiple", value=0.0)

        if st.button("Update Equity"):
            risk_amount = state["equity"] * (state["risk_percent"] / 100)
            state["equity"] += risk_amount * r_value
            save_state(state)

            log_trade({
                "Pair": pair,
                "Score": score,
                "Verdict": verdict,
                "Regime": regime,
                "R": r_value
            })

            st.success(f"Equity Updated → ${round(state['equity'],2)}")

# ==============================
# TAB 2 — TRADE LOG
# ==============================
with tab2:
    if os.path.exists(LOG_FILE):
        df = pd.read_csv(LOG_FILE)
        st.dataframe(df)
        st.download_button("Download CSV", df.to_csv(index=False), "trade_log.csv")
    else:
        st.write("No trades logged yet.")

# ==============================
# TAB 3 — STATISTICS
# ==============================
with tab3:
    if os.path.exists(LOG_FILE):
        df = pd.read_csv(LOG_FILE)
        stats = compute_stats(df)

        if stats:
            st.metric("Total Trades", stats["total"])
            st.metric("Winrate (%)", round(stats["winrate"],2))
            st.metric("Average R", round(stats["avg_r"],2))
            st.metric("Expectancy", round(stats["expectancy"],2))
    else:
        st.write("No statistics yet.")
