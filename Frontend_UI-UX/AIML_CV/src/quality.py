def analyze_hand_quality(hand_landmarks):

    xs = [lm.x for lm in hand_landmarks.landmark]
    ys = [lm.y for lm in hand_landmarks.landmark]

    avg_x = sum(xs) / len(xs)
    avg_y = sum(ys) / len(ys)

    width = max(xs) - min(xs)

    # Hand Position
    if avg_x < 0.35:
        position = "Left"
    elif avg_x > 0.65:
        position = "Right"
    else:
        position = "Center"

    # Distance
    if width < 0.18:
        distance = "Too Far"
    elif width > 0.45:
        distance = "Too Close"
    else:
        distance = "Good Distance"

    # Quality
    if position == "Center" and distance == "Good Distance":
        quality = "Excellent"
        suggestion = "Gesture looks perfect."
    elif distance == "Too Far":
        quality = "Needs Improvement"
        suggestion = "Move your hand closer to the camera."
    elif distance == "Too Close":
        quality = "Needs Improvement"
        suggestion = "Move your hand slightly away from the camera."
    else:
        quality = "Good"
        suggestion = "Move your hand to the center."

    return {
        "hand_position": position,
        "hand_distance": distance,
        "gesture_quality": quality,
        "suggestion": suggestion
    }