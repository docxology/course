# Module: core.assessment

**File:** `src/curriculum/core/assessment.py`

## Description

Assessment models for quizzes and evaluations.

## Classes

### `QuestionType`

Types of assessment questions.

**Inherits from:** str, Enum

**Methods:** 0

### `DifficultyLevel`

Difficulty levels for questions.

**Inherits from:** str, Enum

**Methods:** 0

### `GradingStatus`

Status of assessment grading.

**Inherits from:** str, Enum

**Methods:** 0

### `Assessment`

Assessment (quiz, exam, etc.) entity.

**Inherits from:** BaseEntity

**Methods:** 1


**Method List:**

- `is_available_now`: Check if assessment is currently available.

### `Question`

Assessment question entity.

**Inherits from:** BaseEntity

**Methods:** 2


**Method List:**

- `calculate_score`: Calculate score for submitted answer.

- `_grade_coding_submission`: Grade coding submission (placeholder).

### `Submission`

Student submission for an assessment.

**Inherits from:** BaseEntity

**Methods:** 3


**Method List:**

- `submit`: Mark submission as submitted.

- `calculate_percentage`: Calculate percentage score.

- `check_passed`: Check if submission passed.

### `SubmissionResult`

Detailed result for a submission.

**Inherits from:** BaseEntity

**Methods:** 0
