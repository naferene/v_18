def calculate_risk(equity, entry, sl, tp, leverage=5, risk_percent=1):
    risk_amount = equity * (risk_percent / 100)
    risk_per_unit = abs(entry - sl)

    if risk_per_unit == 0:
        return None

    position_size = risk_amount / risk_per_unit
    notional = position_size * entry
    margin = notional / leverage
    reward = abs(tp - entry) * position_size
    rr = reward / risk_amount

    return {
        "risk_amount": risk_amount,
        "position_size": position_size,
        "notional": notional,
        "margin": margin,
        "rr": rr
    }
