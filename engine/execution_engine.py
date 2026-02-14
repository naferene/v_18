def generate_execution_plan(data):
    price = data["price"]
    hl = data["hl"]
    hh = data["hh"]

    entry_low = hl * 1.002
    entry_high = hl * 1.004
    sl = hl * 0.996
    tp1 = hh

    return {
        "entry_low": entry_low,
        "entry_high": entry_high,
        "sl": sl,
        "tp1": tp1
    }
