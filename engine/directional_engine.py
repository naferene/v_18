def calculate_directional_score(data):
    score = 0
    breakdown = {}

    trend = data["trend"]
    price = data["price"]
    hl = data["hl"]
    hh = data["hh"]
    break_confirmed = data["break_confirmed"]
    funding = data["funding"]
    oi_trend = data["oi_trend"]
    ls_ratio = data["ls_ratio"]
    rsi = data["rsi"]
    high_24 = data["high_24"]
    low_24 = data["low_24"]
    micro = data["micro"]

    swing = abs(hh - hl)
    range_24 = high_24 - low_24

    # ================= STRUCTURE (20)
    structure = 0
    if trend == "Uptrend":
        structure += 10
        if price > hl:
            structure += 5
    if break_confirmed:
        structure += 5
    breakdown["Structure"] = structure
    score += structure

    # ================= SUPPLY-DEMAND (20)
    sd = 0
    if swing > 0:
        proximity = abs(price - hl) / swing
        if proximity < 0.25:
            sd += 10
        elif proximity < 0.75:
            sd += 5

    if range_24 > 0:
        range_pos = (price - low_24) / range_24
        if range_pos < 0.85:
            sd += 5
        else:
            sd -= 5
    breakdown["SupplyDemand"] = sd
    score += sd

    # ================= POSITIONING (20)
    positioning = 0
    if oi_trend == "Rising":
        positioning += 7
    if funding < 0.05:
        positioning += 5
    else:
        positioning -= 5
    if ls_ratio and ls_ratio < 1:
        positioning += 3
    breakdown["Positioning"] = positioning
    score += positioning

    # ================= RSI / VOLATILITY (15)
    vol = 0
    if 40 <= rsi <= 65:
        vol += 5
    if rsi < 75:
        vol += 5
    breakdown["Volatility"] = vol
    score += vol

    # ================= MICRO (15)
    micro_score = 0
    if micro == "Strong":
        micro_score = 10
    elif micro == "Weak":
        micro_score = 5
    breakdown["Micro"] = micro_score
    score += micro_score

    score = max(min(score, 100), 0)

    return score, breakdown
