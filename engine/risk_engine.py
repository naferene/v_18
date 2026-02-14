def calculate_risk_plan(equity, risk_percent, leverage, entry, sl, tp):
    risk_amount = equity * (risk_percent / 100)
    risk_per_unit = abs(entry - sl)

    if risk_per_unit == 0:
        return None

    position_size = risk_amount / risk_per_unit
    notional = position_size * entry
    margin_required = notional / leverage
    potential_profit = abs(tp - entry) * position_size
    rr = potential_profit / risk_amount

    warnings = []

    if rr < 1.5:
        warnings.append("Low R:R (<1.5)")

    if margin_required > equity * 0.3:
        warnings.append("High exposure (>30% equity)")

    return {
        "risk_amount": risk_amount,
        "position_size": position_size,
        "notional": notional,
        "margin_required": margin_required,
        "potential_profit": potential_profit,
        "rr": rr,
        "warnings": warnings
    }
