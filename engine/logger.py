import os
import pandas as pd
from datetime import datetime

DATA_DIR = "data"
LOG_FILE = os.path.join(DATA_DIR, "trade_log.csv")

def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def log_trade(row):
    ensure_data_dir()
    df = pd.DataFrame([row])
    file_exists = os.path.exists(LOG_FILE)
    df.to_csv(LOG_FILE, mode="a", header=not file_exists, index=False)
