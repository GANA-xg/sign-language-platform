import cv2

from camera import Camera
from detector import HandDetector
from feature_extractor import FeatureExtractor
from config import WINDOW_NAME

camera = Camera()
detector = HandDetector()
extractor = FeatureExtractor()

while True:

    success, frame = camera.get_frame()

    if not success:
        break

    frame, landmarks = detector.detect(frame)

    if landmarks:

        features = extractor.extract_features(landmarks)

        # Display feature information
        cv2.putText(
            frame,
            f"Features: {len(features)}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            "Hand: Detected",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

    else:

        cv2.putText(
            frame,
            "Hand: Not Detected",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2
        )

    cv2.putText(
        frame,
        "Press Q to Exit",
        (10, frame.shape[0] - 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    cv2.imshow(WINDOW_NAME, frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()