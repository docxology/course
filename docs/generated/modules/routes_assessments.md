# Module: routes.assessments

**File:** `src/curriculum/routes/assessments.py`

## Description

Assessment API routes.

## Classes

### `CreateAssessmentRequest`

Request model for creating assessment.

**Inherits from:** BaseModel

**Methods:** 0

### `CreateQuestionRequest`

Request model for creating question.

**Inherits from:** BaseModel

**Methods:** 0

### `SubmitAnswerRequest`

Request model for submitting answer.

**Inherits from:** BaseModel

**Methods:** 0

### `AssessmentResponse`

Response model for assessment.

**Inherits from:** BaseModel

**Methods:** 0

### `QuestionResponse`

Response model for question.

**Inherits from:** BaseModel

**Methods:** 0

### `SubmissionResponse`

Response model for submission.

**Inherits from:** BaseModel

**Methods:** 0

## Functions

### `create_assessment`

Create a new assessment.

**Parameters:**

- `request: CreateAssessmentRequest`

- `current_user: User`

### `get_assessment`

Get assessment by ID.

**Parameters:**

- `assessment_id: UUID`

### `list_assessments`

List assessments.

**Parameters:**

- `content_id: Optional[UUID]`

- `current_user: User`

### `create_question`

Create a new question for assessment.

**Parameters:**

- `assessment_id: UUID`

- `request: CreateQuestionRequest`

- `current_user: User`

### `get_assessment_questions`

Get questions for assessment.

**Parameters:**

- `assessment_id: UUID`

### `start_submission`

Start a new submission.

**Parameters:**

- `assessment_id: UUID`

- `attempt_number: int`

- `current_user: User`

### `submit_answer`

Submit answer for a question.

**Parameters:**

- `submission_id: UUID`

- `request: SubmitAnswerRequest`

- `current_user: User`

### `submit_assessment`

Submit the complete assessment.

**Parameters:**

- `submission_id: UUID`

- `current_user: User`

### `get_submission`

Get submission details.

**Parameters:**

- `submission_id: UUID`

- `current_user: User`

### `get_user_submissions`

Get submissions for a user.

**Parameters:**

- `user_id: UUID`

- `assessment_id: Optional[UUID]`

- `current_user: User`

### `get_assessment_statistics`

Get assessment statistics.

**Parameters:**

- `assessment_id: UUID`

### `_assessment_to_response`

Convert Assessment model to response model.

**Parameters:**

- `assessment: Assessment`

### `_question_to_response`

Convert Question model to response model.

**Parameters:**

- `question: Question`

### `_submission_to_response`

Convert Submission model to response model.

**Parameters:**

- `submission: Submission`
