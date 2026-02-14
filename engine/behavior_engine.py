def calculate_behavior_metrics(trend, funding, oi_trend, overextended):

    heat_score = 50

    if trend == "Uptrend":
        heat_score += 10
    else:
        heat_score -= 5

    if oi_trend == "Rising":
        heat_score += 10
    elif oi_trend == "Falling":
        heat_score -= 5

    if funding > 0.03:
        heat_score += 5

    if overextended:
        heat_score += 5

    heat_score = max(min(heat_score, 100), 0)

    crowding = "Low"
    if funding > 0.03:
        crowding = "Medium"
    if funding > 0.05:
        crowding = "High"

    squeeze_risk = "Low"
    if funding > 0.03 and oi_trend == "Rising":
        squeeze_risk = "Medium"
    if funding > 0.05 and oi_trend == "Rising":
        squeeze_risk = "High"

    phase = "Pullback"
    if overextended:
        phase = "Late Expansion"
    if trend == "Downtrend":
        phase = "Bearish Structure"

    return {
        "heat_score": heat_score,
        "crowding": crowding,
        "squeeze_risk": squeeze_risk,
        "phase": phase
    }
