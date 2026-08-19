# Model Robustness Testing Report

## Objective

Evaluate the trained ASL recognition model under different real-world conditions to verify its robustness and generalization ability.

---

## Test Conditions

The trained model was tested under the following conditions:

- Normal lighting
- Bright lighting
- Low lighting
- White background
- Dark background
- Busy background
- Near distance
- Medium distance
- Far distance
- Multiple users

---

## Test Summary

| Test Condition | Result |
|---------------|--------|
| Normal Lighting | Pass |
| Bright Lighting | Pass |
| Low Lighting | Pass |
| White Background | Pass |
| Dark Background | Pass |
| Busy Background | Pass |
| Near Distance | Pass |
| Medium Distance | Pass |
| Far Distance | Pass |
| Different Users | Pass |

---

## Observations

- The model maintained stable predictions across different lighting conditions.
- Recognition remained accurate with different backgrounds.
- The trained model generalized well to multiple users.
- Landmark detection remained stable at different distances.
- Minor landmark jitter was observed in low-light conditions but did not significantly affect prediction accuracy.

---

## Conclusion

The trained XGBoost model demonstrated robust real-time performance under different environmental conditions and with multiple users. The diversity of the training dataset contributed to strong generalization, enabling reliable predictions across lighting conditions, backgrounds, camera distances, and different users.