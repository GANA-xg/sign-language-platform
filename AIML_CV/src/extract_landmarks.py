import os
import cv2
import mediapipe as mp
import pandas as pd

# ==================================================
# Paths
# ==================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATASET_DIR = os.path.join(
    BASE_DIR,
    "..",
    "dataset",
    "asl_alphabet_train"
)

OUTPUT_DIR = os.path.join(BASE_DIR, "..", "processed")
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "gesture_landmarks.csv")

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("Dataset Path :", DATASET_DIR)
print("Path Exists  :", os.path.exists(DATASET_DIR))

# ==================================================
# MediaPipe
# ==================================================

mp_hands = mp.solutions.hands

hands = mp_hands.Hands(
    static_image_mode=True,
    max_num_hands=1,
    min_detection_confidence=0.5
)

# ==================================================
# CSV Columns
# ==================================================

columns = []

for i in range(21):
    columns.append(f"x{i}")
    columns.append(f"y{i}")
    columns.append(f"z{i}")

columns.append("label")

dataset = []

total_images = 0
detected_images = 0

# ==================================================
# Read Labels
# ==================================================

labels = sorted(os.listdir(DATASET_DIR))

print("\nLabels Found:")
print(labels)

for label in labels:

    label_path = os.path.join(DATASET_DIR, label)

    if not os.path.isdir(label_path):
        continue

    print(f"\nProcessing {label}...")

    images = sorted(os.listdir(label_path))

    # Process first 100 images only
    for image_name in images:

        image_path = os.path.join(label_path, image_name)

        image = cv2.imread(image_path)

        if image is None:
            continue

        total_images += 1

        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        results = hands.process(rgb)

        if results.multi_hand_landmarks:

            landmarks = results.multi_hand_landmarks[0]

            features = []

            for point in landmarks.landmark:
                features.extend([
                    point.x,
                    point.y,
                    point.z
                ])

            features.append(label)

            dataset.append(features)

            detected_images += 1

# ==================================================
# Save CSV
# ==================================================

print("\nSaving CSV...")

df = pd.DataFrame(dataset, columns=columns)

df.to_csv(OUTPUT_CSV, index=False)

print("\n====================================")
print("Landmark Extraction Completed")
print("====================================")
print("Total Images      :", total_images)
print("Hands Detected    :", detected_images)
print("CSV Saved         :", OUTPUT_CSV)
print("====================================")