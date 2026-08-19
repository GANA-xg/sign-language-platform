import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score

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