import os
import pandas as pd

DATA_DIR = "data"
LOG_FILE = os.path.join(DATA_DIR, "trade_log.csv")

def log_trade(pair, scenario, probability, r_multiple, equity):

    os.makedirs(DATA_DIR, exist_ok=True)

    trade_data = {
        "Pair": pair,
        "Scenario": scenario,
        "Probability": probability,
        "R": r_multiple,
        "Equity": equity
    }

    df_new = pd.DataFrame([trade_data])

    if os.path.exists(LOG_FILE):
        df_new.to_csv(LOG_FILE, mode="a", header=False, index=False)
    else:
        df_new.to_csv(LOG_FILE, index=False)
