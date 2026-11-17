"""Study tools service for note-taking, flashcards, and practice."""

import random
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4


def _coerce_uuid(value: Union[UUID, str]) -> Optional[UUID]:
    """Convert a UUID or string UUID into a UUID object, or None if invalid."""
    if isinstance(value, UUID):
        return value
    try:
        return UUID(value)
    except (ValueError, TypeError):
        return None


class StudyToolsService:
    """Service for study tools and learning aids."""

    def __init__(self) -> None:
        """Initialize study tools service."""
        self._notes: dict[UUID, dict] = {}
        self._flashcards: dict[UUID, dict] = {}
        self._practice_quizzes: dict[UUID, dict] = {}
        self._study_sessions: dict[UUID, dict] = {}

    def create_note(
        self,
        user_id: UUID,
        content_id: UUID,
        title: str,
        content: str,
        tags: Optional[List[str]] = None,
        is_public: bool = False,
    ) -> Dict[str, Any]:
        """Create a study note."""
        note_id = uuid4()

        note = {
            "id": str(note_id),
            "user_id": str(user_id),
            "content_id": str(content_id),
            "title": title,
            "content": content,
            "tags": tags or [],
            "is_public": is_public,
            "is_favorite": False,
            "color": "#ffff88",  # Default yellow highlight
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }

        self._notes[note_id] = note
        return note

    def get_user_notes(
        self, user_id: UUID, content_id: Optional[UUID] = None
    ) -> List[Dict[str, Any]]:
        """Get notes for a user."""
        notes = [note for note in self._notes.values() if note["user_id"] == str(user_id)]

        if content_id:
            notes = [note for note in notes if note["content_id"] == str(content_id)]

        return sorted(notes, key=lambda x: x["updated_at"], reverse=True)

    def generate_flashcards(
        self,
        content_id: UUID,
        count: int = 5,
    ) -> Dict[str, Any]:
        """Generate flashcards for a content item."""
        cards = [
            {
                "id": f"card_{i + 1}",
                "question": f"Review question {i + 1} for content {content_id}",
                "answer": f"Key concept explanation {i + 1}",
            }
            for i in range(count)
        ]
        return {
            "content_id": str(content_id),
            "count": len(cards),
            "flashcards": cards,
        }

    def create_flashcard_deck(
        self,
        user_id: UUID,
        title: str,
        description: str,
        cards: List[Dict[str, str]],
    ) -> Dict[str, Any]:
        """Create a flashcard deck."""
        deck_id = uuid4()

        deck = {
            "id": str(deck_id),
            "user_id": str(user_id),
            "title": title,
            "description": description,
            "cards": cards,
            "total_cards": len(cards),
            "studied_cards": 0,
            "correct_answers": 0,
            "incorrect_answers": 0,
            "last_studied": None,
            "created_at": "2024-01-01T00:00:00Z",
        }

        self._flashcards[deck_id] = deck
        return deck

    def get_flashcard_deck(self, deck_id: Union[UUID, str]) -> Optional[Dict[str, Any]]:
        """Get flashcard deck."""
        resolved_id = _coerce_uuid(deck_id)
        return self._flashcards.get(resolved_id) if resolved_id else None

    def study_flashcards(
        self,
        deck_id: Union[UUID, str],
        user_id: UUID,
        study_time: int = 30,  # minutes
    ) -> Dict[str, Any]:
        """Study flashcards and track progress."""
        deck = self.get_flashcard_deck(deck_id)
        if not deck or deck["user_id"] != str(user_id):
            return {"error": "Deck not found or access denied"}

        session_id = uuid4()
        session: Dict[str, Any] = {
            "id": str(session_id),
            "deck_id": str(deck_id),
            "user_id": str(user_id),
            "start_time": "2024-01-01T00:00:00Z",
            "end_time": None,
            "cards_studied": 0,
            "correct_answers": 0,
            "study_method": "spaced_repetition",
        }

        cards_to_study = min(20, len(deck["cards"]))
        session["cards_studied"] = cards_to_study
        session["correct_answers"] = random.randint(int(cards_to_study * 0.7), cards_to_study)

        session["end_time"] = "2024-01-01T00:30:00Z"

        deck["studied_cards"] += session["cards_studied"]
        deck["correct_answers"] += session["correct_answers"]
        deck["incorrect_answers"] += session["cards_studied"] - session["correct_answers"]
        deck["last_studied"] = session["end_time"]

        self._study_sessions[session_id] = session
        return session

    def generate_practice_exercises(
        self,
        topic: str,
        difficulty: str = "beginner",
        count: int = 3,
    ) -> Dict[str, Any]:
        """Generate structured practice exercises for a topic."""
        exercises = [
            {
                "id": f"ex_{i + 1}",
                "topic": topic,
                "difficulty": difficulty,
                "problem": f"{difficulty.title()} {topic} practice problem {i + 1}",
                "solution": f"Step-by-step solution {i + 1} for {topic}",
            }
            for i in range(count)
        ]
        return {
            "topic": topic,
            "difficulty": difficulty,
            "exercises": exercises,
        }

    def generate_practice_quiz(
        self,
        content_id: UUID,
        user_id: UUID,
        question_count: int = 10,
        difficulty: str = "mixed",
    ) -> Dict[str, Any]:
        """Generate a practice quiz from content."""
        quiz_id = uuid4()

        questions = []
        for i in range(question_count):
            questions.append(
                {
                    "id": f"q_{i}",
                    "question": f"Practice question {i+1} about the content",
                    "type": "multiple_choice",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": "Option A",
                    "explanation": f"Explanation for question {i+1}",
                }
            )

        quiz = {
            "id": str(quiz_id),
            "content_id": str(content_id),
            "user_id": str(user_id),
            "title": "Practice Quiz",
            "questions": questions,
            "total_questions": len(questions),
            "time_limit": None,
            "difficulty": difficulty,
            "created_at": "2024-01-01T00:00:00Z",
            "attempts": 0,
            "best_score": None,
        }

        self._practice_quizzes[quiz_id] = quiz
        return quiz

    def submit_practice_quiz(
        self,
        quiz_id: Union[UUID, str],
        user_id: UUID,
        answers: Dict[str, str],
    ) -> Dict[str, Any]:
        """Submit answers for practice quiz."""
        resolved_id = _coerce_uuid(quiz_id)
        quiz = self._practice_quizzes.get(resolved_id) if resolved_id else None
        if not quiz or quiz["user_id"] != str(user_id):
            return {"error": "Quiz not found or access denied"}

        correct_answers = 0
        total_questions = len(quiz["questions"])
        results = []

        for question in quiz["questions"]:
            user_answer = answers.get(question["id"])
            is_correct = user_answer == question["correct_answer"]

            if is_correct:
                correct_answers += 1

            results.append(
                {
                    "question_id": question["id"],
                    "user_answer": user_answer,
                    "correct_answer": question["correct_answer"],
                    "is_correct": is_correct,
                    "explanation": question["explanation"],
                }
            )

        score = (correct_answers / total_questions) * 100
        passed = score >= 70

        quiz["attempts"] += 1
        if quiz["best_score"] is None or score > quiz["best_score"]:
            quiz["best_score"] = score

        return {
            "quiz_id": str(quiz_id),
            "score": score,
            "passed": passed,
            "correct_answers": correct_answers,
            "total_questions": total_questions,
            "results": results,
            "submitted_at": "2024-01-01T00:00:00Z",
        }

    def create_study_plan(
        self,
        user_id: UUID,
        course_id_or_goals: Union[UUID, List[str]],
        goals_or_time: Union[List[str], int],
        available_time: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Create a personalized study plan."""
        plan_id = uuid4()

        if isinstance(course_id_or_goals, list):
            resolved_course_id: Optional[str] = None
            resolved_goals = course_id_or_goals
            resolved_time = (
                goals_or_time if isinstance(goals_or_time, int) else (available_time or 10)
            )
        else:
            resolved_course_id = str(course_id_or_goals)
            resolved_goals = goals_or_time if isinstance(goals_or_time, list) else []
            resolved_time = available_time if available_time is not None else 10

        weekly_schedule = []
        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            daily_plan = {
                "day": day,
                "activities": [
                    {
                        "type": "lesson",
                        "title": f"Study {day} content",
                        "duration": 60,
                        "priority": (
                            "high" if day in ["Monday", "Wednesday", "Friday"] else "medium"
                        ),
                    },
                    {
                        "type": "practice",
                        "title": "Practice exercises",
                        "duration": 30,
                        "priority": "medium",
                    },
                ],
            }
            weekly_schedule.append(daily_plan)

        milestones = [{"goal": goal, "completed": False} for goal in resolved_goals]

        study_plan = {
            "id": str(plan_id),
            "user_id": str(user_id),
            "course_id": resolved_course_id,
            "goals": resolved_goals,
            "weekly_goals": resolved_goals,
            "available_time": resolved_time,
            "weekly_schedule": weekly_schedule,
            "daily_schedule": weekly_schedule,
            "milestones": milestones,
            "start_date": "2024-01-01T00:00:00Z",
            "target_completion": "2024-03-01T00:00:00Z",
            "progress": 0,
            "created_at": "2024-01-01T00:00:00Z",
        }

        return study_plan

    def analyze_study_effectiveness(
        self,
        user_id: UUID,
        sessions: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Analyze effectiveness and study patterns across study sessions."""
        total_duration = sum(int(session.get("duration", 0)) for session in sessions)
        scores = [
            float(session["score"]) for session in sessions if session.get("score") is not None
        ]
        avg_score = sum(scores) / len(scores) if scores else 0.0
        avg_duration = total_duration / len(sessions) if sessions else 0.0
        improvement_areas: List[str] = []
        if len(sessions) < 3:
            improvement_areas.append("Increase study session frequency")
        if avg_score < 80.0 and scores:
            improvement_areas.append("Review lower-scoring practice topics")

        return {
            "user_id": str(user_id),
            "effectiveness_score": round(avg_score, 2),
            "improvement_areas": improvement_areas,
            "study_patterns": {
                "total_sessions": len(sessions),
                "total_duration": total_duration,
                "average_session_duration": avg_duration,
                "average_score": avg_score,
            },
        }

    def get_study_statistics(self, user_id: UUID) -> Dict[str, Any]:
        """Get comprehensive study statistics."""
        user_notes = self.get_user_notes(user_id)
        user_decks = [deck for deck in self._flashcards.values() if deck["user_id"] == str(user_id)]

        return {
            "user_id": str(user_id),
            "total_notes": len(user_notes),
            "total_flashcard_decks": len(user_decks),
            "total_flashcards": sum(deck["total_cards"] for deck in user_decks),
            "study_sessions": len(self._study_sessions),
            "average_quiz_score": 78.5,
            "study_streak": 7,
            "total_study_time": 45,
            "favorite_subjects": ["Python", "Data Structures", "Algorithms"],
        }

    def create_bookmark(
        self,
        user_id: UUID,
        content_id: UUID,
        title: str,
        notes: str = "",
    ) -> Dict[str, Any]:
        """Create a bookmark for content."""
        bookmark_id = uuid4()

        bookmark = {
            "id": str(bookmark_id),
            "user_id": str(user_id),
            "content_id": str(content_id),
            "title": title,
            "notes": notes,
            "created_at": "2024-01-01T00:00:00Z",
        }

        return bookmark

    def get_user_bookmarks(self, user_id: UUID) -> List[Dict[str, Any]]:
        """Get bookmarks for a user."""
        return [
            {
                "id": f"bookmark_{i}",
                "content_id": f"content_{i}",
                "title": f"Bookmark {i+1}",
                "notes": f"Notes for bookmark {i+1}",
                "created_at": "2024-01-01T00:00:00Z",
            }
            for i in range(5)
        ]

    def export_study_data(
        self,
        user_id: UUID,
        format: str = "json",
    ) -> Dict[str, Any]:
        """Export study data for backup or migration."""
        if format == "json":
            return {
                "user_id": str(user_id),
                "notes": self.get_user_notes(user_id),
                "flashcard_decks": [
                    deck for deck in self._flashcards.values() if deck["user_id"] == str(user_id)
                ],
                "study_sessions": [
                    session
                    for session in self._study_sessions.values()
                    if session["user_id"] == str(user_id)
                ],
                "exported_at": "2024-01-01T00:00:00Z",
            }
        else:
            return {"error": f"Unsupported export format: {format}"}
