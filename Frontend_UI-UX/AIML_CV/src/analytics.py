from .history import get_history

def get_analytics():
    history = get_history()

    if not history:
        return {
            "total_predictions": 0,
            "average_confidence": 0,
            "high_confidence_predictions": 0,
            "low_confidence_predictions": 0,
            "most_predicted_sign": None
        }

    total = len(history)

    avg_confidence = round(
        sum(item["confidence"] for item in history) / total, 4
    )

    high = sum(1 for item in history if item["confidence_level"] == "High")
    low = total - high

    counts = {}
    for item in history:
        sign = item["prediction"]
        counts[sign] = counts.get(sign, 0) + 1

    most_predicted = max(counts, key=counts.get)

    return {
        "total_predictions": total,
        "average_confidence": avg_confidence,
        "high_confidence_predictions": high,
        "low_confidence_predictions": low,
        "most_predicted_sign": most_predicted
    }