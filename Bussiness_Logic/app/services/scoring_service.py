from typing import Optional

# Default weights out of 100, used when all four components are available.
# These are a starting point — worth revisiting once real hand_shape/
# finger_position data exists from Abhinaya's model.
DEFAULT_WEIGHTS = {
    "confidence": 30,
    "duration": 20,
    "hand_shape": 25,
    "finger_position": 25,
}

# A gesture held roughly in this range (seconds) scores full marks on duration;
# too fast or too slow tapers off. Placeholder values — tune once we have
# real practice data to look at.
IDEAL_DURATION_RANGE = (0.8, 3.0)


def score_duration(hold_seconds: float) -> float:
    """Returns 0-100. Full marks inside the ideal range, tapering off outside it."""
    low, high = IDEAL_DURATION_RANGE
    if low <= hold_seconds <= high:
        return 100.0
    if hold_seconds < low:
        # too rushed — scale down linearly from 0 to low
        return max(0.0, (hold_seconds / low) * 100)
    # held too long — taper off gradually, floor at 40
    overshoot = hold_seconds - high
    return max(40.0, 100 - overshoot * 15)


def compute_weighted_score(
    is_correct: bool,
    confidence: float,
    hold_seconds: Optional[float] = None,
    hand_shape_score: Optional[float] = None,
    finger_position_score: Optional[float] = None,
) -> dict:
    """
    Combines up to 4 components into one score out of 100.

    hand_shape_score / finger_position_score are NOT available from the AI
    service today (as of M2 Day 1 planning) — pass None until Abhinaya's
    model exposes them. When a component is missing, its weight is
    redistributed proportionally across whatever IS available, so the
    formula degrades gracefully instead of breaking or faking data.

    Returns a dict with the final score plus a breakdown, so the Feedback
    Engine (Day 3) can explain *why* a score landed where it did.
    """
    components = {"confidence": confidence * 100}
    weights = {"confidence": DEFAULT_WEIGHTS["confidence"]}

    if hold_seconds is not None:
        components["duration"] = score_duration(hold_seconds)
        weights["duration"] = DEFAULT_WEIGHTS["duration"]

    if hand_shape_score is not None:
        components["hand_shape"] = hand_shape_score
        weights["hand_shape"] = DEFAULT_WEIGHTS["hand_shape"]

    if finger_position_score is not None:
        components["finger_position"] = finger_position_score
        weights["finger_position"] = DEFAULT_WEIGHTS["finger_position"]

    total_weight = sum(weights.values())
    raw_score = sum(components[k] * weights[k] for k in components) / total_weight

    # Correctness gate, carried over from M1's Tier 1 logic: a wrong sign
    # should never score high just because confidence/duration looked good,
    # and a correct sign shouldn't score suspiciously low.
    if is_correct:
        final_score = max(raw_score, 60.0)
    else:
        final_score = min(raw_score, 30.0)

    return {
        "score": round(final_score, 2),
        "components": {k: round(v, 2) for k, v in components.items()},
        "weights_used": weights,
    }