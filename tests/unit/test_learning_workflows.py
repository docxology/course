"""Regression coverage for the in-process learning services."""

from uuid import UUID, uuid4

import pytest

from curriculum.integration.gamification import GamificationService
from curriculum.integration.integration import IntegrationService
from curriculum.learning.study_tools import StudyToolsService
from curriculum.orchestration import CurriculumOrchestrator


def test_study_records_are_scoped_to_the_learner() -> None:
    tools = StudyToolsService()
    user, other, lesson = uuid4(), uuid4(), uuid4()
    note = tools.create_note(user, lesson, "Definitions", "Review chapter one")
    tools.create_note(other, lesson, "Private notes", "Do not export")
    tools.create_note(user, uuid4(), "Another chapter", "Review later")
    assert tools.get_user_notes(user, lesson) == [note]

    cards = tools.generate_flashcards(lesson, count=24)["flashcards"]
    deck = tools.create_flashcard_deck(user, "Chapter one", "Definitions", cards)
    assert tools.get_flashcard_deck(UUID(deck["id"])) == deck
    assert "error" in tools.study_flashcards(deck["id"], other)
    assert tools.get_flashcard_deck("invalid") is None

    session = tools.study_flashcards(deck["id"], user)
    assert session["cards_studied"] == 20
    assert deck["correct_answers"] + deck["incorrect_answers"] == 20
    assert deck["last_studied"] == session["end_time"]

    export = tools.export_study_data(user)
    assert {entry["user_id"] for entry in export["notes"]} == {str(user)}
    assert export["flashcard_decks"] == [deck]
    assert export["study_sessions"] == [session]
    assert tools.get_study_statistics(user)["total_flashcards"] == 24
    assert "error" in tools.export_study_data(user, "unsupported")


def test_practice_quiz_keeps_best_attempt() -> None:
    tools = StudyToolsService()
    user, stranger = uuid4(), uuid4()
    quiz = tools.generate_practice_quiz(uuid4(), user, question_count=2)
    first, second = quiz["questions"]
    correct = {item["id"]: item["correct_answer"] for item in (first, second)}
    assert "error" in tools.submit_practice_quiz(quiz["id"], stranger, correct)
    assert tools.submit_practice_quiz(UUID(quiz["id"]), user, correct)["passed"]

    retry = tools.submit_practice_quiz(quiz["id"], user, {first["id"]: "Option A"})
    assert retry["score"] == 50
    assert not retry["passed"]
    assert retry["results"][1]["user_answer"] is None
    assert (quiz["attempts"], quiz["best_score"]) == (2, 100)


def test_study_plans_preserve_both_call_shapes() -> None:
    tools = StudyToolsService()
    user, course = uuid4(), uuid4()
    goals = ["Review summary", "Complete quiz"]
    general = tools.create_study_plan(user, goals, 4)
    course_plan = tools.create_study_plan(user, course, goals)
    assert general["course_id"] is None
    assert general["available_time"] == 4
    assert course_plan["course_id"] == str(course)
    assert course_plan["available_time"] == 10
    assert [item["goal"] for item in course_plan["milestones"]] == goals
    assert len(course_plan["weekly_schedule"]) == 7

    analysis = tools.analyze_study_effectiveness(
        user, [{"duration": 30, "score": 70}, {"duration": 20}]
    )
    assert analysis["study_patterns"]["average_session_duration"] == 25
    assert analysis["effectiveness_score"] == 70
    assert len(analysis["improvement_areas"]) == 2


@pytest.mark.parametrize(
    ("reason", "badge_id"),
    [
        ("lesson_completed", "first_steps"),
        ("quiz_perfect_score", "quiz_master"),
        ("study_streak", "streak_keeper"),
        ("participation", None),
    ],
)
def test_points_and_redemption(reason: str, badge_id: str | None) -> None:
    game = GamificationService()
    user = uuid4()
    earned = game.award_points(user, 100, reason)
    expected = [badge_id] if badge_id else []
    assert [badge["id"] for badge in earned["badges_earned"]] == expected
    assert game.redeem_reward(user, "reward", 101) == {"error": "Insufficient points"}
    assert game.redeem_reward(user, "reward", 70)["remaining_points"] == 30
    assert game.award_points(user, 5, "participation")["new_total"] == 35


@pytest.mark.parametrize(("progress", "rewards"), [(24.9, []), (25, [50]), (50, [50, 100])])
def test_gamification_milestone_boundaries(progress: float, rewards: list[int]) -> None:
    game = GamificationService()
    awards = game.check_milestone_achievement(uuid4(), uuid4(), progress)
    assert [award["reward_points"] for award in awards] == rewards


