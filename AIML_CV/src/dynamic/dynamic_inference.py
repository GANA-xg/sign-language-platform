import os
import cv2
import numpy as np
import mediapipe as mp

from tensorflow.keras.models import load_model


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

MODELS_DIR = os.path.join(
    BASE_DIR,
    "..",
    "..",
    "models"
)

MODEL_PATH = os.path.join(
    MODELS_DIR,
    "dynamic_word_model.keras"
)

LABEL_PATH = os.path.join(
    MODELS_DIR,
    "dynamic_label_encoder.npy"
)


# ============================================================
# SETTINGS
# ============================================================

MAX_FRAMES = 30
FEATURES_PER_FRAME = 63


# ============================================================
# LOAD MODEL
# ============================================================

print("Loading dynamic model...")

dynamic_model = load_model(
    MODEL_PATH
)

dynamic_classes = np.load(
    LABEL_PATH,
    allow_pickle=True
)

print("Dynamic model loaded successfully.")

print("Classes:")

for index, label in enumerate(dynamic_classes):
    print(f"{index} -> {label}")


# ============================================================
# MEDIAPIPE
# ============================================================

mp_hands = mp.solutions.hands


# ============================================================
# EXTRACT LANDMARK FEATURES FROM ONE FRAME
# ============================================================

def extract_frame_features(hand_landmarks):

    features = []

    for landmark in hand_landmarks.landmark:

        features.extend([
            landmark.x,
            landmark.y,
            landmark.z
        ])

    return np.asarray(
        features,
        dtype=np.float32
    )


# ============================================================
# PREDICT FROM SEQUENCE
# ============================================================

def predict_sequence(sequence):

    sequence = np.asarray(
        sequence,
        dtype=np.float32
    )

    expected_shape = (
        MAX_FRAMES,
        FEATURES_PER_FRAME
    )

    if sequence.shape != expected_shape:

        raise ValueError(
            f"Invalid sequence shape: "
            f"{sequence.shape}. "
            f"Expected {expected_shape}."
        )

    model_input = np.expand_dims(
        sequence,
        axis=0
    )

    probabilities = dynamic_model.predict(
        model_input,
        verbose=0
    )[0]

    predicted_index = int(
        np.argmax(probabilities)
    )

    prediction = str(
        dynamic_classes[predicted_index]
    )

    confidence = float(
        probabilities[predicted_index] * 100
    )

    return {
        "prediction": prediction,
        "confidence": round(confidence, 2),
        "sequence_shape": list(sequence.shape)
    }


# ============================================================
# PREDICT FROM VIDEO
# ============================================================

def predict_video(video_path):

    if not os.path.exists(video_path):

        raise FileNotFoundError(
            f"Video not found: {video_path}"
        )

    cap = cv2.VideoCapture(
        video_path
    )

    if not cap.isOpened():

        raise ValueError(
            f"Unable to open video: {video_path}"
        )

    sequence = []

    with mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    ) as hands:

        while True:

            success, frame = cap.read()

            if not success:
                break

            rgb = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            results = hands.process(
                rgb
            )

            if results.multi_hand_landmarks:

                hand = (
                    results.multi_hand_landmarks[0]
                )

                features = extract_frame_features(
                    hand
                )

                if len(features) == FEATURES_PER_FRAME:

                    sequence.append(
                        features
                    )

    cap.release()


    # --------------------------------------------------------
    # Validate extracted frames
    # --------------------------------------------------------

    if len(sequence) == 0:

        raise ValueError(
            "No hand landmarks detected in video."
        )


    # --------------------------------------------------------
    # Convert to numpy
    # --------------------------------------------------------

    sequence = np.asarray(
        sequence,
        dtype=np.float32
    )


    # --------------------------------------------------------
    # Resize sequence to 30 frames
    # --------------------------------------------------------

    if len(sequence) >= MAX_FRAMES:

        indices = np.linspace(
            0,
            len(sequence) - 1,
            MAX_FRAMES
        ).astype(int)

        sequence = sequence[
            indices
        ]

    else:

        padding = np.repeat(
            sequence[-1][np.newaxis, :],
            MAX_FRAMES - len(sequence),
            axis=0
        )

        sequence = np.vstack([
            sequence,
            padding
        ])


    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

    return predict_sequence(
        sequence
    )