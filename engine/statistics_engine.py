import pandas as pd


def compute_statistics(df):

    if df.empty:
        return None

    total = len(df)
    wins = df[df["R"] > 0]
    losses = df[df["R"] < 0]

    winrate = (len(wins) / total) * 100
    avg_r = df["R"].mean()

    avg_win = wins["R"].mean() if not wins.empty else 0
    avg_loss = losses["R"].mean() if not losses.empty else 0

    expectancy = (len(wins)/total * avg_win) + (len(losses)/total * avg_loss)

    breakdown = df.groupby("Scenario")["R"].mean().to_dict()

    df["Prob_Bucket"] = pd.cut(
        df["Probability"],
        bins=[0, 40, 60, 80, 100],
        labels=["Low", "Medium", "Medium-High", "High"]
    )

    prob_breakdown = df.groupby("Prob_Bucket")["R"].mean().to_dict()

    return {
        "total": total,
        "winrate": winrate,
        "avg_r": avg_r,
        "expectancy": expectancy,
        "scenario_breakdown": breakdown,
        "probability_breakdown": prob_breakdown
    }
