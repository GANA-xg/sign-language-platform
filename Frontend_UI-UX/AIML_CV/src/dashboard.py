from .history import get_history
from .analytics import get_analytics

def get_dashboard():

    history = get_history()
    analytics = get_analytics()

    recent_predictions = history[-5:] if len(history) >= 5 else history

    return {
        "analytics": analytics,
        "recent_predictions": recent_predictions
    }