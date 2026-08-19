import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
# from sklearn.metrics import accuracy_score
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    classification_report,
    ConfusionMatrixDisplay
)

import matplotlib.pyplot as plt

from xgboost import XGBClassifier

# =====================================
# Paths
# =====================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CSV_PATH = os.path.join(
    BASE_DIR,
    "..",
    "processed",
    "gesture_landmarks.csv"
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "..",
    "models"
)

os.makedirs(MODEL_DIR, exist_ok=True)

# =====================================
# Load Dataset
# =====================================

df = pd.read_csv(CSV_PATH)

print(df.head())

X = df.drop("label", axis=1)

y = df["label"]

# =====================================
# Encode Labels
# =====================================

encoder = LabelEncoder()

y = encoder.fit_transform(y)

# =====================================
# Train Test Split
# =====================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("Training Samples :", len(X_train))
print("Testing Samples  :", len(X_test))

# =====================================
# XGBoost
# =====================================

model = XGBClassifier(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,
    objective="multi:softmax",
    eval_metric="mlogloss",
    random_state=42
)

print("\nTraining XGBoost...")

model.fit(X_train, y_train)

# =====================================
# Evaluation
# =====================================

pred = model.predict(X_test)

accuracy = accuracy_score(y_test, pred)

print("\nAccuracy :", round(accuracy * 100, 2), "%")

# -------------------------------------
# Classification Report
# -------------------------------------

print("\nClassification Report\n")

report = classification_report(
    y_test,
    pred,
    target_names=encoder.classes_
)

print(report)

# -------------------------------------
# Confusion Matrix
# -------------------------------------

cm = confusion_matrix(y_test, pred)

disp = ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=encoder.classes_
)

fig, ax = plt.subplots(figsize=(12,10))

disp.plot(
    ax=ax,
    cmap="Blues",
    xticks_rotation=90
)

plt.title("Sign Language Confusion Matrix")

plt.tight_layout()

CONFUSION_MATRIX_PATH = os.path.join(
    MODEL_DIR,
    "confusion_matrix.png"
)

plt.savefig(CONFUSION_MATRIX_PATH)

plt.show()

print("\nConfusion Matrix Saved Successfully!")
print(CONFUSION_MATRIX_PATH)

# =====================================
# Save Evaluation Report
# =====================================

REPORT_PATH = os.path.join(
    MODEL_DIR,
    "evaluation_report.txt"
)

with open(REPORT_PATH, "w") as file:

    file.write("SIGN LANGUAGE MODEL EVALUATION\n")
    file.write("=" * 40 + "\n\n")

    file.write(f"Accuracy : {round(accuracy * 100, 2)}%\n\n")

    file.write(report)

print("\nEvaluation Report Saved Successfully!")
print(REPORT_PATH)

# =====================================
# Save
# =====================================

joblib.dump(
    model,
    os.path.join(MODEL_DIR, "xgboost_landmark.pkl")
)

joblib.dump(
    encoder,
    os.path.join(MODEL_DIR, "label_encoder.pkl")
)

print("\nModel Saved Successfully!")