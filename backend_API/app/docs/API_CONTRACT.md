# API Contract Document

## Project
**AI-Powered Sign Language Learning & Assessment Platform**


---

# Base URL

```
http://localhost:8000
```

---

# Authentication APIs

## 1. Register User

### Endpoint

```
POST /auth/register
```

### Description

Creates a new user account.

### Request Body

```json
{
  "name": "Ashley",
  "email": "ashley@gmail.com",
  "password": "Password@123",
  "role": "Learner"
}
```

### Success Response

**Status Code**

```
201 Created
```

```json
{
  "message": "User registered successfully"
}
```

### Error Response

```json
{
  "detail": "Email already exists"
}
```

---

## 2. Login

### Endpoint

```
POST /auth/login
```

### Description

Authenticates a user and returns a JWT access token.

### Request Body

```json
{
  "email": "ashley@gmail.com",
  "password": "Password@123"
}
```

### Success Response

**Status Code**

```
200 OK
```

```json
{
  "access_token": "jwt-token",
  "token_type": "Bearer"
}
```

### Error Response

```json
{
  "detail": "Invalid email or password"
}
```

---

## 3. Get User Profile

### Endpoint

```
GET /auth/profile
```

### Description

Returns the logged-in user's profile.

### Headers

```
Authorization: Bearer <JWT Token>
```

### Success Response

```json
{
  "id": 1,
  "name": "Ashley",
  "email": "ashley@gmail.com",
  "role": "Learner"
}
```

---

# Course APIs

## 1. Get All Courses

### Endpoint

```
GET /courses
```

### Description

Returns all available sign language courses.

### Success Response

```json
[
  {
    "id": 1,
    "title": "Alphabet Course",
    "difficulty": "Beginner"
  },
  {
    "id": 2,
    "title": "Greetings",
    "difficulty": "Intermediate"
  }
]
```

---

## 2. Get Course by ID

### Endpoint

```
GET /courses/{id}
```

### Success Response

```json
{
  "id": 1,
  "title": "Alphabet Course",
  "description": "Learn the alphabet in sign language.",
  "difficulty": "Beginner"
}
```

---

## 3. Create Course

### Endpoint

```
POST /courses
```

### Request Body

```json
{
  "title": "Basic Signs",
  "description": "Introduction to basic signs",
  "difficulty": "Beginner"
}
```

### Success Response

```json
{
  "message": "Course created successfully"
}
```

---

## 4. Update Course

### Endpoint

```
PUT /courses/{id}
```

### Request Body

```json
{
  "title": "Updated Course",
  "description": "Updated description",
  "difficulty": "Intermediate"
}
```

### Success Response

```json
{
  "message": "Course updated successfully"
}
```

---

## 5. Delete Course

### Endpoint

```
DELETE /courses/{id}
```

### Success Response

```json
{
  "message": "Course deleted successfully"
}
```

---

# Lesson APIs

## 1. Get All Lessons

### Endpoint

```
GET /lessons
```

### Success Response

```json
[
  {
    "id": 1,
    "course_id": 1,
    "lesson_name": "Letter A"
  },
  {
    "id": 2,
    "course_id": 1,
    "lesson_name": "Letter B"
  }
]
```

---

## 2. Get Lesson by ID

### Endpoint

```
GET /lessons/{id}
```

### Success Response

```json
{
  "id": 1,
  "course_id": 1,
  "lesson_name": "Letter A"
}
```

---

## 3. Create Lesson

### Endpoint

```
POST /lessons
```

### Request Body

```json
{
  "course_id": 1,
  "lesson_name": "Letter C"
}
```

### Success Response

```json
{
  "message": "Lesson created successfully"
}
```

---

## 4. Update Lesson

### Endpoint

```
PUT /lessons/{id}
```

### Request Body

```json
{
  "lesson_name": "Updated Lesson"
}
```

### Success Response

```json
{
  "message": "Lesson updated successfully"
}
```

---

## 5. Delete Lesson

### Endpoint

```
DELETE /lessons/{id}
```

### Success Response

```json
{
  "message": "Lesson deleted successfully"
}
```

---

# Health Check API

## Endpoint

```
GET /health
```

### Success Response

```json
{
  "status": "healthy",
  "service": "Backend API"
}
```

---

# HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Resource Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 404 | Resource Not Found |
| 500 | Internal Server Error |

---

# Authentication

The backend will use **JWT (JSON Web Token)**.

Every protected endpoint must include:

```
Authorization: Bearer <JWT Token>
```

---

# Planned Technology Stack

- FastAPI
- Python 3.11+
- SQLAlchemy
- PostgreSQL
- JWT Authentication
- Pydantic
- Uvicorn

---

# Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 07 July 2026 | Initial API Contract |