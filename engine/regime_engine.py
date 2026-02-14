def detect_regime(volume_24h, change_24h, oi_trend, funding):
    if change_24h > 15 and volume_24h > 50_000_000 and oi_trend == "Rising":
        return "High Participation Expansion"
    if change_24h > 15 and oi_trend == "Rising":
        return "Leverage Driven Expansion"
    if abs(change_24h) < 5:
        return "Compression / Range"
    if funding > 0.05:
        return "Crowded Positioning Risk"
    return "Normal Trend Environment"
