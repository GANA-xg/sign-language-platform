# Day 8 – Model Optimization Report

## Model Information

- Model: XGBoost
- Dataset: ASL Landmark Dataset
- Total Samples: 63,676
- Classes: 29

---

## Performance Metrics

| Metric | Value |
|--------|--------|
| Accuracy | 98.76% |
| Prediction Time | 10.427 ms |
| Throughput | 95.91 FPS |
| Model Size | 11.96 MB |

---

## Analysis

The trained XGBoost model was benchmarked to evaluate its inference speed and deployment readiness.

Results show that the model performs one prediction in approximately **10.4 milliseconds**, allowing it to process nearly **96 frames per second**, which exceeds the requirements for real-time webcam recognition.

The serialized model size is **11.96 MB**, making it lightweight enough for deployment in desktop applications.

Since both inference speed and accuracy meet the project requirements, no additional optimization was necessary.

---

## Conclusion

The current XGBoost model satisfies the real-time performance requirements while maintaining high classification accuracy.