import os
import cv2
import time
import pandas as pd

from camera import Camera
from detector import HandDetector
from feature_extractor import FeatureExtractor

# ===========================
# Paths
# ===========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "..", "dataset")
CSV_PATH = os.path.join(DATASET_DIR, "gesture_dataset.csv")

os.makedirs(DATASET_DIR, exist_ok=True)

columns = [f"f{i+1}" for i in range(63)]
columns.append("label")

if not os.path.exists(CSV_PATH) or os.path.getsize(CSV_PATH) == 0:
    pd.DataFrame(columns=columns).to_csv(CSV_PATH, index=False)

# ===========================
# Modules
# ===========================
camera = Camera()
detector = HandDetector()
extractor = FeatureExtractor()

label = input("Enter Gesture Label (A/B/C/L/Y): ").strip().upper()

TARGET_SAMPLES = 100
sample_count = 0

last_saved_time = time.time()

print(f"\nCollecting {TARGET_SAMPLES} samples for '{label}'...\n")

while sample_count < TARGET_SAMPLES:

    success, frame = camera.get_frame()

    if not success:
        break

    frame, landmarks = detector.detect(frame)

    if landmarks is not None:

        features = extractor.extract_features(landmarks)

        current_time = time.time()

        # Save every 1 second
        if current_time - last_saved_time >= 1:

            row = features + [label]

            pd.DataFrame([row], columns=columns).to_csv(
                CSV_PATH,
                mode="a",
                header=False,
                index=False
            )

            sample_count += 1
            last_saved_time = current_time

            print(f"✅ Sample {sample_count}/{TARGET_SAMPLES} Saved")

        cv2.putText(
            frame,
            f"Gesture : {label}",
            (10,30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0,255,0),
            2
        )

        cv2.putText(
            frame,
            f"Samples : {sample_count}/{TARGET_SAMPLES}",
            (10,65),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255,255,0),
            2
        )

    else:

        cv2.putText(
            frame,
            "No Hand Detected",
            (10,30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0,0,255),
            2
        )

    cv2.imshow("Dataset Creator", frame)

    # ESC key to exit
    if cv2.waitKey(1) == 27:
        break

camera.release()
cv2.destroyAllWindows()

print("\n====================================")
print("Dataset Collection Completed")
print(f"Total Samples Collected : {sample_count}")
print(f"Saved to : {CSV_PATH}")
print("====================================")