import os
import cv2
import numpy as np
import mediapipe as mp

# ============================================================
# Configuration
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

DATASET_DIR = os.path.join(
    BASE_DIR,
    "dataset",
    "asl_dynamic_words"
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "processed",
    "dynamic_sequences"
)

WORDS = [
    "HELLO",
    "THANKYOU",
    "SORRY",
    "YES",
    "NO"
]

MAX_FRAMES = 30
FEATURES_PER_FRAME = 63

# ============================================================
# MediaPipe
# ============================================================

mp_hands = mp.solutions.hands

hands = mp_hands.Hands(
    static_image_mode=True,
    max_num_hands=1,
    min_detection_confidence=0.5
)


# ============================================================
# Extract landmarks from one frame
# ============================================================

def extract_landmarks(frame):

    rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    results = hands.process(rgb)

    if not results.multi_hand_landmarks:
        return None

    hand = results.multi_hand_landmarks[0]

    features = []

    for landmark in hand.landmark:
        features.extend([
            landmark.x,
            landmark.y,
            landmark.z
        ])

    return features


# ============================================================
# Read one video
# ============================================================

def process_video(video_path):

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"Could not open: {video_path}")
        return None

    total_frames = int(
        cap.get(cv2.CAP_PROP_FRAME_COUNT)
    )

    if total_frames <= 0:
        cap.release()
        return None

    # Select 30 frames uniformly from the video
    frame_indices = np.linspace(
        0,
        total_frames - 1,
        MAX_FRAMES
    ).astype(int)

    sequence = []

    for frame_index in frame_indices:

        cap.set(
            cv2.CAP_PROP_POS_FRAMES,
            int(frame_index)
        )

        success, frame = cap.read()

        if not success:
            continue

        features = extract_landmarks(frame)

        if features is not None:
            sequence.append(features)

    cap.release()

    if len(sequence) == 0:
        return None

    # Convert to numpy
    sequence = np.array(
        sequence,
        dtype=np.float32
    )

    # ========================================================
    # Make every sequence exactly 30 frames
    # ========================================================

    if len(sequence) < MAX_FRAMES:

        last_frame = sequence[-1]

        padding_count = (
            MAX_FRAMES - len(sequence)
        )

        padding = np.repeat(
            last_frame[np.newaxis, :],
            padding_count,
            axis=0
        )

        sequence = np.vstack([
            sequence,
            padding
        ])

    elif len(sequence) > MAX_FRAMES:

        sequence = sequence[:MAX_FRAMES]

    return sequence


# ============================================================
# Process entire dataset
# ============================================================

def main():

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    total_processed = 0
    total_failed = 0

    print("\n========================================")
    print("DYNAMIC WORD LANDMARK EXTRACTION")
    print("========================================")

    print(f"Dataset : {DATASET_DIR}")
    print(f"Output  : {OUTPUT_DIR}")

    for word in WORDS:

        word_dir = os.path.join(
            DATASET_DIR,
            word
        )

        if not os.path.exists(word_dir):

            print(
                f"\nWARNING: Folder not found: {word_dir}"
            )

            continue

        output_word_dir = os.path.join(
            OUTPUT_DIR,
            word
        )

        os.makedirs(
            output_word_dir,
            exist_ok=True
        )

        videos = [
            file
            for file in os.listdir(word_dir)
            if file.lower().endswith(".avi")
        ]

        print(
            f"\n{word}: {len(videos)} videos"
        )

        for video_file in videos:

            video_path = os.path.join(
                word_dir,
                video_file
            )

            output_name = (
                os.path.splitext(video_file)[0]
                + ".npy"
            )

            output_path = os.path.join(
                output_word_dir,
                output_name
            )

            print(
                f"Processing: {video_file}"
            )

            sequence = process_video(
                video_path
            )

            if sequence is None:

                print(
                    "  FAILED - no hand landmarks"
                )

                total_failed += 1
                continue

            np.save(
                output_path,
                sequence
            )

            print(
                f"  Saved: {sequence.shape}"
            )

            total_processed += 1

    print("\n========================================")
    print("EXTRACTION COMPLETED")
    print("========================================")

    print(
        f"Successful videos : {total_processed}"
    )

    print(
        f"Failed videos     : {total_failed}"
    )

    print(
        f"Expected shape    : ({MAX_FRAMES}, {FEATURES_PER_FRAME})"
    )


# ============================================================
# Entry point
# ============================================================

if __name__ == "__main__":
    main()