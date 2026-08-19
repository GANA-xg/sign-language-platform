import os
import cv2
import joblib
import numpy as np
import mediapipe as mp

from dynamic.reference_matcher import ReferenceMatcher


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

STATIC_MODEL_PATH = os.path.join(
    BASE_DIR,
    "..",
    "models",
    "xgboost_landmark.pkl"
)

STATIC_ENCODER_PATH = os.path.join(
    BASE_DIR,
    "..",
    "models",
    "label_encoder.pkl"
)


# ============================================================
# SETTINGS
# ============================================================

TARGET_FRAMES = 30

# Capture more frames from webcam.
# They will later be resized to 30 frames.
CAPTURE_FRAMES = 45

MOVEMENT_THRESHOLD = 0.003


# ============================================================
# LOAD STATIC MODEL
# ============================================================

print()
print("========================================")
print("LOADING STATIC A-Z MODEL")
print("========================================")

static_model = joblib.load(
    STATIC_MODEL_PATH
)

static_encoder = joblib.load(
    STATIC_ENCODER_PATH
)

print("Static model loaded successfully.")


# ============================================================
# LOAD DYNAMIC REFERENCES
# ============================================================

print()
print("========================================")
print("LOADING DYNAMIC REFERENCES")
print("========================================")

matcher = ReferenceMatcher()

print("Dynamic reference matcher loaded successfully.")


# ============================================================
# MEDIAPIPE
# ============================================================

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)


# ============================================================
# CAMERA
# ============================================================

cap = cv2.VideoCapture(0)

if not cap.isOpened():

    print("ERROR: Webcam could not be opened.")

    raise SystemExit


# ============================================================
# VARIABLES
# ============================================================

mode = "STATIC"

recording = False

sequence = []

previous_wrist = None

prediction = "Waiting..."

confidence = 0.0

distance = 0.0

cooldown = 0


# ============================================================
# RESIZE SEQUENCE
# ============================================================

def resize_sequence(sequence):

    sequence = np.asarray(
        sequence,
        dtype=np.float32
    )

    if len(sequence) == 0:

        return None

    if len(sequence) == TARGET_FRAMES:

        return sequence

    old_positions = np.linspace(
        0,
        1,
        len(sequence)
    )

    new_positions = np.linspace(
        0,
        1,
        TARGET_FRAMES
    )

    resized = np.zeros(
        (
            TARGET_FRAMES,
            63
        ),
        dtype=np.float32
    )

    for feature_index in range(63):

        resized[:, feature_index] = np.interp(
            new_positions,
            old_positions,
            sequence[:, feature_index]
        )

    return resized


# ============================================================
# RESET
# ============================================================

def reset_dynamic():

    global recording
    global sequence
    global previous_wrist
    global prediction
    global confidence
    global distance
    global cooldown

    recording = False

    sequence = []

    previous_wrist = None

    prediction = "Waiting..."

    confidence = 0.0

    distance = 0.0

    cooldown = 0


# ============================================================
# PREDICT DYNAMIC WORD
# ============================================================

def predict_dynamic_word(sequence):

    global prediction
    global confidence
    global distance

    print()
    print("========================================")
    print("DYNAMIC PREDICTION")
    print("========================================")

    print(
        "Captured frames:",
        len(sequence)
    )

    processed_sequence = resize_sequence(
        sequence
    )

    if processed_sequence is None:

        prediction = "Try Again"

        return

    print(
        "Processed shape:",
        processed_sequence.shape
    )

    try:

        result = matcher.match(
            processed_sequence
        )

        prediction = result["word"]

        confidence = float(
            result["confidence"]
        )

        distance = float(
            result["distance"]
        )

        print()
        print("========================================")
        print("FINAL DYNAMIC RESULT")
        print("========================================")

        print(
            "Word       :",
            prediction
        )

        print(
            f"Confidence : {confidence:.2f}%"
        )

        print(
            f"Distance   : {distance:.4f}"
        )

        print("========================================")

    except Exception as e:

        print()
        print("DYNAMIC MATCHING ERROR")
        print(e)

        prediction = "Error"

        confidence = 0.0

        distance = 0.0


