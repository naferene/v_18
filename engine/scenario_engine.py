def confidence_label(prob):
    if prob >= 75:
        return "High"
    elif prob >= 60:
        return "Medium-High"
    elif prob >= 45:
        return "Medium"
    else:
        return "Low"

def score_scenarios(trend, funding, oi_trend, rsi):

    scenarios = []

    score = 0
    if trend == "Uptrend":
        score += 2
    if oi_trend == "Rising":
        score += 1.5
    if funding > 0.03:
        score -= 1
    if rsi >= 70:
        score -= 0.5

    prob = max(min(50 + score * 5, 90), 10)

    scenarios.append({
        "name": "Pullback Continuation",
        "probability": prob,
        "confidence": confidence_label(prob),
        "reason": "Trend structure intact with OI participation."
    })

    score = 0
    if funding > 0.03:
        score += 1.5
    if rsi >= 70:
        score += 1

    prob = max(min(40 + score * 5, 80), 10)

    scenarios.append({
        "name": "Liquidity Flush",
        "probability": prob,
        "confidence": confidence_label(prob),
        "reason": "Crowded positioning may trigger short-term sweep."
    })

    score = 0
    if trend == "Uptrend":
        score += 1
    if rsi >= 75:
        score -= 1

    prob = max(min(35 + score * 5, 75), 5)

    scenarios.append({
        "name": "Late Breakout",
        "probability": prob,
        "confidence": confidence_label(prob),
        "reason": "Breakout possible but extension risk exists."
    })

    return sorted(scenarios, key=lambda x: x["probability"], reverse=True)
