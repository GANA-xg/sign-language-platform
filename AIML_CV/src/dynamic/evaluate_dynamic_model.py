import os
import glob
import numpy as np
import tensorflow as tf

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score
)


# ============================================================
# Paths
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

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "dynamic_word_model.keras"
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
RANDOM_STATE = 42


# ============================================================
# Load Dataset
# ============================================================

def load_dataset():

    X = []
    y = []

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

        for file_path in files:

            sequence = np.load(
                file_path
            )

            if sequence.shape == (
                MAX_FRAMES,
                FEATURES
            ):

                X.append(sequence)
                y.append(word)

    return (
        np.array(X, dtype=np.float32),
        np.array(y)
    )


# ============================================================
# Main
# ============================================================

def main():

    print("\n========================================")
    print("DYNAMIC WORD MODEL EVALUATION")
    print("========================================")

    X, y = load_dataset()

    print(
        f"Total sequences: {len(X)}"
    )

    # --------------------------------------------------------
    # Encode labels
    # --------------------------------------------------------

    encoder = LabelEncoder()

    y_encoded = encoder.fit_transform(y)

    print("\nLabel mapping:")

    for index, label in enumerate(
        encoder.classes_
    ):

        print(
            f"{index} -> {label}"
        )

    # --------------------------------------------------------
    # Recreate EXACT same test split
    # --------------------------------------------------------

    X_train, X_temp, y_train, y_temp = train_test_split(
        X,
        y_encoded,
        test_size=0.20,
        random_state=RANDOM_STATE,
        stratify=y_encoded
    )

    X_val, X_test, y_val, y_test = train_test_split(
        X_temp,
        y_temp,
        test_size=0.50,
        random_state=RANDOM_STATE,
        stratify=y_temp
    )

    # --------------------------------------------------------
    # Load trained model
    # --------------------------------------------------------

    model = tf.keras.models.load_model(
        MODEL_PATH
    )

    print("\nModel loaded successfully.")

    # --------------------------------------------------------
    # Predict
    # --------------------------------------------------------

    probabilities = model.predict(
        X_test,
        verbose=0
    )

    predictions = np.argmax(
        probabilities,
        axis=1
    )

    # --------------------------------------------------------
    # Accuracy
    # --------------------------------------------------------

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    print("\n========================================")
    print("RESULT")
    print("========================================")

    print(
        f"Accuracy: {accuracy * 100:.2f}%"
    )

    # --------------------------------------------------------
    # Classification Report
    # --------------------------------------------------------

    print("\nClassification Report:\n")

    print(
        classification_report(
            y_test,
            predictions,
            labels=np.arange(len(encoder.classes_)),
            target_names=encoder.classes_,
            zero_division=0
        )
    )

    # --------------------------------------------------------
    # Confusion Matrix
    # --------------------------------------------------------

    print("Confusion Matrix:\n")

    matrix = confusion_matrix(
        y_test,
        predictions,
        labels=np.arange(len(encoder.classes_))
    )

    print(
        matrix
    )

    # --------------------------------------------------------
    # Individual Predictions
    # --------------------------------------------------------

    print("\nIndividual Test Predictions:\n")

    for i in range(
        len(X_test)
    ):

        actual = encoder.inverse_transform(
            [y_test[i]]
        )[0]

        predicted = encoder.inverse_transform(
            [predictions[i]]
        )[0]

        confidence = (
            float(
                np.max(
                    probabilities[i]
                )
            ) * 100
        )

        status = (
            "CORRECT"
            if actual == predicted
            else "WRONG"
        )

        print(
            f"{i + 1}. "
            f"Actual: {actual:<10} "
            f"Predicted: {predicted:<10} "
            f"Confidence: {confidence:.2f}% "
            f"-> {status}"
        )


if __name__ == "__main__":
    main()