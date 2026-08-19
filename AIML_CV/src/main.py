import cv2
import numpy as np
from pathlib import Path
from collections import deque
from tensorflow.keras.models import load_model

from camera import Camera
from detector import HandDetector
from feature_extractor import FeatureExtractor
from predict import predict_gesture
from config import WINDOW_NAME


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

DYNAMIC_MODEL_PATH = (
    BASE_DIR / "models" / "dynamic_word_model.keras"
)

DYNAMIC_LABEL_PATH = (
    BASE_DIR / "models" / "dynamic_label_encoder.npy"
)


# ============================================================
# DYNAMIC MODEL SETTINGS
# ============================================================

MAX_FRAMES = 30
FEATURES_PER_FRAME = 63

# Your current model classes
DYNAMIC_CLASSES = np.load(
    DYNAMIC_LABEL_PATH,
    allow_pickle=True
)

DYNAMIC_MODEL = load_model(
    DYNAMIC_MODEL_PATH
)

print("Dynamic model loaded successfully.")
print("Dynamic classes:")

for index, label in enumerate(DYNAMIC_CLASSES):
    print(f"{index} -> {label}")


# ============================================================
# OBJECTS
# ============================================================

camera = Camera()
detector = HandDetector()
extractor = FeatureExtractor()


# ============================================================
# DYNAMIC FRAME BUFFER
# ============================================================

sequence_buffer = deque(
    maxlen=MAX_FRAMES
)

dynamic_prediction = "Waiting..."
dynamic_confidence = 0.0


# ============================================================
# MAIN LOOP
# ============================================================

while True:

    success, frame = camera.get_frame()

    if not success:
        break


    # --------------------------------------------------------
    # Detect hand
    # --------------------------------------------------------

    frame, landmarks = detector.detect(frame)


    if landmarks:

        # ----------------------------------------------------
        # Extract 63 features
        # ----------------------------------------------------

        features = extractor.extract_features(landmarks)

        features = np.asarray(
            features,
            dtype=np.float32
        )


        # ----------------------------------------------------
        # STATIC A-Z PREDICTION
        # ----------------------------------------------------

        result = predict_gesture(features)

        gesture = result["gesture"]
        confidence = result["confidence"]


        # ----------------------------------------------------
        # ADD FRAME TO DYNAMIC BUFFER
        # ----------------------------------------------------

        if len(features) == FEATURES_PER_FRAME:

            sequence_buffer.append(features)


        # ----------------------------------------------------
        # DYNAMIC WORD PREDICTION
        # ----------------------------------------------------

        if len(sequence_buffer) == MAX_FRAMES:

            sequence = np.array(
                sequence_buffer,
                dtype=np.float32
            )

            # Expected:
            # (30, 63)

            if sequence.shape == (
                MAX_FRAMES,
                FEATURES_PER_FRAME
            ):

                model_input = np.expand_dims(
                    sequence,
                    axis=0
                )

                predictions = DYNAMIC_MODEL.predict(
                    model_input,
                    verbose=0
                )

                predicted_index = int(
                    np.argmax(predictions[0])
                )

                dynamic_confidence = (
                    float(predictions[0][predicted_index])
                    * 100
                )

                dynamic_prediction = str(
                    DYNAMIC_CLASSES[predicted_index]
                )


        # ----------------------------------------------------
        # DISPLAY STATIC RESULT
        # ----------------------------------------------------

        cv2.putText(
            frame,
            f"Letter : {gesture}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"Letter Confidence : {confidence:.2f}%",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )


        # ----------------------------------------------------
        # DISPLAY DYNAMIC RESULT
        # ----------------------------------------------------

        cv2.putText(
            frame,
            f"Word : {dynamic_prediction}",
            (10, 95),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 0, 255),
            2
        )

        cv2.putText(
            frame,
            f"Word Confidence : {dynamic_confidence:.2f}%",
            (10, 125),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 0, 255),
            2
        )


        # ----------------------------------------------------
        # FRAME COUNT
        # ----------------------------------------------------

        cv2.putText(
            frame,
            f"Frames : {len(sequence_buffer)}/{MAX_FRAMES}",
            (10, 160),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 0),
            2
        )


        # ----------------------------------------------------
        # FEATURES
        # ----------------------------------------------------

        cv2.putText(
            frame,
            f"Features : {len(features)}",
            (10, 190),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 0),
            2
        )


        # ----------------------------------------------------
        # HAND STATUS
        # ----------------------------------------------------

        cv2.putText(
            frame,
            "Hand : Detected",
            (10, 220),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )


    else:

        # ----------------------------------------------------
        # NO HAND
        # ----------------------------------------------------

        sequence_buffer.clear()

        dynamic_prediction = "Waiting..."
        dynamic_confidence = 0.0

        cv2.putText(
            frame,
            "Hand : Not Detected",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2
        )


    # --------------------------------------------------------
    # EXIT MESSAGE
    # --------------------------------------------------------

    cv2.putText(
        frame,
        "Press Q to Exit",
        (10, frame.shape[0] - 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )


    # --------------------------------------------------------
    # SHOW FRAME
    # --------------------------------------------------------

    cv2.imshow(
        WINDOW_NAME,
        frame
    )


    # --------------------------------------------------------
    # EXIT
    # --------------------------------------------------------

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


# ============================================================
# CLEANUP
# ============================================================

camera.release()
cv2.destroyAllWindows()