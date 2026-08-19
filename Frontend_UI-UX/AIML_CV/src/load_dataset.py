import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "..", "dataset")

train_path = os.path.join(DATASET_DIR, "sign_mnist_train.csv")
test_path = os.path.join(DATASET_DIR, "sign_mnist_test.csv")

train_df = pd.read_csv(train_path)
test_df = pd.read_csv(test_path)

print("="*50)
print("Dataset Loaded Successfully")
print("="*50)

print(f"Training Samples : {len(train_df)}")
print(f"Testing Samples  : {len(test_df)}")

print("\nColumns :", len(train_df.columns))
print("Features:", len(train_df.columns)-1)

print("\nUnique Labels")
print(sorted(train_df["label"].unique()))

print("\nFirst 5 Rows")
print(train_df.head())