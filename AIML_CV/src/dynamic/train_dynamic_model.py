import os
import glob
import numpy as np
import tensorflow as tf

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint


# ============================================================
# Configuration
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

DATA_DIR = os.path.join(
    BASE_DIR,
    "processed",
    "dynamic_sequences"
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "models"
)

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "dynamic_word_model.keras"
)

LABEL_ENCODER_PATH = os.path.join(
    MODEL_DIR,
    "dynamic_label_encoder.npy"
)

WORDS = [
    "HELLO",
    "THANKYOU",
    "SORRY",
    "YES",
    "NO"
]

MAX_FRAMES = 30
FEATURES = 63

TEST_SIZE = 0.20
VALIDATION_SIZE = 0.20

RANDOM_STATE = 42


# ============================================================
# Load Dataset
# ============================================================

def load_dataset():

    X = []
    y = []

    print("\n========================================")
    print("LOADING DYNAMIC WORD DATASET")
    print("========================================")

    for word in WORDS:

        word_dir = os.path.join(
            DATA_DIR,
            word
        )

        files = glob.glob(
            os.path.join(
                word_dir,
                "*.npy"
            )
        )

        print(
            f"{word}: {len(files)} sequences"
        )

        for file_path in files:

            sequence = np.load(
                file_path
            )

            if sequence.shape != (
                MAX_FRAMES,
                FEATURES
            ):
                print(
                    f"Skipping invalid shape: "
                    f"{file_path} -> {sequence.shape}"
                )
                continue

            X.append(sequence)
            y.append(word)

    X = np.array(
        X,
        dtype=np.float32
    )

    y = np.array(y)

    print("\nDataset shape:", X.shape)
    print("Labels shape :", y.shape)

    return X, y


# ============================================================
# Encode Labels
# ============================================================

def encode_labels(y):

    encoder = LabelEncoder()

    y_encoded = encoder.fit_transform(y)

    print("\nLabel Mapping:")

    for index, label in enumerate(
        encoder.classes_
    ):
        print(
            f"{index} -> {label}"
        )

    os.makedirs(
        MODEL_DIR,
        exist_ok=True
    )

    np.save(
        LABEL_ENCODER_PATH,
        encoder.classes_
    )

    return y_encoded


# ============================================================
# Split Dataset
# ============================================================

def split_dataset(X, y):

    # First split:
    # 80% training
    # 20% temporary

    X_train, X_temp, y_train, y_temp = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=RANDOM_STATE,
        stratify=y
    )

    # Split temporary data:
    # 10% validation
    # 10% test

    X_val, X_test, y_val, y_test = train_test_split(
        X_temp,
        y_temp,
        test_size=0.50,
        random_state=RANDOM_STATE,
        stratify=y_temp
    )

    print("\nDataset Split:")

    print(
        "Training   :",
        X_train.shape,
        y_train.shape
    )

    print(
        "Validation :",
        X_val.shape,
        y_val.shape
    )

    print(
        "Testing    :",
        X_test.shape,
        y_test.shape
    )

    return (
        X_train,
        X_val,
        X_test,
        y_train,
        y_val,
        y_test
    )


# ============================================================
# Build LSTM Model
# ============================================================

def build_model():

    model = Sequential([

        LSTM(
            128,
            return_sequences=True,
            input_shape=(
                MAX_FRAMES,
                FEATURES
            )
        ),

        Dropout(0.3),

        LSTM(
            64
        ),

        Dropout(0.3),

        Dense(
            32,
            activation="relu"
        ),

        Dropout(0.2),

        Dense(
            len(WORDS),
            activation="softmax"
        )
    ])

    model.compile(
        optimizer="adam",
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )

    model.summary()

    return model


# ============================================================
# Train Model
# ============================================================

def train_model(
    model,
    X_train,
    y_train,
    X_val,
    y_val
):

    os.makedirs(
        MODEL_DIR,
        exist_ok=True
    )

    callbacks = [

        EarlyStopping(
            monitor="val_loss",
            patience=15,
            restore_best_weights=True
        ),

        ModelCheckpoint(
            MODEL_PATH,
            monitor="val_accuracy",
            save_best_only=True
        )
    ]

    print("\n========================================")
    print("TRAINING DYNAMIC WORD MODEL")
    print("========================================")

    history = model.fit(

        X_train,
        y_train,

        validation_data=(
            X_val,
            y_val
        ),

        epochs=100,

        batch_size=4,

        callbacks=callbacks,

        verbose=1
    )

    return history


# ============================================================
# Evaluate Model
# ============================================================

def evaluate_model(
    model,
    X_test,
    y_test
):

    print("\n========================================")
    print("TESTING MODEL")
    print("========================================")

    loss, accuracy = model.evaluate(
        X_test,
        y_test,
        verbose=0
    )

    print(
        f"\nTest Loss     : {loss:.4f}"
    )

    print(
        f"Test Accuracy : {accuracy * 100:.2f}%"
    )


# ============================================================
# Main
# ============================================================

def main():

    X, y = load_dataset()

    if len(X) == 0:

        print(
            "\nERROR: No valid sequences found."
        )

        return

    y_encoded = encode_labels(y)

    (
        X_train,
        X_val,
        X_test,
        y_train,
        y_val,
        y_test
    ) = split_dataset(
        X,
        y_encoded
    )

    model = build_model()

    train_model(
        model,
        X_train,
        y_train,
        X_val,
        y_val
    )

    evaluate_model(
        model,
        X_test,
        y_test
    )

    print("\n========================================")
    print("TRAINING COMPLETED")
    print("========================================")

    print(
        "Model saved to:"
    )

    print(
        MODEL_PATH
    )

    print(
        "Label encoder saved to:"
    )

    print(
        LABEL_ENCODER_PATH
    )


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    main()