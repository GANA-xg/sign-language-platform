import pandas as pd
import os
from sklearn.model_selection import train_test_split

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "..", "dataset")

train_path = os.path.join(DATASET_DIR, "sign_mnist_train.csv")

df = pd.read_csv(train_path)

X = df.drop("label", axis=1)
y = df["label"]

# Normalize pixel values
X = X / 255.0

print("Features Shape :", X.shape)
print("Labels Shape   :", y.shape)

X_train, X_val, y_train, y_val = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("\nTrain :", X_train.shape)
print("Validation :", X_val.shape)