# Module: learning.assessment

**File:** `src/curriculum/learning/assessment.py`

## Description

Assessment and evaluation service.

## Classes

### `AssessmentService`

Service for managing assessments and evaluations.

**Methods:** 14


**Method List:**

- `__init__`: Initialize assessment service.

- `create_assessment`: Create a new assessment.

- `get_assessment`: Get assessment by ID.

- `create_question`: Create a new question.

- `get_question`: Get question by ID.

- `add_question_to_assessment`: Add a question to an assessment.

- `remove_question_from_assessment`: Remove a question from an assessment.

- `start_submission`: Start a new submission for an assessment.

- `get_submission`: Get submission by ID.

- `submit_answer`: Submit an answer for a question.

- `submit_assessment`: Submit the complete assessment.

- `grade_submission`: Grade a submission (auto-grade when possible).

- `get_user_submissions`: Get all submissions for a user.

- `get_assessment_statistics`: Get statistics for an assessment.
