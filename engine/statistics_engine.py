import pandas as pd

def compute_stats(df):
    if df.empty:
        return None

    total = len(df)
    wins = df[df["R"] > 0]
    losses = df[df["R"] < 0]

    winrate = len(wins) / total * 100
    avg_r = df["R"].mean()

    expectancy = (winrate / 100 * wins["R"].mean() if not wins.empty else 0) + \
                 ((1 - winrate / 100) * losses["R"].mean() if not losses.empty else 0)

    return {
        "total": total,
        "winrate": winrate,
        "avg_r": avg_r,
        "expectancy": expectancy
    }
