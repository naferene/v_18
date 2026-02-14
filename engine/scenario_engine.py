def confidence_label(prob):
    if prob >= 75:
        return "High"
    elif prob >= 60:
        return "Medium-High"
    elif prob >= 45:
        return "Medium"
    else:
        return "Low"


def score_scenarios(trend, funding, oi_trend, overextended, mode="Intraday"):

    scenarios = []

    # ==========================
    # PULLBACK CONTINUATION
    # ==========================
    score = 0

    if trend == "Uptrend":
        score += 2
    if oi_trend == "Rising":
        score += 1.5

    if funding > 0.03:
        score -= 1

    if overextended:
        score -= 0.5

    if mode == "Scalping":
        score -= 0.5  # less weight on macro pullback

    prob = max(min(50 + score * 5, 90), 10)

    scenarios.append({
        "name": "Pullback Continuation",
        "probability": prob,
        "confidence": confidence_label(prob),
        "reason": "Trend intact + OI support; funding & extension reduce conviction."
    })

    # ==========================
    # LIQUIDITY FLUSH
    # ==========================
    score = 0

    if funding > 0.03:
        score += 1.5

    if oi_trend == "Rising":
        score += 1

    if trend == "Uptrend":
        score -= 1

    prob = max(min(40 + score * 5, 80), 10)

    scenarios.append({
        "name": "Liquidity Flush",
        "probability": prob,
        "confidence": confidence_label(prob),
        "reason": "Crowded positioning may trigger short-term sweep."
    })

    # ==========================
    # LATE BREAKOUT
    # ==========================
    score = 0

    if trend == "Uptrend":
        score += 1

    if overextended:
        score -= 1

    if mode == "Scalping":
        score += 1  # breakout more relevant in scalp

    prob = max(min(35 + score * 5, 75), 5)

    scenarios.append({
        "name": "Late Breakout",
        "probability": prob,
        "confidence": confidence_label(prob),
        "reason": "Breakout possible but extension increases risk."
    })

    scenarios = sorted(scenarios, key=lambda x: x["probability"], reverse=True)
    return scenarios


def recommended_action(primary_scenario):
    name = primary_scenario["name"]
    prob = primary_scenario["probability"]

    if name == "Pullback Continuation":
        return "Pullback preferred; avoid chasing breakout at resistance."
    elif name == "Liquidity Flush":
        return "Downside liquidity sweep possible; counter-trend risk elevated."
    elif name == "Late Breakout":
        return "Breakout viable but extension risk present."
    else:
        return "No strong directional edge."