def test_lms_state_controls_sync_and_import() -> None:
    integration = IntegrationService()
    lesson = uuid4()
    grades = [{"student_id": "student", "assignment_id": "quiz", "score": 90}]
    assert "error" in integration.sync_content_to_lms("missing", [lesson])
    assert "error" in integration.sync_grades_to_lms("missing", grades)
    assert "error" in integration.import_content_from_lms("missing", "course", {})

    connection = integration.connect_lms("moodle", {}, {"auto_sync": True})
    published = integration.sync_content_to_lms(connection["id"], [lesson])
    assert published["sync_details"][0]["content_id"] == str(lesson)
    synced_grades = integration.sync_grades_to_lms(connection["id"], grades)
    assert synced_grades["sync_details"] == [{**grades[0], "lms_status": "synced"}]
    imported = integration.import_content_from_lms(connection["id"], "course", {})
    assert len(imported["imported_items"]) == imported["import_summary"]["lessons"]


@pytest.mark.parametrize(
    ("kind", "fragment"),
    [("iframe", 'width="400"'), ("oembed", "/oembed?url=/embed/"), ("lti", "not supported")],
)
def test_integration_embed_formats(kind: str, fragment: str) -> None:
    lesson = uuid4()
    embed = IntegrationService().create_content_embed(lesson, kind, {"width": 400})
    assert embed["content_id"] == str(lesson)
    assert fragment in embed["html"]


async def test_orchestrator_links_lessons_and_quizzes_to_the_course() -> None:
    orchestrator = CurriculumOrchestrator()
    result = await orchestrator.create_course_with_assessments(
        "Foundations", "Core concepts", uuid4(), ["Introduction"], ["Check understanding"]
    )
    course = result["course"]
    assert result["lessons"][0].parent_id == course.id
    assert result["quizzes"][0].content_id == course.id
    assert await orchestrator.create_accessible_learning_experience(uuid4(), {}) == {
        "error": "Content not found"
    }


async def test_orchestrator_carries_course_through_lms_setup() -> None:
    course = uuid4()
    result = await CurriculumOrchestrator().setup_lms_integration("moodle", {}, course)
    connection = result["lms_connection"]["id"]
    assert result["content_sync"]["sync_details"][0]["content_id"] == str(course)
    assert result["grade_sync"]["connection_id"] == connection


async def test_orchestrator_routes_badges_and_points_with_optional_course() -> None:
    orchestrator = CurriculumOrchestrator()
    user, course = uuid4(), uuid4()
    first = await orchestrator.award_gamification_points(user, "lesson_completed", {})
    second = await orchestrator.award_gamification_points(
        user, "quiz_perfect_score", {"course_id": str(course)}
    )
    assert first["points_awarded"]["new_total"] == 25
    assert first["milestone_achievements"] == []
    assert second["points_awarded"]["new_total"] == 50
    assert second["points_awarded"]["badges_earned"][0]["id"] == "quiz_master"


def test_tool_registration_supports_launch_and_health() -> None:
    integration = IntegrationService()
    user, lesson = uuid4(), uuid4()
    assert "error" in integration.create_lti_launch("missing", user, lesson, {})
    config = {"client_id": "quiz-client", "launch_url": "https://example.org/quiz"}
    tool = integration.register_external_tool("Practice quiz", "quiz", config)
    assert integration.get_external_tools()[0]["id"] == tool["id"]
    launch = integration.create_lti_launch(tool["id"], user, lesson, {})
    assert launch["launch_url"] == config["launch_url"]
    assert launch["lti_params"]["sub"] == str(user)
    api = integration.create_api_integration("Quiz service", "rest", config)
    assert integration.get_integration_health(api["id"])["status"] == "healthy"
    assert "error" in integration.get_integration_health("missing")


@pytest.mark.parametrize(
    ("operation", "expected_key"),
    [
        ("generate_comprehensive_analytics", "engagement_metrics"),
        ("setup_mobile_learning_environment", "offline_package"),
        ("export_complete_course_package", "course_export"),
    ],
)
async def test_orchestrator_combines_service_results(operation: str, expected_key: str) -> None:
    orchestrator = CurriculumOrchestrator()
    result = await getattr(orchestrator, operation)(user_id=uuid4(), course_id=uuid4())
    assert result[expected_key]
