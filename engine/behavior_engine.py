def classify_rsi(rsi):
    if rsi >= 75:
        return "Overbought"
    elif rsi <= 25:
        return "Oversold"
    elif rsi >= 65:
        return "High"
    elif rsi <= 35:
        return "Low"
    else:
        return "Normal"

def calculate_behavior(trend, funding, oi_trend, rsi):

    heat = 50

    if trend == "Uptrend":
        heat += 10
    else:
        heat -= 5

    if oi_trend == "Rising":
        heat += 10
    elif oi_trend == "Falling":
        heat -= 5

    if funding > 0.03:
        heat += 5

    if rsi >= 70 or rsi <= 30:
        heat += 5

    heat = max(min(heat, 100), 0)

    if heat < 40:
        phase = "Compression"
    elif heat < 70:
        phase = "Pullback"
    else:
        phase = "Expansion"

    crowding = "Low"
    if funding > 0.03:
        crowding = "Medium"
    if funding > 0.05:
        crowding = "High"

    squeeze = "Low"
    if funding > 0.03 and oi_trend == "Rising":
        squeeze = "Medium"
    if funding > 0.05 and oi_trend == "Rising":
        squeeze = "High"

    return {
        "heat": heat,
        "phase": phase,
        "crowding": crowding,
        "squeeze": squeeze,
        "rsi_status": classify_rsi(rsi)
    }
