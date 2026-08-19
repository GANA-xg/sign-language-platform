import os
import joblib
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
)

# =====================================
# Paths
# =====================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))

CSV_PATH = os.path.join(PROJECT_DIR, "processed", "gesture_landmarks.csv")

MODEL_PATH = os.path.join(PROJECT_DIR, "models", "xgboost_landmark.pkl")

ENCODER_PATH = os.path.join(PROJECT_DIR, "models", "label_encoder.pkl")

OUTPUT_DIR = os.path.join(PROJECT_DIR, "evaluation")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# =====================================
# Load Dataset
# =====================================

print("Loading Dataset...")

df = pd.read_csv(CSV_PATH)

print("Dataset Loaded Successfully")

# Features

X = df.iloc[:, :-1]

# Labels

y = df.iloc[:, -1]

print("Total Samples :", len(df))
print("Total Classes :", len(y.unique()))

# =====================================
# Train Test Split
# =====================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y,
)

print("Testing Samples :", len(X_test))

# =====================================
# Load Model
# =====================================

print("\nLoading Model...")

model = joblib.load(MODEL_PATH)

label_encoder = joblib.load(ENCODER_PATH)

print("Model Loaded Successfully")

# =====================================
# Predict
# =====================================

print("\nPredicting...")

y_pred = model.predict(X_test)

# Convert numeric labels back to original labels

y_pred = label_encoder.inverse_transform(y_pred.astype(int))

# =====================================
# Accuracy
# =====================================

accuracy = accuracy_score(y_test, y_pred)

print(f"\nAccuracy : {accuracy*100:.2f}%")

with open(os.path.join(OUTPUT_DIR, "accuracy.txt"), "w") as f:
    f.write(f"Accuracy : {accuracy*100:.2f}%\n")

# =====================================
# Classification Report
# =====================================

report = classification_report(y_test, y_pred)

print("\nClassification Report\n")

print(report)

with open(
    os.path.join(OUTPUT_DIR, "classification_report.txt"),
    "w",
) as f:
    f.write(report)

# =====================================
# Confusion Matrix
# =====================================

print("\nGenerating Confusion Matrix...")

cm = confusion_matrix(
    y_test,
    y_pred,
    labels=label_encoder.classes_,
)

fig, ax = plt.subplots(figsize=(18, 18))

disp = ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=label_encoder.classes_,
)

disp.plot(
    cmap="Blues",
    xticks_rotation=90,
    ax=ax,
    colorbar=False,
)

plt.title("Sign Language Confusion Matrix")

plt.tight_layout()

plt.savefig(
    os.path.join(
        OUTPUT_DIR,
        "confusion_matrix.png",
    ),
    dpi=300,
)

plt.close()

print("Confusion Matrix Saved")

# =====================================
# Misclassified Samples
# =====================================

misclassified = pd.DataFrame(
    {
        "Actual": y_test.values,
        "Predicted": y_pred,
    }
)

misclassified = misclassified[
    misclassified["Actual"] != misclassified["Predicted"]
]

misclassified.to_csv(
    os.path.join(
        OUTPUT_DIR,
        "misclassified_samples.csv",
    ),
    index=False,
)

print("Misclassified Samples Saved")

# =====================================
# Summary
# =====================================

print("\n===================================")
print("Evaluation Completed Successfully")
print("===================================")

print(f"Accuracy : {accuracy*100:.2f}%")

print("\nFiles Generated:")

print("evaluation/accuracy.txt")

print("evaluation/classification_report.txt")

print("evaluation/confusion_matrix.png")

print("evaluation/misclassified_samples.csv")