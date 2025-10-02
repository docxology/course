"""Content workflow service for managing content creation processes."""

from typing import Dict, List, Optional, Any
from uuid import UUID
from datetime import datetime, timedelta

from curriculum.core.content import Content, ContentStatus
from curriculum.core.user import User


class ContentWorkflowService:
    """Service for managing content creation workflows."""

    def __init__(self) -> None:
        """Initialize content workflow service."""
        self._workflows: Dict[UUID, Dict[str, Any]] = {}
        self._workflow_steps: Dict[UUID, List[Dict[str, Any]]] = {}
        self._content_reviews: Dict[UUID, List[Dict[str, Any]]] = {}

    def create_content_workflow(
        self,
        title: str,
        description: str,
        content_type: str,
        steps: List[Dict[str, Any]],
        assigned_users: List[UUID],
    ) -> Dict[str, Any]:
        """Create a new content creation workflow."""
        workflow_id = f"workflow_{len(self._workflows)}"

        workflow = {
            "id": workflow_id,
            "title": title,
            "description": description,
            "content_type": content_type,
            "steps": steps,
            "assigned_users": [str(uid) for uid in assigned_users],
            "status": "active",
            "created_at": datetime.utcnow().isoformat(),
            "deadline": (datetime.utcnow() + timedelta(days=14)).isoformat(),
            "progress": 0,  # percentage
            "current_step": 0,
        }

        self._workflows[workflow_id] = workflow
        self._workflow_steps[workflow_id] = steps

        return workflow

    def get_workflow_status(self, workflow_id: UUID) -> Dict[str, Any]:
        """Get current status of a workflow."""
        workflow = self._workflows.get(workflow_id)
        if not workflow:
            return {"error": "Workflow not found"}

        steps = self._workflow_steps.get(workflow_id, [])
        completed_steps = sum(1 for step in steps if step.get("status") == "completed")

        workflow["progress"] = (completed_steps / len(steps)) * 100 if steps else 0

        return workflow

    def assign_workflow_step(
        self,
        workflow_id: UUID,
        step_index: int,
        assigned_user_id: UUID,
    ) -> Dict[str, Any]:
        """Assign a workflow step to a user."""
        workflow = self._workflows.get(workflow_id)
        if not workflow:
            return {"error": "Workflow not found"}

        steps = self._workflow_steps.get(workflow_id, [])
        if step_index >= len(steps):
            return {"error": "Invalid step index"}

        steps[step_index]["assigned_to"] = str(assigned_user_id)
        steps[step_index]["assigned_at"] = datetime.utcnow().isoformat()
        steps[step_index]["status"] = "assigned"

        return steps[step_index]

    def complete_workflow_step(
        self,
        workflow_id: UUID,
        step_index: int,
        completed_by: UUID,
        notes: str = "",
    ) -> Dict[str, Any]:
        """Mark a workflow step as completed."""
        workflow = self._workflows.get(workflow_id)
        if not workflow:
            return {"error": "Workflow not found"}

        steps = self._workflow_steps.get(workflow_id, [])
        if step_index >= len(steps):
            return {"error": "Invalid step index"}

        step = steps[step_index]
        step["status"] = "completed"
        step["completed_by"] = str(completed_by)
        step["completed_at"] = datetime.utcnow().isoformat()
        step["notes"] = notes

        # Update workflow progress
        completed_steps = sum(1 for s in steps if s.get("status") == "completed")
        workflow["progress"] = (completed_steps / len(steps)) * 100 if steps else 0
        workflow["current_step"] = min(step_index + 1, len(steps) - 1)

        return step

    def submit_content_for_review(
        self,
        workflow_id: UUID,
        content_id: UUID,
        submitted_by: UUID,
        review_type: str = "internal",
    ) -> Dict[str, Any]:
        """Submit content for review in the workflow."""
        workflow = self._workflows.get(workflow_id)
        if not workflow:
            return {"error": "Workflow not found"}

        review = {
            "id": f"review_{content_id}",
            "workflow_id": str(workflow_id),
            "content_id": str(content_id),
            "submitted_by": str(submitted_by),
            "review_type": review_type,
            "status": "pending",
            "submitted_at": datetime.utcnow().isoformat(),
            "reviewers": workflow["assigned_users"],
            "reviews": [],
        }

        if workflow_id not in self._content_reviews:
            self._content_reviews[workflow_id] = []

        self._content_reviews[workflow_id].append(review)

        return review

    def submit_review(
        self,
        review_id: str,
        reviewer_id: UUID,
        decision: str,  # approve, reject, needs_revision
        feedback: str,
        score: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Submit a review for content."""
        # Find the review
        review = None
        for workflow_reviews in self._content_reviews.values():
            for r in workflow_reviews:
                if r["id"] == review_id:
                    review = r
                    break

        if not review:
            return {"error": "Review not found"}

        review_entry = {
            "reviewer_id": str(reviewer_id),
            "decision": decision,
            "feedback": feedback,
            "score": score,
            "reviewed_at": datetime.utcnow().isoformat(),
        }

        review["reviews"].append(review_entry)

        # Update review status
        if decision == "approve":
            review["status"] = "approved"
        elif decision == "reject":
            review["status"] = "rejected"
        else:
            review["status"] = "needs_revision"

        return review

    def get_workflow_timeline(self, workflow_id: UUID) -> List[Dict[str, Any]]:
        """Get timeline of workflow events."""
        workflow = self._workflows.get(workflow_id)
        if not workflow:
            return []

        steps = self._workflow_steps.get(workflow_id, [])
        timeline = []

        for i, step in enumerate(steps):
            timeline.append({
                "step": i + 1,
                "title": step.get("title", f"Step {i+1}"),
                "status": step.get("status", "pending"),
                "assigned_to": step.get("assigned_to"),
                "started_at": step.get("started_at"),
                "completed_at": step.get("completed_at"),
                "notes": step.get("notes", ""),
            })

        return timeline

    def create_workflow_template(
        self,
        name: str,
        description: str,
        default_steps: List[Dict[str, Any]],
        category: str = "general",
    ) -> Dict[str, Any]:
        """Create a reusable workflow template."""
        template_id = f"template_{len(self._workflows)}"

        template = {
            "id": template_id,
            "name": name,
            "description": description,
            "category": category,
            "default_steps": default_steps,
            "estimated_duration": sum(step.get("estimated_duration", 60) for step in default_steps),
            "required_roles": ["content_creator", "reviewer", "editor"],
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
        }

        return template

    def get_workflow_templates(self) -> List[Dict[str, Any]]:
        """Get available workflow templates."""
        # Mock templates - in production, these would be stored in database
        return [
            {
                "id": "template_1",
                "name": "Standard Lesson Creation",
                "description": "Complete workflow for creating educational lessons",
                "category": "content",
                "estimated_duration": 240,  # minutes
                "steps": 5,
            },
            {
                "id": "template_2",
                "name": "Assessment Development",
                "description": "Workflow for creating quizzes and exams",
                "category": "assessment",
                "estimated_duration": 180,
                "steps": 4,
            },
            {
                "id": "template_3",
                "name": "Course Material Review",
                "description": "Review workflow for course materials",
                "category": "review",
                "estimated_duration": 120,
                "steps": 3,
            },
        ]

    def track_workflow_metrics(
        self,
        workflow_id: UUID,
    ) -> Dict[str, Any]:
        """Track metrics for workflow performance."""
        workflow = self._workflows.get(workflow_id)
        if not workflow:
            return {"error": "Workflow not found"}

        steps = self._workflow_steps.get(workflow_id, [])
        completed_steps = [s for s in steps if s.get("status") == "completed"]

        total_estimated_time = sum(s.get("estimated_duration", 60) for s in steps)
        actual_time = sum(
            (datetime.fromisoformat(s.get("completed_at", "")) - datetime.fromisoformat(s.get("started_at", ""))).total_seconds() / 60
            for s in completed_steps
            if s.get("started_at") and s.get("completed_at")
        )

        return {
            "workflow_id": str(workflow_id),
            "total_steps": len(steps),
            "completed_steps": len(completed_steps),
            "progress": workflow["progress"],
            "estimated_total_time": total_estimated_time,
            "actual_time_spent": actual_time,
            "efficiency": (total_estimated_time / max(actual_time, 1)) * 100,
            "bottlenecks": self._identify_bottlenecks(steps),
            "average_step_completion_time": actual_time / len(completed_steps) if completed_steps else 0,
        }

    def _identify_bottlenecks(self, steps: List[Dict[str, Any]]) -> List[str]:
        """Identify bottlenecks in workflow steps."""
        bottlenecks = []

        for step in steps:
            if step.get("status") == "in_progress":
                duration = 0
                if step.get("started_at"):
                    start_time = datetime.fromisoformat(step["started_at"])
                    duration = (datetime.utcnow() - start_time).total_seconds() / 3600  # hours

                if duration > 24:  # More than 24 hours
                    bottlenecks.append(f"Step '{step.get('title', 'Unknown')}' has been in progress for {duration:.1f} hours")

        return bottlenecks

    def create_collaborative_workflow(
        self,
        workflow_id: UUID,
        collaborators: List[UUID],
        permissions: Dict[str, str],
    ) -> Dict[str, Any]:
        """Create a collaborative workflow with multiple contributors."""
        workflow = self._workflows.get(workflow_id)
        if not workflow:
            return {"error": "Workflow not found"}

        workflow["collaborators"] = [str(uid) for uid in collaborators]
        workflow["permissions"] = permissions
        workflow["collaboration_features"] = [
            "real_time_editing",
            "comment_system",
            "version_control",
            "notification_system",
        ]

        return workflow

    def generate_workflow_report(
        self,
        workflow_id: UUID,
        report_type: str = "comprehensive",
    ) -> Dict[str, Any]:
        """Generate a comprehensive workflow report."""
        workflow = self._workflows.get(workflow_id)
        if not workflow:
            return {"error": "Workflow not found"}

        if report_type == "comprehensive":
            report = {
                "workflow_id": str(workflow_id),
                "title": workflow["title"],
                "status": workflow["status"],
                "progress": workflow["progress"],
                "timeline": self.get_workflow_timeline(workflow_id),
                "metrics": self.track_workflow_metrics(workflow_id),
                "participants": workflow.get("assigned_users", []),
                "reviews": self._content_reviews.get(workflow_id, []),
                "generated_at": datetime.utcnow().isoformat(),
            }

        return report

    def get_workflow_analytics(self) -> Dict[str, Any]:
        """Get analytics across all workflows."""
        total_workflows = len(self._workflows)
        completed_workflows = sum(1 for w in self._workflows.values() if w["progress"] == 100)

        return {
            "total_workflows": total_workflows,
            "active_workflows": total_workflows - completed_workflows,
            "completed_workflows": completed_workflows,
            "average_completion_time": 168,  # hours (1 week)
            "average_progress": sum(w["progress"] for w in self._workflows.values()) / total_workflows if total_workflows > 0 else 0,
            "most_common_bottlenecks": [
                "Content review delays",
                "Technical implementation issues",
                "Resource availability",
            ],
            "team_performance": {
                "average_steps_per_workflow": 5.2,
                "average_collaborators": 3.1,
                "review_approval_rate": 0.87,
            },
        }

    def create_approval_workflow(
        self,
        content_id: UUID,
        approval_chain: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Create an approval workflow for content."""
        approval_id = f"approval_{content_id}"

        approval_workflow = {
            "id": approval_id,
            "content_id": str(content_id),
            "approval_chain": approval_chain,
            "current_approver": 0,
            "status": "pending",
            "approvals": [],
            "rejections": [],
            "created_at": datetime.utcnow().isoformat(),
        }

        return approval_workflow

    def submit_for_approval(
        self,
        approval_id: str,
        approver_id: UUID,
        decision: str,  # approve, reject, request_changes
        comments: str = "",
    ) -> Dict[str, Any]:
        """Submit approval decision."""
        # Find approval workflow
        approval_workflow = None
        for workflow in self._workflows.values():
            if workflow.get("approval_id") == approval_id:
                approval_workflow = workflow
                break

        if not approval_workflow:
            return {"error": "Approval workflow not found"}

        approval_entry = {
            "approver_id": str(approver_id),
            "decision": decision,
            "comments": comments,
            "submitted_at": datetime.utcnow().isoformat(),
        }

        if decision == "approve":
            approval_workflow["approvals"].append(approval_entry)
        elif decision == "reject":
            approval_workflow["rejections"].append(approval_entry)
        else:
            approval_workflow["change_requests"].append(approval_entry)

        # Update status
        if len(approval_workflow["approvals"]) >= len(approval_workflow["approval_chain"]):
            approval_workflow["status"] = "approved"
        elif approval_workflow["rejections"]:
            approval_workflow["status"] = "rejected"

        return approval_entry

    def get_pending_approvals(self, user_id: UUID) -> List[Dict[str, Any]]:
        """Get pending approvals for a user."""
        # Mock pending approvals
        return [
            {
                "id": f"approval_{i}",
                "content_title": f"Content {i+1}",
                "content_type": "lesson",
                "submitted_by": f"user_{i}",
                "submitted_at": "2024-01-20T10:00:00Z",
                "priority": "normal",
                "days_pending": 2,
            }
            for i in range(3)
        ]

    def create_revision_request(
        self,
        workflow_id: UUID,
        reviewer_id: UUID,
        revision_notes: str,
        priority: str = "medium",
    ) -> Dict[str, Any]:
        """Create a revision request for content."""
        revision_id = f"revision_{len(self._content_reviews.get(workflow_id, []))}"

        revision = {
            "id": revision_id,
            "workflow_id": str(workflow_id),
            "reviewer_id": str(reviewer_id),
            "revision_notes": revision_notes,
            "priority": priority,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "deadline": (datetime.utcnow() + timedelta(days=7)).isoformat(),
        }

        return revision
