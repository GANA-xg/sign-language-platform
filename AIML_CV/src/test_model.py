import os
import time
import requests

# ==========================================
# Configuration
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TEST_FOLDER = os.path.join(
    BASE_DIR,
    "..",
    "dataset",
    "asl_alphabet_test"
)

API_URL = "http://127.0.0.1:8001/predict"

total = 0
correct = 0
processing_times = []

print("=" * 70)
print("SIGN LANGUAGE API TEST")
print("=" * 70)

for image_name in sorted(os.listdir(TEST_FOLDER)):

    image_path = os.path.join(TEST_FOLDER, image_name)

    if not os.path.isfile(image_path):
        continue

    # Skip non-image files
    if not image_name.lower().endswith((".jpg", ".jpeg", ".png")):
        continue

    # Extract expected label
    actual_label = image_name.split("_")[0]

    with open(image_path, "rb") as image_file:

        files = {
            "file": (image_name, image_file, "image/jpeg")
        }

        start = time.time()
        response = requests.post(API_URL, files=files)
        end = time.time()

    elapsed = round((end - start) * 1000, 2)
    processing_times.append(elapsed)

    total += 1

    if response.status_code != 200:
        print(f"{image_name:20} API Error")
        continue

    result = response.json()

    if not result.get("success", False):
        print(f"{image_name:20} -> {result['message']}")
        continue

    predicted = result["prediction"]
    confidence = result["confidence"]

    if predicted == actual_label:
        correct += 1
        status = "PASS"
    else:
        status = "FAIL"

    print(
        f"{image_name:20}"
        f" Actual:{actual_label:8}"
        f" Pred:{predicted:8}"
        f" Conf:{confidence:6.2f}%"
        f" Time:{elapsed:7.2f} ms"
        f" {status}"
    )

print("\n" + "=" * 70)

accuracy = (correct / total) * 100 if total else 0
avg_time = sum(processing_times) / len(processing_times) if processing_times else 0

print(f"Total Images        : {total}")
print(f"Correct Predictions : {correct}")
print(f"Accuracy            : {accuracy:.2f}%")
print(f"Average Time        : {avg_time:.2f} ms")

print("=" * 70)