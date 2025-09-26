# Speaking Tests Management Documentation

## Overview
The Speaking Tests Management system allows administrators to create, manage, and organize IELTS speaking tests. Speaking tests consist of individual questions with specific timing requirements for preparation and response.

## Speaking Test Structure

### Speaking Test
- **Test ID**: Unique identifier
- **Title**: Test name (e.g., "IELTS Speaking Test 1")
- **Difficulty**: Easy, Intermediate, Hard
- **Description**: Optional test description
- **Questions**: Collection of speaking questions

### Speaking Question
- **Question ID**: Unique identifier
- **Test ID**: Parent test reference
- **Question Number**: Order in the test (1, 2, 3...)
- **Prompt**: The question text for the student
- **Preparation Time**: Time in seconds for preparation (default: 15s)
- **Response Time**: Time in seconds for response (default: 60s)

## Admin Endpoints

All endpoints require admin authentication via JWT token in the Authorization header.

### Authentication Header
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 1. CREATE OPERATIONS

### Create Speaking Test
**Endpoint:** `POST /admin/speaking/tests`

**Description:** Create a new speaking test

**Request Body:**
```json
{
  "title": "IELTS Speaking Test - Part 1",
  "difficulty": "Intermediate",
  "description": "General questions about personal topics"
}
```

**Request Fields:**
- `title` (required): Test name
- `difficulty` (required): "Easy", "Intermediate", or "Hard"
- `description` (optional): Test description

**Response:**
```json
{
  "test_id": 1,
  "message": "Speaking test created successfully"
}
```

---

### Create Speaking Question
**Endpoint:** `POST /admin/speaking/questions`

**Description:** Add a question to an existing speaking test

**Request Body:**
```json
{
  "test_id": 1,
  "question_number": 1,
  "prompt": "Tell me about your hometown. What do you like most about it?",
  "preparation_time": 15,
  "response_time": 90
}
```

**Request Fields:**
- `test_id` (required): ID of the parent test
- `question_number` (required): Order in the test
- `prompt` (required): Question text
- `preparation_time` (optional): Preparation time in seconds (default: 15)
- `response_time` (optional): Response time in seconds (default: 60)

**Response:**
```json
{
  "question_id": 1,
  "message": "Speaking question created successfully"
}
```

---

## 2. READ OPERATIONS

### Get All Speaking Tests
**Endpoint:** `GET /admin/speaking/tests`

**Description:** Retrieve all speaking tests with basic information

**Response:**
```json
[
  {
    "id": 1,
    "title": "IELTS Speaking Test - Part 1",
    "difficulty": "Intermediate",
    "description": "General questions about personal topics",
    "created_at": "2024-01-15T10:30:00"
  },
  {
    "id": 2,
    "title": "IELTS Speaking Test - Part 2",
    "difficulty": "Hard",
    "description": "Long turn speaking tasks",
    "created_at": "2024-01-16T14:20:00"
  }
]
```

---

### Get Speaking Test Details
**Endpoint:** `GET /admin/speaking/tests/{test_id}`

**Description:** Get detailed information about a specific speaking test including all questions

**Path Parameters:**
- `test_id`: ID of the speaking test

**Response:**
```json
{
  "id": 1,
  "title": "IELTS Speaking Test - Part 1",
  "difficulty": "Intermediate",
  "description": "General questions about personal topics",
  "created_at": "2024-01-15T10:30:00",
  "questions": [
    {
      "id": 1,
      "question_number": 1,
      "prompt": "Tell me about your hometown. What do you like most about it?",
      "preparation_time": 15,
      "response_time": 90
    },
    {
      "id": 2,
      "question_number": 2,
      "prompt": "Do you prefer living in the city or countryside? Why?",
      "preparation_time": 15,
      "response_time": 90
    }
  ]
}
```

---

### Get Speaking Question
**Endpoint:** `GET /admin/speaking/questions/{question_id}`

**Description:** Get details of a specific speaking question

**Path Parameters:**
- `question_id`: ID of the speaking question

