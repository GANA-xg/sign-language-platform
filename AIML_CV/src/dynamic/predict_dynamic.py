import os
import sys
import cv2
import numpy as np
import mediapipe as mp
import tensorflow as tf


# ============================================================
# Paths
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "dynamic_word_model.keras"
)

LABEL_ENCODER_PATH = os.path.join(
    BASE_DIR,
    "models",
    "dynamic_label_encoder.npy"
)


# ============================================================
# Configuration
# ============================================================

MAX_FRAMES = 30
FEATURES = 63


# ============================================================
# Load Model
# ============================================================

print("Loading dynamic word model...")

model = tf.keras.models.load_model(
    MODEL_PATH
)

labels = np.load(
    LABEL_ENCODER_PATH,
    allow_pickle=True
)

print("Dynamic model loaded successfully.")

print("Classes:")

for index, label in enumerate(labels):
    print(f"{index} -> {label}")


# ============================================================
# MediaPipe
# ============================================================

mp_hands = mp.solutions.hands

hands = mp_hands.Hands(
    static_image_mode=True,
    max_num_hands=1,
    min_detection_confidence=0.5
)


# ============================================================
# Extract landmarks from one frame
# ============================================================

def extract_landmarks(frame):

    rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    results = hands.process(rgb)

    if not results.multi_hand_landmarks:
        return None

    hand = results.multi_hand_landmarks[0]

    features = []

    for landmark in hand.landmark:

        features.extend([
            landmark.x,
            landmark.y,
            landmark.z
        ])

    return features


# ============================================================
# Extract sequence from video
# ============================================================

def extract_video_sequence(video_path):

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():

        print(
            f"ERROR: Could not open video: {video_path}"
        )

        return None

    total_frames = int(
        cap.get(cv2.CAP_PROP_FRAME_COUNT)
    )

    if total_frames <= 0:

        cap.release()

        print(
            "ERROR: Video contains no frames."
        )

        return None

    # Same frame-selection strategy used during training
    frame_indices = np.linspace(
        0,
        total_frames - 1,
        MAX_FRAMES
    ).astype(int)

    sequence = []

    for frame_index in frame_indices:

        cap.set(
            cv2.CAP_PROP_POS_FRAMES,
            int(frame_index)
        )

        success, frame = cap.read()

        if not success:
            continue

        features = extract_landmarks(
            frame
        )

        if features is not None:

            sequence.append(
                features
            )

    cap.release()

    if len(sequence) == 0:

        print(
            "ERROR: No hand landmarks detected."
        )

        return None

    sequence = np.array(
        sequence,
        dtype=np.float32
    )

    # ========================================================
    # Same padding logic used during training
    # ========================================================

    if len(sequence) < MAX_FRAMES:

        last_frame = sequence[-1]

        padding_count = (
            MAX_FRAMES - len(sequence)
        )

        padding = np.repeat(
            last_frame[np.newaxis, :],
            padding_count,
            axis=0
        )

        sequence = np.vstack([
            sequence,
            padding
        ])

    elif len(sequence) > MAX_FRAMES:

        sequence = sequence[
            :MAX_FRAMES
        ]

    # Final safety check
    if sequence.shape != (
        MAX_FRAMES,
        FEATURES
    ):

        print(
            "ERROR: Invalid sequence shape:",
            sequence.shape
        )

        return None

    return sequence


# ============================================================
# Predict Dynamic Word
# ============================================================

def predict_dynamic_word(video_path):

    sequence = extract_video_sequence(
        video_path
    )

    if sequence is None:
        return None

    # Add batch dimension
    input_data = np.expand_dims(
        sequence,
        axis=0
    )

    # Shape:
    # (1, 30, 63)

    probabilities = model.predict(
        input_data,
        verbose=0
    )[0]

    predicted_index = int(
        np.argmax(probabilities)
    )

    confidence = float(
        probabilities[predicted_index]
    )

    predicted_word = str(
        labels[predicted_index]
    )

    return {
        "prediction": predicted_word,
        "confidence": round(
            confidence * 100,
            2
        ),
        "sequence_shape": list(
            sequence.shape
        )
    }


# ============================================================
# Main
# ============================================================

def main():

    if len(sys.argv) < 2:

        print(
            "\nUsage:"
        )

        print(
            "python AIML_CV\\src\\dynamic\\predict_dynamic.py <video_path>"
        )

        print(
            "\nExample:"
        )

        print(
            "python AIML_CV\\src\\dynamic\\predict_dynamic.py AIML_CV\\dataset\\asl_dynamic_words\\HELLO\\HELLO_clip1.avi"
        )

        return

    video_path = sys.argv[1]

    if not os.path.exists(video_path):

        print(
            f"\nERROR: Video not found:\n{video_path}"
        )

        return

    print("\n========================================")
    print("DYNAMIC WORD PREDICTION")
    print("========================================")

    print(
        f"Video: {video_path}"
    )

    result = predict_dynamic_word(
        video_path
    )

    if result is None:

        print(
            "\nPrediction failed."
        )

        return

    print("\n========================================")
    print("RESULT")
    print("========================================")

    print(
        f"Prediction     : {result['prediction']}"
    )

    print(
        f"Confidence     : {result['confidence']}%"
    )

    print(
        f"Sequence shape : {result['sequence_shape']}"
    )

    print("========================================")


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    main()