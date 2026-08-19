import os
import cv2
import joblib
import mediapipe as mp

# ==============================
# Load Model
# ==============================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "..", "models", "xgboost_landmark.pkl")
ENCODER_PATH = os.path.join(BASE_DIR, "..", "models", "label_encoder.pkl")

model = joblib.load(MODEL_PATH)
encoder = joblib.load(ENCODER_PATH)

# ==============================
# MediaPipe
# ==============================

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# ==============================
# Webcam
# ==============================

cap = cv2.VideoCapture(0)

while True:

    success, frame = cap.read()

    if not success:
        break

    frame = cv2.flip(frame, 1)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = hands.process(rgb)

    prediction = "No Hand"

    if results.multi_hand_landmarks:

        hand = results.multi_hand_landmarks[0]

        mp_draw.draw_landmarks(
            frame,
            hand,
            mp_hands.HAND_CONNECTIONS
        )

        features = []

        for lm in hand.landmark:
            features.extend([
                lm.x,
                lm.y,
                lm.z
            ])

        pred = model.predict([features])

        prediction = encoder.inverse_transform(pred)[0]

    cv2.putText(
        frame,
        f"Prediction : {prediction}",
        (20,40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0,255,0),
        2
    )

    cv2.imshow("ASL Recognition", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()