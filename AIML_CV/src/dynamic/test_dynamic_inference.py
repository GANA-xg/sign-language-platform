import os
import sys


# Add dynamic folder to Python path
CURRENT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

sys.path.insert(
    0,
    CURRENT_DIR
)


from dynamic_inference import predict_video


# ============================================================
# TEST VIDEO
# ============================================================

VIDEO_PATH = os.path.join(
    os.path.dirname(
        os.path.dirname(
            CURRENT_DIR
        )
    ),
    "dataset",
    "asl_dynamic_words",
    "HELLO",
    "HELLO_clip1.avi"
)


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n========================================")
    print("DYNAMIC VIDEO INFERENCE TEST")
    print("========================================")

    print(
        "Video:",
        VIDEO_PATH
    )

    if not os.path.exists(
        VIDEO_PATH
    ):

        print(
            "\nERROR: Video not found."
        )

        return

    try:

        result = predict_video(
            VIDEO_PATH
        )

        print("\n========================================")
        print("RESULT")
        print("========================================")

        print(
            "Prediction     :",
            result["prediction"]
        )

        print(
            "Confidence     :",
            f'{result["confidence"]}%'
        )

        print(
            "Sequence shape :",
            result["sequence_shape"]
        )

        print("========================================")

    except Exception as e:

        print("\nERROR:")
        print(e)


if __name__ == "__main__":
    main()