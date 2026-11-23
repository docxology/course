"""Exercise content review and quality checks with real lesson data."""

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from curriculum.content_generation.quality import ContentQualityService
from curriculum.content_generation.workflow import ContentWorkflowService
from curriculum.core.content import Content, ContentFormat, ContentType


def make_lesson(body: str | None) -> Content:
    return Content(
        title="Foundations",
        content_type=ContentType.LESSON,
        format=ContentFormat.MARKDOWN,
        author_id=uuid4(),
        content_body=body,
    )


@pytest.mark.parametrize("body", [None, "", "Short draft."])
def test_incomplete_lessons_receive_actionable_feedback(body: str | None) -> None:
    quality = ContentQualityService()
    lesson = make_lesson(body)
    result = quality.assess_content_quality(lesson)
    assert result["content_id"] == str(lesson.id)
    assert result["overall_score"] < 70
    assert result["breakdown"]["content_length"]["issues"]
    assert any("examples" in item.lower() for item in quality.suggest_quality_improvements(lesson))


def test_quality_checklist_distinguishes_completed_and_missing_items() -> None:
    quality = ContentQualityService()
    checklist = quality.create_quality_checklist("assessment", "introductory")
    lesson = make_lesson(
        "# Introduction\nObjective: Explain the concept.\n"
        "For example, compare these results. " * 25
        + "\n# Exercises\nPractice with the following quiz question.\n# Conclusion\nReview."
    )
    result = quality.validate_against_checklist(lesson, checklist)
    checked = {item["item"]: item["passed"] for item in result["checklist_results"]}
    assert checked["Includes practical examples"]
    assert checked["Questions are clear and unambiguous"]
    assert result["total_points"] == sum(item["points"] for item in checklist)
    assert result["earned_points"] > 0
    assert quality.validate_against_checklist(make_lesson(None), [])["score"] == 0

    report = quality.assess_content_quality(lesson)
    assert set(report["breakdown"]) == {
        "content_length",
        "structure",
        "readability",
        "technical_accuracy",
        "engagement",
    }
    assert quality.suggest_quality_improvements(lesson, target_score=0) == [
        "Content quality is already excellent"
    ]


def test_content_workflow_reports_progress_and_review_history() -> None:
    service = ContentWorkflowService()
    reviewer, author, lesson = uuid4(), uuid4(), uuid4()
    steps = [
        {
            "title": "Draft",
            "estimated_duration": 45,
            "started_at": datetime.now(timezone.utc).isoformat(),
        },
        {"title": "Review"},
    ]
    flow = service.create_content_workflow("Lesson", "Prepare a draft", "lesson", steps, [reviewer])
    flow_id = flow["id"]
    assert service.get_workflow_status(flow_id)["progress"] == 0
    assert "error" in service.get_workflow_status(uuid4())
    assert "error" in service.assign_workflow_step(flow_id, 2, author)
    assert service.assign_workflow_step(flow_id, 0, author)["assigned_to"] == str(author)

    completed = service.complete_workflow_step(flow_id, 0, author, "Draft ready")
    assert completed["completed_by"] == str(author)
    assert service.get_workflow_status(flow_id)["progress"] == 50

    review = service.submit_content_for_review(flow_id, lesson, author)
    assert review["reviewers"] == [str(reviewer)]
    for action, outcome in [
        ("needs_revision", "needs_revision"),
        ("reject", "rejected"),
        ("approve", "approved"),
    ]:
        result = service.submit_review(review["id"], reviewer, action, "Reviewed draft")
        assert result["status"] == outcome
    assert "error" in service.submit_review("missing", reviewer, "approve", "")

    report = service.generate_workflow_report(flow_id)
    assert report["metrics"]["completed_steps"] == 1
    assert report["metrics"]["estimated_total_time"] == 105
    assert len(report["reviews"][0]["reviews"]) == 3
    assert service.create_collaborative_workflow(flow_id, [author], {})["collaborators"] == [
        str(author)
    ]
    assert service.get_workflow_analytics()["total_workflows"] == 1
