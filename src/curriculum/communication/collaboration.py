"""Collaboration service for group projects and peer review."""

from typing import Dict, List, Optional, Any
from uuid import UUID

from curriculum.core.user import User


class CollaborationService:
    """Service for collaborative features."""

    def __init__(self) -> None:
        """Initialize collaboration service."""
        self._projects: dict[UUID, dict] = {}
        self._workspaces: dict[UUID, dict] = {}
        self._peer_reviews: dict[UUID, dict] = {}
        self._group_memberships: dict[str, List[str]] = {}

    def create_group_project(
        self,
        course_id: UUID,
        title: str,
        description: str,
        instructor_id: UUID,
        max_group_size: int = 5,
        due_date: str = "2024-02-01T23:59:59Z",
    ) -> Dict[str, Any]:
        """Create a group project."""
        project_id = UUID(f"project_{course_id}")

        project = {
            "id": str(project_id),
            "course_id": str(course_id),
            "title": title,
            "description": description,
            "instructor_id": str(instructor_id),
            "max_group_size": max_group_size,
            "min_group_size": 2,
            "due_date": due_date,
            "status": "active",  # active, completed, cancelled
            "groups": [],
            "requirements": [
                "Research phase",
                "Design phase",
                "Implementation phase",
                "Testing phase",
                "Presentation",
            ],
            "evaluation_criteria": [
                "Technical correctness",
                "Creativity and innovation",
                "Collaboration effectiveness",
                "Documentation quality",
                "Presentation skills",
            ],
            "created_at": "2024-01-01T00:00:00Z",
        }

        self._projects[project_id] = project
        return project

    def create_study_group(
        self,
        course_id: UUID,
        title: str,
        description: str,
        organizer_id: UUID,
        max_members: int = 8,
    ) -> Dict[str, Any]:
        """Create a study group."""
        group_id = UUID(f"group_{course_id}")

        study_group = {
            "id": str(group_id),
            "course_id": str(course_id),
            "title": title,
            "description": description,
            "organizer_id": str(organizer_id),
            "max_members": max_members,
            "current_members": 1,
            "member_ids": [str(organizer_id)],
            "is_open": True,
            "meeting_schedule": "Flexible",
            "communication_platform": "Discord",
            "study_goals": ["Complete course", "Prepare for exams", "Share knowledge"],
            "created_at": "2024-01-01T00:00:00Z",
        }

        return study_group

    def join_group(self, group_id: UUID, user_id: UUID) -> Dict[str, Any]:
        """Join a group."""
        # Find the group (could be project group or study group)
        group = None
        for project in self._projects.values():
            for g in project["groups"]:
                if g["id"] == str(group_id):
                    group = g
                    break

        if not group:
            return {"error": "Group not found"}

        if str(user_id) in group["member_ids"]:
            return {"error": "Already a member"}

        if len(group["member_ids"]) >= group.get("max_members", 10):
            return {"error": "Group is full"}

        group["member_ids"].append(str(user_id))
        group["current_members"] = len(group["member_ids"])

        return {"message": "Joined group successfully"}

    def create_workspace(
        self,
        group_id: UUID,
        name: str,
        description: str,
        tools: List[str] = None,
    ) -> Dict[str, Any]:
        """Create a collaborative workspace."""
        workspace_id = UUID(f"workspace_{group_id}")

        workspace = {
            "id": str(workspace_id),
            "group_id": str(group_id),
            "name": name,
            "description": description,
            "tools": tools or ["documents", "whiteboard", "chat", "tasks"],
            "files": [],
            "members": [],  # Would get from group members
            "is_public": False,
            "created_at": "2024-01-01T00:00:00Z",
        }

        self._workspaces[workspace_id] = workspace
        return workspace

    def create_peer_review_assignment(
        self,
        course_id: UUID,
        title: str,
        description: str,
        instructor_id: UUID,
        submission_deadline: str,
        review_deadline: str,
    ) -> Dict[str, Any]:
        """Create a peer review assignment."""
        assignment_id = UUID(f"peer_review_{course_id}")

        assignment = {
            "id": str(assignment_id),
            "course_id": str(course_id),
            "title": title,
            "description": description,
            "instructor_id": str(instructor_id),
            "submission_deadline": submission_deadline,
            "review_deadline": review_deadline,
            "review_criteria": [
                "Content quality",
                "Clarity of presentation",
                "Technical accuracy",
                "Creativity",
                "Overall impact",
            ],
            "reviewer_count": 3,  # Number of reviewers per submission
            "is_anonymous": True,
            "submissions": [],
            "reviews": [],
            "created_at": "2024-01-01T00:00:00Z",
        }

        return assignment

    def submit_for_review(
        self,
        assignment_id: UUID,
        user_id: UUID,
        submission_title: str,
        submission_content: str,
        files: List[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Submit work for peer review."""
        assignment = self._peer_reviews.get(assignment_id)
        if not assignment:
            return {"error": "Assignment not found"}

        submission_id = UUID(f"submission_{len(assignment['submissions'])}")

        submission = {
            "id": str(submission_id),
            "assignment_id": str(assignment_id),
            "user_id": str(user_id),
            "title": submission_title,
            "content": submission_content,
            "files": files or [],
            "submitted_at": "2024-01-01T00:00:00Z",
            "status": "pending_review",
            "reviews": [],
            "average_score": None,
        }

        assignment["submissions"].append(submission)
        return submission

    def submit_review(
        self,
        submission_id: UUID,
        reviewer_id: UUID,
        scores: Dict[str, float],
        feedback: str,
        is_anonymous: bool = True,
    ) -> Dict[str, Any]:
        """Submit a peer review."""
        # Find the submission
        submission = None
        assignment = None

        for assignment_data in self._peer_reviews.values():
            for sub in assignment_data["submissions"]:
                if sub["id"] == str(submission_id):
                    submission = sub
                    assignment = assignment_data
                    break

        if not submission:
            return {"error": "Submission not found"}

        review_id = UUID(f"review_{len(assignment['reviews'])}")

        review = {
            "id": str(review_id),
            "submission_id": str(submission_id),
            "reviewer_id": str(reviewer_id),
            "scores": scores,
            "feedback": feedback,
            "is_anonymous": is_anonymous,
            "submitted_at": "2024-01-01T00:00:00Z",
        }

        submission["reviews"].append(review)
        assignment["reviews"].append(review)

        # Calculate average score if all reviews are in
        if len(submission["reviews"]) >= assignment["reviewer_count"]:
            total_score = sum(
                sum(r["scores"].values()) for r in submission["reviews"]
            )
            max_score = len(submission["reviews"]) * len(scores) * 5  # Assuming 5-point scale
            submission["average_score"] = total_score / max_score * 100

        return review

    def get_group_projects(self, course_id: UUID) -> List[Dict[str, Any]]:
        """Get group projects for a course."""
        return [
            project for project in self._projects.values()
            if project["course_id"] == str(course_id)
        ]

    def get_user_groups(self, user_id: UUID) -> List[Dict[str, Any]]:
        """Get groups a user is a member of."""
        user_groups = []

        # Check project groups
        for project in self._projects.values():
            for group in project["groups"]:
                if str(user_id) in group["member_ids"]:
                    user_groups.append({
                        "id": group["id"],
                        "title": group["title"],
                        "type": "project",
                        "role": "member",
                    })

        return user_groups

    def assign_group_roles(
        self,
        group_id: UUID,
        role_assignments: Dict[str, str],
    ) -> Dict[str, Any]:
        """Assign roles within a group."""
        # Find the group
        group = None
        for project in self._projects.values():
            for g in project["groups"]:
                if g["id"] == str(group_id):
                    group = g
                    break

        if not group:
            return {"error": "Group not found"}

        group["roles"] = role_assignments

        return {"message": "Roles assigned successfully"}

    def create_collaboration_task(
        self,
        workspace_id: UUID,
        title: str,
        description: str,
        assignee_id: UUID,
        due_date: str,
    ) -> Dict[str, Any]:
        """Create a task in a collaborative workspace."""
        task_id = UUID(f"task_{workspace_id}")

        task = {
            "id": str(task_id),
            "workspace_id": str(workspace_id),
            "title": title,
            "description": description,
            "assignee_id": str(assignee_id),
            "status": "pending",  # pending, in_progress, completed, cancelled
            "priority": "medium",  # low, medium, high
            "due_date": due_date,
            "created_at": "2024-01-01T00:00:00Z",
            "comments": [],
        }

        return task

    def get_collaboration_statistics(self, course_id: UUID) -> Dict[str, Any]:
        """Get collaboration statistics for a course."""
        projects = self.get_group_projects(course_id)
        total_groups = sum(len(project["groups"]) for project in projects)

        return {
            "course_id": str(course_id),
            "total_projects": len(projects),
            "total_groups": total_groups,
            "average_group_size": 4.2,  # Mock average
            "completed_projects": len([
                p for p in projects if p["status"] == "completed"
            ]),
            "active_collaborations": total_groups * 0.8,  # Mock active percentage
            "peer_reviews_completed": len([
                r for a in self._peer_reviews.values()
                for r in a["reviews"]
                if a["course_id"] == str(course_id)
            ]),
        }

    def create_shared_document(
        self,
        workspace_id: UUID,
        title: str,
        content: str,
        author_id: UUID,
    ) -> Dict[str, Any]:
        """Create a shared document in a workspace."""
        doc_id = UUID(f"doc_{workspace_id}")

        document = {
            "id": str(doc_id),
            "workspace_id": str(workspace_id),
            "title": title,
            "content": content,
            "author_id": str(author_id),
            "is_locked": False,
            "editors": [str(author_id)],
            "viewers": [],
            "version": 1,
            "created_at": "2024-01-01T00:00:00Z",
            "last_edited": "2024-01-01T00:00:00Z",
        }

        return document

    def add_collaborator(
        self,
        document_id: UUID,
        user_id: UUID,
        permission: str = "edit",  # view, edit, admin
    ) -> Dict[str, Any]:
        """Add a collaborator to a document."""
        # Find document
        document = None
        for workspace in self._workspaces.values():
            for file in workspace["files"]:
                if file["id"] == str(document_id) and file["type"] == "document":
                    document = file
                    break

        if not document:
            return {"error": "Document not found"}

        if permission == "edit":
            if str(user_id) not in document["editors"]:
                document["editors"].append(str(user_id))
        elif permission == "view":
            if str(user_id) not in document["viewers"]:
                document["viewers"].append(str(user_id))

        return {"message": "Collaborator added successfully"}

    def get_collaboration_activity(
        self,
        course_id: UUID,
        days: int = 7,
    ) -> List[Dict[str, Any]]:
        """Get recent collaboration activity."""
        # Mock activity data
        return [
            {
                "id": f"activity_{i}",
                "type": "document_edit",
                "user_id": f"user_{i}",
                "description": f"Edited document {i+1}",
                "timestamp": "2024-01-01T00:00:00Z",
            }
            for i in range(10)  # Mock recent activities
        ]
