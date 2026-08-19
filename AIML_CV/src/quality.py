def analyze_hand_quality(hand_landmarks):
    """
    Analyze the detected hand position and approximate distance.

    This module provides immediate hand-guidance suggestions
    for the user.

    It does NOT perform gesture prediction.
    Gesture prediction is handled by the XGBoost model.
    """

    # ==================================================
    # Get landmark coordinates
    # ==================================================

    xs = [lm.x for lm in hand_landmarks.landmark]
    ys = [lm.y for lm in hand_landmarks.landmark]

    # ==================================================
    # Calculate approximate hand center
    # ==================================================

    avg_x = sum(xs) / len(xs)
    avg_y = sum(ys) / len(ys)

    # ==================================================
    # Calculate approximate hand width
    #
    # Small width  -> hand is far
    # Large width  -> hand is close
    # ==================================================

    width = max(xs) - min(xs)

    # ==================================================
    # Check horizontal hand position
    # ==================================================

    if avg_x < 0.35:

        position = "Left"

    elif avg_x > 0.65:

        position = "Right"

    else:

        position = "Center"

    # ==================================================
    # Check vertical hand position
    # ==================================================

    if avg_y < 0.25:

        vertical_position = "Top"

    elif avg_y > 0.75:

        vertical_position = "Bottom"

    else:

        vertical_position = "Center"

    # ==================================================
    # Check approximate hand distance
    # ==================================================

    if width < 0.18:

        distance = "Too Far"

    elif width > 0.45:

        distance = "Too Close"

    else:

        distance = "Good Distance"

    # ==================================================
    # Generate hand-guidance recommendation
    # ==================================================

    # ----------------------------------------------
    # Case 1: Hand is too far
    # ----------------------------------------------

    if distance == "Too Far":

        quality = "Needs Improvement"

        suggestion = (
            "Move your hand closer to the camera."
        )

    # ----------------------------------------------
    # Case 2: Hand is too close
    # ----------------------------------------------

    elif distance == "Too Close":

        quality = "Needs Improvement"

        suggestion = (
            "Move your hand slightly away from the camera."
        )

    # ----------------------------------------------
    # Case 3: Hand is on the left
    # ----------------------------------------------

    elif position == "Left":

        quality = "Good"

        suggestion = (
            "Move your hand slightly to the center."
        )

    # ----------------------------------------------
    # Case 4: Hand is on the right
    # ----------------------------------------------

    elif position == "Right":

        quality = "Good"

        suggestion = (
            "Move your hand slightly to the center."
        )

    # ----------------------------------------------
    # Case 5: Hand is at the top
    # ----------------------------------------------

    elif vertical_position == "Top":

        quality = "Good"

        suggestion = (
            "Move your hand slightly downward "
            "towards the center."
        )

    # ----------------------------------------------
    # Case 6: Hand is at the bottom
    # ----------------------------------------------

    elif vertical_position == "Bottom":

        quality = "Good"

        suggestion = (
            "Move your hand slightly upward "
            "towards the center."
        )

    # ----------------------------------------------
    # Case 7: Hand is in a good position
    # ----------------------------------------------

    else:

        quality = "Excellent"

        suggestion = (
            "Good hand position. Keep the gesture steady."
        )

    # ==================================================
    # Return quality information
    # ==================================================

    return {
        "hand_position": position,
        "vertical_position": vertical_position,
        "hand_distance": distance,
        "gesture_quality": quality,
        "suggestion": suggestion
    }