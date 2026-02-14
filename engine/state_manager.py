import json
import os
from datetime import datetime

DATA_DIR = "data"
STATE_FILE = os.path.join(DATA_DIR, "state.json")

DEFAULT_STATE = {
    "equity": 1000.0,
    "risk_percent": 1.0,
    "max_daily_loss_percent": 3.0,
    "leverage": 5.0,
    "daily_loss": 0.0,
    "last_trade_date": str(datetime.now().date()),
    "current_streak": 0,
    "max_win_streak": 0,
    "max_loss_streak": 0
}


def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


def load_state():
    ensure_data_dir()
    if not os.path.exists(STATE_FILE):
        save_state(DEFAULT_STATE)
        return DEFAULT_STATE
    with open(STATE_FILE, "r") as f:
        return json.load(f)


def save_state(state):
    ensure_data_dir()
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)


def reset_daily_if_needed(state):
    today = str(datetime.now().date())
    if state["last_trade_date"] != today:
        state["daily_loss"] = 0.0
        state["last_trade_date"] = today
        save_state(state)
    return state


def update_streak(state, r_value):
    if r_value > 0:
        if state["current_streak"] >= 0:
            state["current_streak"] += 1
        else:
            state["current_streak"] = 1
        state["max_win_streak"] = max(
            state["max_win_streak"], state["current_streak"])
    elif r_value < 0:
        if state["current_streak"] <= 0:
            state["current_streak"] -= 1
        else:
            state["current_streak"] = -1
        state["max_loss_streak"] = min(
            state["max_loss_streak"], state["current_streak"])

    save_state(state)
    return state
