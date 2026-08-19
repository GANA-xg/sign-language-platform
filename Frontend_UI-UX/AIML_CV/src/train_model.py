import os
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# -------------------------
# Paths
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CSV_PATH = os.path.join(BASE_DIR, "..", "dataset", "gesture_dataset.csv")

MODEL_DIR = os.path.join(BASE_DIR, "..", "models")
os.makedirs(MODEL_DIR, exist_ok=True)

MODEL_PATH = os.path.join(MODEL_DIR, "sign_model.pkl")

# -------------------------
# Load Dataset
# -------------------------
df = pd.read_csv(CSV_PATH)

print("Dataset Loaded Successfully")
print(df.head())

# -------------------------
# Features and Labels
# -------------------------
X = df.iloc[:, :-1]   # 63 Features
y = df.iloc[:, -1]    # Label

print("Features Shape:", X.shape)
print("Labels Shape:", y.shape)

# -------------------------
# Split Dataset
# -------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# -------------------------
# Train Model
# -------------------------
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)

# -------------------------
# Test Model
# -------------------------
predictions = model.predict(X_test)

accuracy = accuracy_score(y_test, predictions)

print("\nModel Accuracy:", round(accuracy * 100, 2), "%")

# -------------------------
# Save Model
# -------------------------
joblib.dump(model, MODEL_PATH)

print("\nModel Saved Successfully")
print(MODEL_PATH)