**Response:**
```json
{
  "id": 1,
  "test_id": 1,
  "question_number": 1,
  "prompt": "Tell me about your hometown. What do you like most about it?",
  "preparation_time": 15,
  "response_time": 90
}
```

---

## 3. UPDATE OPERATIONS

### Update Speaking Test
**Endpoint:** `PUT /admin/speaking/tests/{test_id}`

**Description:** Update speaking test information

**Path Parameters:**
- `test_id`: ID of the speaking test

**Request Body:**
```json
{
  "title": "Updated IELTS Speaking Test - Part 1",
  "difficulty": "Hard",
  "description": "Updated description for personal topics"
}
```

**Request Fields (all optional):**
- `title`: New test name
- `difficulty`: New difficulty level
- `description`: New test description

**Response:**
```json
{
  "message": "Speaking test updated successfully"
}
```

---

### Update Speaking Question
**Endpoint:** `PUT /admin/speaking/questions/{question_id}`

**Description:** Update a speaking question

**Path Parameters:**
- `question_id`: ID of the speaking question

**Request Body:**
```json
{
  "prompt": "Updated: Tell me about your hometown and describe the culture there.",
  "preparation_time": 20,
  "response_time": 120
}
```

**Request Fields (all optional):**
- `prompt`: New question text
- `preparation_time`: New preparation time in seconds
- `response_time`: New response time in seconds

**Response:**
```json
{
  "message": "Speaking question updated successfully"
}
```

---

## 4. DELETE OPERATIONS

### Delete Speaking Test
**Endpoint:** `DELETE /admin/speaking/tests/{test_id}`

**Description:** Delete a speaking test and all its questions

**Path Parameters:**
- `test_id`: ID of the speaking test

**Response:**
```json
{
  "message": "Speaking test deleted successfully"
}
```

**Note:** This will also delete all questions associated with the test.

---

### Delete Speaking Question
**Endpoint:** `DELETE /admin/speaking/questions/{question_id}`

**Description:** Delete a specific speaking question

**Path Parameters:**
- `question_id`: ID of the speaking question

**Response:**
```json
{
  "message": "Speaking question deleted successfully"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request data"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Admin access required"
}
```

### 404 Not Found
```json
{
  "detail": "Speaking test not found"
}
```

## Best Practices

### Test Creation
1. Use descriptive titles that indicate the test part/level
2. Set appropriate difficulty levels based on question complexity
3. Include helpful descriptions for test organization

### Question Management
1. Number questions sequentially within each test
2. Set realistic preparation and response times
3. Write clear, grammatically correct prompts
4. Consider IELTS speaking test format requirements

### Timing Guidelines
- **Part 1 Questions**: 15s preparation, 30-45s response
- **Part 2 Questions**: 60s preparation, 120s response
- **Part 3 Questions**: 15s preparation, 60-90s response

### Content Guidelines
1. **Part 1**: Personal questions about familiar topics
2. **Part 2**: Individual long turn with cue card
3. **Part 3**: Abstract discussions related to Part 2 topic

## Example Complete Test Creation

```bash
# 1. Create the test
POST /admin/speaking/tests
{
  "title": "IELTS Speaking Mock Test 1",
  "difficulty": "Intermediate",
  "description": "Complete speaking test covering all three parts"
}

# 2. Add Part 1 questions
POST /admin/speaking/questions
{
  "test_id": 1,
  "question_number": 1,
  "prompt": "What's your full name?",
  "preparation_time": 5,
  "response_time": 15
}

# 3. Add Part 2 question
POST /admin/speaking/questions
{
  "test_id": 1,
  "question_number": 2,
  "prompt": "Describe a memorable journey you have taken. You should say: where you went, who you went with, what you did there, and explain why it was memorable.",
  "preparation_time": 60,
  "response_time": 120
}

# 4. Add Part 3 questions
POST /admin/speaking/questions
{
  "test_id": 1,
  "question_number": 3,
  "prompt": "Do you think traveling is important for young people? Why?",
  "preparation_time": 15,
  "response_time": 90
}
```