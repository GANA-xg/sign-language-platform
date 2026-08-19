# Model Card

## Model Information

| Field | Value |
|-------|-------|
| Model Name | Sign Language Recognition Model |
| Version | 1.0 |
| Model Type | Supervised Machine Learning |
| Algorithm | XGBoost Classifier |

---

## Purpose

This model recognizes sign language hand gestures from images by extracting hand landmarks using MediaPipe and classifying them into corresponding sign language alphabets.

---

## Dataset

- Dataset Name: ASL Alphabet Dataset
- Number of Classes: 28
- Classes:
  - A-Z
  - space
  - nothing

---

## Input

- Image containing a hand gesture
- Feature Extraction:
  - MediaPipe Hands
  - 21 hand landmarks
  - 63 numerical features (x, y, z)

---

## Output

The model returns:

- Predicted Gesture
- Confidence Score
- Confidence Level
- Feedback
- Possible Issue
- Processing Time

---

## Technologies Used

- Python
- MediaPipe
- OpenCV
- XGBoost
- NumPy
- Scikit-Learn
- FastAPI

---

## Performance

- High confidence predictions on detected hands
- Average inference time: ~80–90 ms
- Prediction confidence generally above 97%

---

## Limitations

- Requires successful hand detection by MediaPipe.
- Performance may decrease under poor lighting.
- Incorrect hand positioning may reduce detection accuracy.

---

## Future Improvements

- Real-time continuous gesture recognition
- Sentence-level sign language recognition
- Deep Learning (CNN/LSTM/Transformer)
- Improved hand detection under challenging conditions