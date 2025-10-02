"""Gamification service for points, badges, and leaderboards."""

from typing import Dict, List, Optional, Any
from uuid import UUID
from collections import defaultdict

from curriculum.core.user import User


class GamificationService:
    """Service for gamification features."""

    def __init__(self) -> None:
        """Initialize gamification service."""
        self._user_points: dict[UUID, int] = {}
        self._badges: dict[UUID, dict] = {}
        self._achievements: dict[str, dict] = {}
        self._leaderboards: dict[str, List[Dict[str, Any]]] = {}

        # Initialize default badges
        self._initialize_badges()

    def _initialize_badges(self) -> None:
        """Initialize default badge definitions."""
        self._badges = {
            "first_steps": {
                "id": "first_steps",
                "name": "First Steps",
                "description": "Complete your first lesson",
                "icon": "🚀",
                "category": "progression",
                "rarity": "common",
                "points": 10,
            },
            "quiz_master": {
                "id": "quiz_master",
                "name": "Quiz Master",
                "description": "Score 100% on a quiz",
                "icon": "🏆",
                "category": "achievement",
                "rarity": "rare",
                "points": 50,
            },
            "streak_keeper": {
                "id": "streak_keeper",
                "name": "Streak Keeper",
                "description": "Study for 7 days in a row",
                "icon": "🔥",
                "category": "consistency",
                "rarity": "uncommon",
                "points": 75,
            },
            "early_bird": {
                "id": "early_bird",
                "name": "Early Bird",
                "description": "Complete assignments before deadline",
                "icon": "🌅",
                "category": "productivity",
                "rarity": "common",
                "points": 25,
            },
            "collaborator": {
                "id": "collaborator",
                "name": "Collaborator",
                "description": "Help 5 other students",
                "icon": "🤝",
                "category": "social",
                "rarity": "rare",
                "points": 100,
            },
        }

    def award_points(
        self,
        user_id: UUID,
        points: int,
        reason: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Award points to a user."""
        current_points = self._user_points.get(user_id, 0)
        new_total = current_points + points

        self._user_points[user_id] = new_total

        # Check for badge eligibility
        badges_earned = self._check_badge_eligibility(user_id, reason)

        return {
            "user_id": str(user_id),
            "points_awarded": points,
            "new_total": new_total,
            "reason": reason,
            "badges_earned": badges_earned,
            "metadata": metadata or {},
            "awarded_at": "2024-01-01T00:00:00Z",
        }

    def _check_badge_eligibility(self, user_id: UUID, reason: str) -> List[Dict[str, Any]]:
        """Check if user is eligible for any badges."""
        badges_earned = []

        # Mock badge checking logic based on reason
        if reason == "lesson_completed":
            badge = self._badges.get("first_steps")
            if badge:
                badges_earned.append(badge)

        elif reason == "quiz_perfect_score":
            badge = self._badges.get("quiz_master")
            if badge:
                badges_earned.append(badge)

        elif reason == "study_streak":
            badge = self._badges.get("streak_keeper")
            if badge:
                badges_earned.append(badge)

        return badges_earned

    def get_user_badges(self, user_id: UUID) -> List[Dict[str, Any]]:
        """Get badges earned by a user."""
        # In production, this would query a user_badges table
        return [
            {
                "badge_id": "first_steps",
                "earned_at": "2024-01-01T00:00:00Z",
                "progress": 100,
            },
            {
                "badge_id": "quiz_master",
                "earned_at": "2024-01-02T00:00:00Z",
                "progress": 100,
            },
        ]

    def create_custom_badge(
        self,
        course_id: UUID,
        name: str,
        description: str,
        icon: str,
        criteria: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create a custom badge for a course."""
        badge_id = UUID(f"custom_{len(self._badges)}")

        badge = {
            "id": str(badge_id),
            "course_id": str(course_id),
            "name": name,
            "description": description,
            "icon": icon,
            "criteria": criteria,
            "category": "custom",
            "rarity": "uncommon",
            "points": 50,
            "is_active": True,
            "created_at": "2024-01-01T00:00:00Z",
        }

        self._badges[badge_id] = badge
        return badge

    def get_leaderboard(
        self,
        category: str = "points",
        timeframe: str = "all_time",
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get leaderboard for specified category."""
        # Mock leaderboard data
        if category == "points":
            return [
                {
                    "rank": i + 1,
                    "user_id": f"user_{i}",
                    "user_name": f"Student {i+1}",
                    "points": 1000 - (i * 50),
                    "badges": 5 - i if i < 5 else 0,
                }
                for i in range(min(limit, 10))
            ]
        elif category == "streaks":
            return [
                {
                    "rank": i + 1,
                    "user_id": f"user_{i}",
                    "user_name": f"Student {i+1}",
                    "current_streak": 14 - i,
                    "longest_streak": 21 - i,
                }
                for i in range(min(limit, 8))
            ]
        else:
            return []

    def create_achievement(
        self,
        user_id: UUID,
        achievement_type: str,
        title: str,
        description: str,
        points: int = 0,
    ) -> Dict[str, Any]:
        """Create a custom achievement."""
        achievement_id = f"achievement_{len(self._achievements)}"

        achievement = {
            "id": achievement_id,
            "user_id": str(user_id),
            "type": achievement_type,
            "title": title,
            "description": description,
            "points": points,
            "is_public": False,
            "created_at": "2024-01-01T00:00:00Z",
        }

        self._achievements[achievement_id] = achievement
        return achievement

    def get_user_achievements(self, user_id: UUID) -> List[Dict[str, Any]]:
        """Get achievements for a user."""
        return [
            achievement for achievement in self._achievements.values()
            if achievement["user_id"] == str(user_id)
        ]

    def create_level_system(
        self,
        course_id: UUID,
        levels: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Create a leveling system for a course."""
        level_system = {
            "course_id": str(course_id),
            "levels": levels,
            "current_level": 1,
            "experience_points": 0,
            "points_to_next_level": levels[1]["min_points"] if len(levels) > 1 else 0,
        }

        return level_system

    def calculate_level_progress(self, user_id: UUID, course_id: UUID) -> Dict[str, Any]:
        """Calculate user's level progress."""
        # Mock level calculation
        return {
            "user_id": str(user_id),
            "course_id": str(course_id),
            "current_level": 3,
            "current_points": 2450,
            "points_to_next_level": 550,
            "level_progress": 81.7,  # percentage
            "total_levels": 10,
        }

    def create_challenge(
        self,
        course_id: UUID,
        title: str,
        description: str,
        challenge_type: str,  # daily, weekly, monthly, special
        rewards: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create a challenge for students."""
        challenge_id = UUID(f"challenge_{challenge_type}")

        challenge = {
            "id": str(challenge_id),
            "course_id": str(course_id),
            "title": title,
            "description": description,
            "type": challenge_type,
            "start_date": "2024-01-01T00:00:00Z",
            "end_date": "2024-01-07T23:59:59Z",
            "rewards": rewards,
            "participants": 0,
            "completed": 0,
            "is_active": True,
        }

        return challenge

    def join_challenge(self, challenge_id: UUID, user_id: UUID) -> Dict[str, Any]:
        """Join a challenge."""
        # Mock challenge joining
        return {
            "challenge_id": str(challenge_id),
            "user_id": str(user_id),
            "joined_at": "2024-01-01T00:00:00Z",
            "progress": 0,
        }

    def get_gamification_statistics(self, course_id: UUID) -> Dict[str, Any]:
        """Get gamification statistics for a course."""
        return {
            "course_id": str(course_id),
            "total_participants": 150,
            "active_gamification_users": 120,
            "total_points_awarded": 45000,
            "badges_earned": 340,
            "challenges_completed": 45,
            "average_engagement_score": 78,
            "top_gamification_features": [
                "points_system",
                "badges",
                "leaderboards",
                "challenges",
            ],
        }

    def create_reward_system(
        self,
        course_id: UUID,
        reward_types: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Create a reward system for the course."""
        reward_system = {
            "course_id": str(course_id),
            "reward_types": reward_types,
            "redemption_rules": {
                "minimum_points": 100,
                "daily_limit": 5,
                "weekly_limit": 20,
            },
            "is_active": True,
        }

        return reward_system

    def redeem_reward(
        self,
        user_id: UUID,
        reward_id: str,
        points_cost: int,
    ) -> Dict[str, Any]:
        """Redeem a reward using points."""
        current_points = self._user_points.get(user_id, 0)

        if current_points < points_cost:
            return {"error": "Insufficient points"}

        self._user_points[user_id] = current_points - points_cost

        return {
            "user_id": str(user_id),
            "reward_id": reward_id,
            "points_spent": points_cost,
            "remaining_points": self._user_points[user_id],
            "redeemed_at": "2024-01-01T00:00:00Z",
        }

    def get_available_rewards(self) -> List[Dict[str, Any]]:
        """Get available rewards."""
        return [
            {
                "id": "certificate",
                "name": "Course Certificate",
                "description": "Digital certificate of completion",
                "points_cost": 500,
                "category": "achievement",
            },
            {
                "id": "study_guide",
                "name": "Premium Study Guide",
                "description": "Comprehensive study materials",
                "points_cost": 200,
                "category": "learning",
            },
            {
                "id": "one_on_one",
                "name": "1-on-1 Tutoring Session",
                "description": "30-minute tutoring session",
                "points_cost": 300,
                "category": "support",
            },
        ]

    def track_gamification_engagement(
        self,
        user_id: UUID,
        activity_type: str,
        metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Track user engagement with gamification features."""
        return {
            "user_id": str(user_id),
            "activity_type": activity_type,
            "engagement_score": 85,  # out of 100
            "metadata": metadata,
            "tracked_at": "2024-01-01T00:00:00Z",
        }

    def create_progress_milestone(
        self,
        course_id: UUID,
        title: str,
        description: str,
        target_percentage: float,
        reward_points: int,
    ) -> Dict[str, Any]:
        """Create a progress milestone."""
        milestone_id = UUID(f"milestone_{course_id}")

        milestone = {
            "id": str(milestone_id),
            "course_id": str(course_id),
            "title": title,
            "description": description,
            "target_percentage": target_percentage,
            "reward_points": reward_points,
            "is_achieved": False,
            "participants": 0,
            "completions": 0,
            "created_at": "2024-01-01T00:00:00Z",
        }

        return milestone

    def check_milestone_achievement(
        self,
        user_id: UUID,
        course_id: UUID,
        current_progress: float,
    ) -> List[Dict[str, Any]]:
        """Check if user has achieved any milestones."""
        # Mock milestone checking
        achievements = []

        if current_progress >= 25:
            achievements.append({
                "milestone": "Quarter Complete",
                "reward_points": 50,
                "achieved_at": "2024-01-01T00:00:00Z",
            })

        if current_progress >= 50:
            achievements.append({
                "milestone": "Halfway There",
                "reward_points": 100,
                "achieved_at": "2024-01-01T00:00:00Z",
            })

        return achievements
