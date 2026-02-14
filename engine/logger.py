import os
import pandas as pd
from datetime import datetime

DATA_DIR = "data"
LOG_FILE = os.path.join(DATA_DIR, "trade_log.csv")


def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


def log_trade(pair, mode, scenario, probability, r_value, equity_after):
    ensure_data_dir()

    row = {
        "Timestamp": datetime.now(),
        "Pair": pair,
        "Mode": mode,
        "Scenario": scenario,
        "Probability": probability,
        "R": r_value,
        "Equity_After": equity_after
    }

    file_exists = os.path.exists(LOG_FILE)

    df = pd.DataFrame([row])
    df.to_csv(LOG_FILE, mode="a", header=not file_exists, index=False)
