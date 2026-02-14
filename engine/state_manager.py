import os
import json
from datetime import datetime

DATA_DIR = "data"
STATE_FILE = os.path.join(DATA_DIR, "state.json")

DEFAULT_STATE = {
    "equity": 1000.0,
    "risk_percent": 1.0,
    "leverage": 5,
    "daily_loss": 0.0,
    "current_streak": 0,
    "last_trade_date": str(datetime.now().date())
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
