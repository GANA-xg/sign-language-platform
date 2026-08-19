import os
import glob
import time
import requests


# ==================================================
# API CONFIGURATION
# ==================================================

API_URL = "http://127.0.0.1:8001/predict"


# ==================================================
# FIND AIML_CV DIRECTORY
# ==================================================

SRC_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

AIML_DIR = os.path.dirname(
    SRC_DIR
)


# ==================================================
# FIND A TEST IMAGE AUTOMATICALLY
# ==================================================

DATASET_DIR = os.path.join(
    AIML_DIR,
    "dataset"
)

image_files = glob.glob(
    os.path.join(
        DATASET_DIR,
        "**",
        "*.jpg"
    ),
    recursive=True
)

if not image_files:

    image_files = glob.glob(
        os.path.join(
            DATASET_DIR,
            "**",
            "*.jpeg"
        ),
        recursive=True
    )

if not image_files:

    image_files = glob.glob(
        os.path.join(
            DATASET_DIR,
            "**",
            "*.png"
        ),
        recursive=True
    )


# Use the first available image
IMAGE_PATH = None

if image_files:

    IMAGE_PATH = os.path.normpath(
        image_files[0]
    )


# ==================================================
# BENCHMARK
# ==================================================

def benchmark():

    total_requests = 20

    times = []

    print("========================================")
    print("       SIGN LANGUAGE API BENCHMARK")
    print("========================================")

    # --------------------------------------------------
    # Check test image
    # --------------------------------------------------

    if IMAGE_PATH is None:

        print(
            "ERROR: No test image found "
            "inside AIML_CV/dataset."
        )

        return

    print(
        f"Test Image : {IMAGE_PATH}"
    )

    print(
        "\nTest image found successfully."
    )

    # --------------------------------------------------
    # Send requests
    # --------------------------------------------------

    for i in range(total_requests):

        try:

            with open(
                IMAGE_PATH,
                "rb"
            ) as image:

                files = {
                    "file": (
                        os.path.basename(IMAGE_PATH),
                        image,
                        "image/jpeg"
                    )
                }

                start_time = time.perf_counter()

                response = requests.post(
                    API_URL,
                    files=files,
                    timeout=10
                )

                end_time = time.perf_counter()

            # --------------------------------------------------
            # Calculate API latency
            # --------------------------------------------------

            elapsed_ms = (
                end_time - start_time
            ) * 1000

            print(
                f"Request {i + 1:02d} : "
                f"{elapsed_ms:.2f} ms | "
                f"Status : {response.status_code}"
            )

            # --------------------------------------------------
            # Store successful requests
            # --------------------------------------------------

            if response.status_code == 200:

                times.append(
                    elapsed_ms
                )

        except requests.RequestException as e:

            print(
                f"Request {i + 1:02d} failed: {e}"
            )

        except Exception as e:

            print(
                f"Request {i + 1:02d} error: {e}"
            )

    # ==================================================
    # RESULTS
    # ==================================================

    if not times:

        print(
            "\nNo successful API requests."
        )

        return

    average_latency = (
        sum(times) / len(times)
    )

    minimum_latency = min(times)

    maximum_latency = max(times)

    print(
        "\n========================================"
    )

    print(
        "          BENCHMARK RESULTS"
    )

    print(
        "========================================"
    )

    print(
        f"Total Requests      : {total_requests}"
    )

    print(
        f"Successful Requests : {len(times)}"
    )

    print(
        f"Average Latency     : "
        f"{average_latency:.2f} ms"
    )

    print(
        f"Minimum Latency     : "
        f"{minimum_latency:.2f} ms"
    )

    print(
        f"Maximum Latency     : "
        f"{maximum_latency:.2f} ms"
    )

    print(
        f"Average Latency     : "
        f"{average_latency / 1000:.3f} seconds"
    )

    # ==================================================
    # REQUIREMENT CHECK
    # ==================================================

    print(
        "\n========================================"
    )

    if average_latency <= 3000:

        print(
            "RESULT: PASS"
        )

        print(
            "API response time is within "
            "the 1-3 second requirement."
        )

    else:

        print(
            "RESULT: NEEDS IMPROVEMENT"
        )

        print(
            "API response time exceeds "
            "the 3 second requirement."
        )

    print(
        "========================================"
    )


# ==================================================
# MAIN
# ==================================================

if __name__ == "__main__":

    benchmark()