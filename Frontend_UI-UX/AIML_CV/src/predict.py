import os
import joblib
import pandas as pd

# -----------------------
# Paths
# -----------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "..", "dataset")
MODEL_DIR = os.path.join(BASE_DIR, "..", "models")

# -----------------------
# Load Model
# -----------------------
model = joblib.load(os.path.join(MODEL_DIR, "xgboost_model.pkl"))
encoder = joblib.load(os.path.join(MODEL_DIR, "label_encoder.pkl"))

# -----------------------
# Load Test Dataset
# -----------------------
df = pd.read_csv(os.path.join(DATASET_DIR, "sign_mnist_test.csv"))

print(f"Total Test Samples : {len(df)}")

sample = int(input("Enter sample index (0-7171): "))

row = df.iloc[sample]

actual_label = row["label"]

image = row.drop("label").values.reshape(1, -1) / 255.0

prediction = model.predict(image)

predicted_label = encoder.inverse_transform(prediction)

print("\n============================")
print("Actual Label    :", actual_label)
print("Predicted Label :", predicted_label[0])
print("============================")