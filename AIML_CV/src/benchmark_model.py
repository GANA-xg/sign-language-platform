import os
import time
import joblib
import pandas as pd

# ==========================
# Paths
# ==========================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "..",
    "models",
    "xgboost_landmark.pkl"
)

CSV_PATH = os.path.join(
    BASE_DIR,
    "..",
    "processed",
    "gesture_landmarks.csv"
)

# ==========================
# Load Model
# ==========================

model = joblib.load(MODEL_PATH)

print("Model Loaded Successfully")

# ==========================
# Load Dataset
# ==========================

df = pd.read_csv(CSV_PATH)

X = df.drop("label", axis=1)

print("Dataset Loaded Successfully")
print("Samples :", len(X))

# ==========================
# Benchmark
# ==========================

sample = X.iloc[[0]]

# Warm-up
model.predict(sample)

runs = 1000

start = time.perf_counter()

for _ in range(runs):
    model.predict(sample)

end = time.perf_counter()

total_time = end - start
avg_time = total_time / runs

print("\n========== BENCHMARK ==========")
print(f"Total Predictions : {runs}")
print(f"Total Time        : {total_time:.4f} sec")
print(f"Average Time      : {avg_time:.6f} sec")
print(f"FPS               : {1/avg_time:.2f}")