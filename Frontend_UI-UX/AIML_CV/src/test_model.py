import os
import joblib
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

# ==========================================
# Paths
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CSV_PATH = os.path.join(
    BASE_DIR,
    "..",
    "processed",
    "gesture_landmarks.csv"
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "..",
    "models",
    "xgboost_landmark.pkl"
)

ENCODER_PATH = os.path.join(
    BASE_DIR,
    "..",
    "models",
    "label_encoder.pkl"
)

# ==========================================
# Load Dataset
# ==========================================

df = pd.read_csv(CSV_PATH)

X = df.drop("label", axis=1)
y = df["label"]

# ==========================================
# Load Model
# ==========================================

model = joblib.load(MODEL_PATH)
encoder = joblib.load(ENCODER_PATH)

y_encoded = encoder.transform(y)

# ==========================================
# Predict
# ==========================================

pred = model.predict(X)

accuracy = accuracy_score(y_encoded, pred)

print("=" * 50)
print(f"Model Accuracy : {accuracy * 100:.2f}%")
print("=" * 50)

# ==========================================
# Show Sample Predictions
# ==========================================

pred_labels = encoder.inverse_transform(pred)

print("\nSample Predictions:\n")

for i in range(10):
    print(
        f"Sample {i+1}: "
        f"Actual = {y.iloc[i]} | "
        f"Predicted = {pred_labels[i]}"
    )

# ==========================================
# Classification Report
# ==========================================

print("\nClassification Report\n")
print(classification_report(y_encoded, pred))

# ==========================================
# Confusion Matrix
# ==========================================

print("\nConfusion Matrix\n")
print(confusion_matrix(y_encoded, pred))