# ============================================================
# START MESSAGE
# ============================================================

print()
print("========================================")
print("SIGN LANGUAGE WEBCAM")
print("========================================")

print()
print("STATIC MODE")
print("A-Z letters")

print()
print("CONTROLS")
print("----------------------------------------")
print("D = Dynamic Word Mode")
print("S = Static A-Z Mode")
print("R = Reset")
print("Q = Exit")

print()
print("Dynamic words:")
print("HELLO / THANKYOU / SORRY / YES / NO")

print()
print("IMPORTANT:")
print("Dynamic mode uses the ORIGINAL camera orientation")
print("to match the reference videos.")
print("========================================")


# ============================================================
# MAIN LOOP
# ============================================================

while True:

    success, original_frame = cap.read()

    if not success:

        print("Camera frame failed.")

        break


    # ========================================================
    # IMPORTANT
    #
    # DO NOT FLIP THE FRAME BEFORE MEDIAPIPE.
    #
    # Reference videos were processed in original orientation.
    # ========================================================

    rgb = cv2.cvtColor(
        original_frame,
        cv2.COLOR_BGR2RGB
    )

    results = hands.process(
        rgb
    )


    # ========================================================
    # DISPLAY FRAME
    #
    # We can mirror ONLY the display.
    # MediaPipe still uses original_frame.
    # ========================================================

    frame = cv2.flip(
        original_frame,
        1
    )


    # ========================================================
    # HAND DETECTED
    # ========================================================

    if results.multi_hand_landmarks:

        hand = results.multi_hand_landmarks[0]


        # Draw landmarks on display frame.
        #
        # Since display is mirrored, mirror landmark
        # x-coordinate for drawing only.
        #
        # Prediction itself still uses original landmarks.

        display_landmarks = []

        for lm in hand.landmark:

            display_landmarks.append(
                (
                    int((1.0 - lm.x) * frame.shape[1]),
                    int(lm.y * frame.shape[0])
                )
            )


        # Draw manually
        for connection in mp_hands.HAND_CONNECTIONS:

            start = connection[0]

            end = connection[1]

            cv2.line(
                frame,
                display_landmarks[start],
                display_landmarks[end],
                (0, 255, 0),
                2
            )


        for point in display_landmarks:

            cv2.circle(
                frame,
                point,
                4,
                (0, 255, 0),
                -1
            )


        # ====================================================
        # 63 FEATURES
        # ====================================================

        features = []

        for lm in hand.landmark:

            features.extend([
                lm.x,
                lm.y,
                lm.z
            ])

        features = np.asarray(
            features,
            dtype=np.float32
        )


        # ====================================================
        # STATIC MODE
        # ====================================================

        if mode == "STATIC":

            try:

                pred = static_model.predict(
                    [features]
                )

                letter = static_encoder.inverse_transform(
                    pred
                )[0]

            except Exception:

                letter = "Unknown"


            cv2.putText(
                frame,
                f"LETTER: {letter}",
                (20, 45),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 255, 0),
                3
            )

            cv2.putText(
                frame,
                "STATIC A-Z MODE",
                (20, 85),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 0),
                2
            )


        # ====================================================
        # DYNAMIC MODE
        # ====================================================

        else:

            wrist = hand.landmark[0]

            current_wrist = (
                wrist.x,
                wrist.y
            )


            # ------------------------------------------------
            # Calculate movement
            # ------------------------------------------------

            if previous_wrist is None:

                movement = 0.0

            else:

                dx = (
                    current_wrist[0]
                    -
                    previous_wrist[0]
                )

                dy = (
                    current_wrist[1]
                    -
                    previous_wrist[1]
                )

                movement = np.sqrt(
                    dx * dx +
                    dy * dy
                )


            previous_wrist = current_wrist


            # =================================================
            # COOLDOWN
            # =================================================

            if cooldown > 0:

                cooldown -= 1

                cv2.putText(
                    frame,
                    "RESULT READY",
                    (20, 45),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2
                )


            # =================================================
            # WAITING FOR MOVEMENT
            # =================================================

            elif not recording:

                cv2.putText(
                    frame,
                    "DYNAMIC MODE",
                    (20, 45),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    (255, 0, 255),
                    2
                )

                cv2.putText(
                    frame,
                    "Move your hand",
                    (20, 85),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 255),
                    2
                )


                # --------------------------------------------
                # Start recording
                # --------------------------------------------

                if movement > MOVEMENT_THRESHOLD:

                    recording = True

                    sequence = []

                    # Include current frame
                    sequence.append(
                        features.copy()
                    )

                    print()
                    print("========================================")
                    print("MOVEMENT DETECTED")
                    print("========================================")
                    print(
                        f"Recording {CAPTURE_FRAMES} frames..."
                    )


            # =================================================
            # RECORDING
            # =================================================

            else:

                sequence.append(
                    features.copy()
                )


                cv2.putText(
                    frame,
                    "RECORDING...",
                    (20, 45),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    (0, 0, 255),
                    3
                )

                cv2.putText(
                    frame,
                    f"Frames: {len(sequence)}/{CAPTURE_FRAMES}",
                    (20, 85),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 255),
                    2
                )


                # --------------------------------------------
                # Capture enough frames
                # --------------------------------------------

                if len(sequence) >= CAPTURE_FRAMES:

                    print()
                    print(
                        f"{CAPTURE_FRAMES} FRAMES COLLECTED"
                    )

                    captured = sequence.copy()

                    recording = False

                    sequence = []

                    previous_wrist = None


                    # ----------------------------------------
                    # Predict
                    # ----------------------------------------

                    predict_dynamic_word(
                        captured
                    )


                    # ----------------------------------------
                    # Cooldown
                    # ----------------------------------------

                    cooldown = 25


    # ========================================================
    # NO HAND
    # ========================================================

    else:

        cv2.putText(
            frame,
            "HAND NOT DETECTED",
            (20, 45),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2
        )


    # ========================================================
    # SHOW RESULT
    # ========================================================

    if mode == "DYNAMIC":

        cv2.putText(
            frame,
            f"WORD: {prediction}",
            (20, 140),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 255, 0),
            3
        )

        if confidence > 0:

            cv2.putText(
                frame,
                f"Confidence: {confidence:.2f}%",
                (20, 180),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2
            )


    # ========================================================
    # CONTROLS
    # ========================================================

    cv2.putText(
        frame,
        "D: Dynamic | S: Static | R: Reset | Q: Exit",
        (20, frame.shape[0] - 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        2
    )


    # ========================================================
    # DISPLAY
    # ========================================================

    cv2.imshow(
        "SIGN LANGUAGE WEBCAM",
        frame
    )


    # ========================================================
    # KEYBOARD
    # ========================================================

    key = cv2.waitKey(1) & 0xFF


    if key == ord("d"):

        mode = "DYNAMIC"

        reset_dynamic()

        print()
        print("========================================")
        print("DYNAMIC MODE ENABLED")
        print("========================================")
        print("Move your hand.")
        print(
            f"{CAPTURE_FRAMES} frames will be captured."
        )
        print("========================================")


    elif key == ord("s"):

        mode = "STATIC"

        reset_dynamic()

        print()
        print("STATIC A-Z MODE ENABLED")


    elif key == ord("r"):

        reset_dynamic()

        print()
        print("DYNAMIC RESET")


    elif key == ord("q"):

        break


# ============================================================
# CLEANUP
# ============================================================

cap.release()

hands.close()

cv2.destroyAllWindows()

print()
print("Webcam closed.")