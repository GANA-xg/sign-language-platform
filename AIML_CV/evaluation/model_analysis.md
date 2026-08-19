# Model Analysis

Dataset Used
------------
ASL Alphabet Dataset

Number of Classes
-----------------
29

Images per Class
----------------
Approximately 3000

Total Samples
-------------
63,676

Model
-----
XGBoost Classifier

Features
--------
63 Hand Landmarks (x, y, z coordinates) extracted using MediaPipe Hands

Overall Accuracy
----------------
98.76%

Prediction Performance
----------------------
Average Prediction Time : 10.427 ms
Throughput              : 95.91 FPS
Model Size              : 11.96 MB

Evaluation Files
----------------
✓ Accuracy Report
✓ Classification Report
✓ Confusion Matrix
✓ Misclassified Samples
✓ Model Comparison
✓ Optimization Report
✓ Robustness Report

Weak Classes
------------
M ↔ N
U ↔ V
X ↔ S
R ↔ U
J ↔ G

Reason
------
These gestures have very similar finger positions, making them difficult to distinguish. As a result, the model occasionally predicts one class as another.

Robustness Testing
------------------
The trained model was tested under different real-world conditions.

✓ Different users
✓ Different lighting conditions
✓ Different backgrounds
✓ Different camera distances

The model maintained stable real-time predictions across all tested conditions. Minor landmark jitter was observed under low-light conditions but did not significantly affect prediction accuracy.

Strengths
---------
✓ High classification accuracy (98.76%)
✓ Real-time webcam prediction
✓ Fast inference (~10 ms per prediction)
✓ Stable performance across different users and environments
✓ Lightweight model suitable for desktop deployment

Limitations
-----------
- Similar hand gestures (M/N, U/V, X/S) may occasionally be confused.
- Dynamic gestures are not fully supported; the movement tracker is a proof-of-concept based on simple rule-based motion detection.

Future Improvements
-------------------
- Improve recognition of similar hand gestures using additional feature engineering.
- Explore hyperparameter tuning for further optimization.
- Train a sequence-based model (e.g., LSTM or Transformer) for dynamic gesture recognition.
- Expand the dataset with additional users and more challenging environmental conditions.