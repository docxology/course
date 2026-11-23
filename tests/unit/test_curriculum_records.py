"""Regression tests for metadata, version history, and teacher records."""

from uuid import uuid4

import pytest

from curriculum.content.metadata import MetadataService
from curriculum.content.version_control import VersionControlService
from curriculum.core.content import Content, ContentFormat, ContentType
from curriculum.core.metadata import EducationalUse, LearningResourceType
from curriculum.teachers.student_management import StudentManagementService


def test_learning_metadata_updates_are_scoped_to_existing_records() -> None:
    service = MetadataService()
    lesson, missing = uuid4(), uuid4()
    metadata = service.create_metadata(lesson, "Introduction")
    assert service.get_metadata_by_content(lesson) == metadata
    assert service.get_metadata_by_content(missing) is None
    assert service.update_dublin_core(missing, title="Missing") is None
    assert service.add_lrmi_metadata(missing, time_required=20) is None
    assert service.add_custom_field(missing, "chapter", "1") is None

    updated = service.update_dublin_core(
        metadata.id,
        title="Revised",
        description="Overview",
        creators=["Instructor"],
        subjects=["Logic"],
    )
    assert updated.dublin_core.title == "Revised"
    assert updated.dublin_core.creator == ["Instructor"]
    assert updated.dublin_core.subject == ["Logic"]
    use = next(iter(EducationalUse))
    resource = next(iter(LearningResourceType))
    updated = service.add_lrmi_metadata(metadata.id, [use.value], [resource], 20)
    assert updated.lrmi.educational_use == [use]
    assert updated.lrmi.learning_resource_type == [resource]
    assert updated.lrmi.time_required == 20
    assert service.add_custom_field(metadata.id, "chapter", "1").custom_fields == {"chapter": "1"}


def test_tags_and_taxonomy_preserve_identity_and_order() -> None:
    service = MetadataService()
    tag = service.create_or_get_tag("Course Design")
    assert service.create_or_get_tag("course design").id == tag.id
    assert service.get_tag_by_name("COURSE DESIGN") == tag
    assert service.get_tag_by_name("Missing") is None
    assert service.get_tag(tag.id) == tag
    service.create_or_get_tag("Assessment")
    service.increment_tag_usage("Course Design")
    assert service.get_popular_tags(limit=1) == [tag]
    assert len(service.get_all_tags()) == 2

    parent = service.create_taxonomy("Teaching", "teaching")
    child = service.create_taxonomy("Assessment", "teaching/assessment", parent.id, 1)
    service.create_taxonomy("Unrelated", "unrelated")
    assert service.get_taxonomy(child.id) == child
    assert service.get_taxonomy_children(parent.id) == [child]


def test_version_history_compares_and_restores_only_the_correct_content() -> None:
    service = VersionControlService()
    content = Content(
        title="Draft",
        description="Original",
        content_type=ContentType.LESSON,
        format=ContentFormat.MARKDOWN,
        author_id=uuid4(),
        content_body="Original body",
    )
    assert service.get_latest_version(content.id) is None
    original = service.create_version(content)
    content.title = "Revised"
    content.description = "Revised description"
    content.content_body = "Revised body"
    revision = service.create_version(content, "Clarify scope")
    assert service.get_latest_version(content.id) == revision
    assert service.get_version_count(content.id) == 2
    assert {
        item["field"] for item in service.compare_versions(original.id, revision.id)["differences"]
    } == {"title", "description", "content_body"}
    assert service.compare_versions(original.id, original.id)["is_identical"]
    assert service.compare_versions(original.id, uuid4()) is None
    unrelated = content.model_copy(update={"id": uuid4()})
    assert service.restore_version(unrelated, original.id) is None
    assert service.restore_version(content, original.id).content_body == "Original body"
    assert not service.delete_version(uuid4())
    assert service.delete_version(revision.id)
    assert service.get_version(revision.id).is_deleted


@pytest.mark.parametrize(
    ("part", "expected"), [("major", "2.0.0"), ("minor", "1.3.0"), ("patch", "1.2.4")]
)
def test_version_number_increments(part: str, expected: str) -> None:
    assert VersionControlService().increment_version("1.2.3", part) == expected


def test_student_records_are_scoped_by_course_and_teacher() -> None:
    service = StudentManagementService()
    teacher, another_teacher, student, course, another_course = (uuid4() for _ in range(5))
    assert service.get_class_analytics(teacher, course)["class_size"] == 0
    service.enroll_student(teacher, course, student)
    service.enroll_student(teacher, course, student)
    assert service.get_class_analytics(teacher, course)["class_size"] == 1

    service.update_student_grade(teacher, course, student, "quiz", 80, "Good work")
    grade = service.get_student_grades(teacher, course, student)["grades"]["quiz"]
    assert (grade["grade"], grade["graded_by"]) == (80, str(teacher))
    assert service.get_student_grades(teacher, another_course, student)["grades"] == {}

    note = service.add_student_note(teacher, student, "Follow up next week")
    service.add_student_note(teacher, uuid4(), "Another student")
    assert note["is_private"]
    assert service.get_student_notes(teacher, student) == [note]
    assert service.get_student_notes(another_teacher, student) == []
    assert service.get_students_needing_help(teacher, course, {"low_attendance": True}) == []
    assert service.generate_student_report(teacher, course, student)["student_id"] == str(student)
    service.unenroll_student(teacher, course, student)
    assert service.get_course_roster(teacher, course) == []
