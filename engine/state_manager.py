import os
import json
from datetime import datetime

DATA_DIR = "data"
STATE_FILE = os.path.join(DATA_DIR, "state.json")

DEFAULT_STATE = {
    "equity": 1000,
    "daily_loss": 0,
    "risk_percent": 1,
    "leverage": 5,
    "current_streak": 0,
    "last_reset": datetime.now().strftime("%Y-%m-%d")
}


def load_state():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    if not os.path.exists(STATE_FILE):
        with open(STATE_FILE, "w") as f:
            json.dump(DEFAULT_STATE, f)
        return DEFAULT_STATE.copy()

    with open(STATE_FILE, "r") as f:
        return json.load(f)


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def reset_daily_if_needed(state):
    today = datetime.now().strftime("%Y-%m-%d")

    if state.get("last_reset") != today:
        state["daily_loss"] = 0
        state["last_reset"] = today
        save_state(state)

    return state


def update_streak(state, r_input):
    if r_input > 0:
        if state["current_streak"] >= 0:
            state["current_streak"] += 1
        else:
            state["current_streak"] = 1
    elif r_input < 0:
        if state["current_streak"] <= 0:
            state["current_streak"] -= 1
        else:
            state["current_streak"] = -1
