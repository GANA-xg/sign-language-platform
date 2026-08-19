import os
import joblib
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay
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

print("Loading Dataset...")

df = pd.read_csv(CSV_PATH)

X = df.drop("label", axis=1)
y = df["label"]

# ==========================================
# Load Model
# ==========================================

print("Loading Model...")

model = joblib.load(MODEL_PATH)
encoder = joblib.load(ENCODER_PATH)

y_encoded = encoder.transform(y)

# ==========================================
# Prediction
# ==========================================

print("Evaluating Model...")

pred = model.predict(X)

accuracy = accuracy_score(y_encoded, pred)

print("=" * 60)
print(f"Model Accuracy : {accuracy * 100:.2f}%")
print("=" * 60)

# ==========================================
# Sample Predictions
# ==========================================

pred_labels = encoder.inverse_transform(pred)

print("\nSample Predictions\n")

for i in range(10):
    print(
        f"{i+1}. Actual : {y.iloc[i]} | Predicted : {pred_labels[i]}"
    )

# ==========================================
# Classification Report
# ==========================================

print("\nClassification Report\n")

print(
    classification_report(
        y_encoded,
        pred,
        target_names=encoder.classes_
    )
)

# ==========================================
# Confusion Matrix
# ==========================================

cm = confusion_matrix(y_encoded, pred)

disp = ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=encoder.classes_
)

disp.plot(
    xticks_rotation=90,
    cmap="Blues"
)

plt.title("Confusion Matrix")

plt.tight_layout()

plt.savefig("confusion_matrix.png")

print("\nConfusion Matrix saved as confusion_matrix.png")

plt.show()