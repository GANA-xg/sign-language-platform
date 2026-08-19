# API Documentation

## Base URL

```
http://127.0.0.1:8001
```

---

# 1. Predict Gesture

### Endpoint

```
POST /predict
```

### Description

Predicts the sign language gesture from an uploaded image.

### Request

Content-Type:

```
multipart/form-data
```

Parameter

| Name | Type | Required |
|------|------|----------|
| file | Image | Yes |

### Successful Response

```json
{
  "success": true,
  "prediction": "A",
  "confidence": 99.87,
  "confidence_level": "High",
  "feedback": "Correct gesture detected.",
  "possible_issue": null,
  "processing_time_ms": 82
}
```

---

# 2. Prediction History

### Endpoint

```
GET /history
```

### Description

Returns all previous predictions.

### Response

```json
[
  {
    "prediction": "A",
    "confidence": 99.87,
    "timestamp": "2026-07-22T11:30:00"
  }
]
```

---

# 3. Clear History

### Endpoint

```
DELETE /history
```

### Description

Deletes all stored prediction history.

### Response

```json
{
  "message": "History cleared successfully."
}
```

---

# 4. Analytics

### Endpoint

```
GET /analytics
```

### Description

Returns statistics of predictions.

### Response

```json
{
  "total_predictions": 120,
  "average_confidence": 98.5,
  "most_predicted_gesture": "A"
}
```

---

# 5. Dashboard

### Endpoint

```
GET /dashboard
```

### Description

Returns dashboard summary including prediction count and recent activity.

### Response

```json
{
  "total_predictions": 120,
  "recent_predictions": [
    {
      "gesture": "A",
      "confidence": 99.8
    }
  ]
}
```

---

# HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Invalid Request |
| 404 | Resource Not Found |
| 500 | Internal Server Error |

---

# Technologies

- FastAPI
- MediaPipe
- XGBoost
- OpenCV
- Python