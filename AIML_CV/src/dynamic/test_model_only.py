import os
import glob
import numpy as np
import tensorflow as tf


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "dynamic_word_model.keras"
)

LABEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "dynamic_label_encoder.npy"
)

DATA_DIR = os.path.join(
    BASE_DIR,
    "processed",
    "dynamic_sequences"
)


# ============================================================
# Load model
# ============================================================

print("Loading model...")

model = tf.keras.models.load_model(
    MODEL_PATH
)

labels = np.load(
    LABEL_PATH,
    allow_pickle=True
)

print("Model loaded.")
print("Classes:", labels)


# ============================================================
# Test one video from every class
# ============================================================

words = [
    "HELLO",
    "NO",
    "SORRY",
    "THANKYOU",
    "YES"
]


print("\n========================================")
print("DYNAMIC MODEL TEST")
print("========================================")


for word in words:

    files = glob.glob(
        os.path.join(
            DATA_DIR,
            word,
            "*.npy"
        )
    )

    if not files:

        print(
            f"{word}: NO FILE FOUND"
        )

        continue

    file_path = files[0]

    sequence = np.load(
        file_path
    )

    input_data = np.expand_dims(
        sequence,
        axis=0
    )

    probabilities = model.predict(
        input_data,
        verbose=0
    )[0]

    predicted_index = int(
        np.argmax(probabilities)
    )

    prediction = str(
        labels[predicted_index]
    )

    confidence = (
        float(
            probabilities[predicted_index]
        ) * 100
    )

    status = (
        "CORRECT"
        if prediction == word
        else "WRONG"
    )

    print(
        f"{word:<10} → "
        f"{prediction:<10} "
        f"{confidence:6.2f}% "
        f"{status}"
    )


print("\n========================================")
print("TEST COMPLETED")
print("========================================")