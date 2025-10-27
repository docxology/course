"""Content quality assessment and improvement service."""

from typing import Dict, List, Optional, Any
from uuid import UUID
from datetime import datetime
import re

from curriculum.core.content import Content


class ContentQualityService:
    """Service for assessing and improving content quality."""

    def __init__(self) -> None:
        """Initialize content quality service."""
        self._quality_rules: Dict[str, Dict[str, Any]] = {}
        self._quality_scores: Dict[UUID, Dict[str, Any]] = {}

        self._initialize_quality_rules()

    def _initialize_quality_rules(self) -> None:
        """Initialize content quality assessment rules."""
        self._quality_rules = {
            "content_length": {
                "min_words": 300,
                "max_words": 2000,
                "ideal_words": 800,
                "weight": 0.15,
            },
            "structure": {
                "required_sections": ["introduction", "main_content", "conclusion"],
                "recommended_sections": ["examples", "exercises", "references"],
                "weight": 0.20,
            },
            "readability": {
                "max_sentence_length": 25,  # words
                "max_paragraph_length": 150,  # words
                "ideal_flesch_score": 60,  # readability score
                "weight": 0.25,
            },
            "technical_accuracy": {
                "check_spelling": True,
                "check_grammar": True,
                "check_facts": False,  # Would require external services
                "weight": 0.20,
            },
            "engagement": {
                "min_examples": 2,
                "min_exercises": 1,
                "interactive_elements": True,
                "weight": 0.20,
            },
        }

    def assess_content_quality(self, content: Content) -> Dict[str, Any]:
        """Assess overall quality of content."""
        content_id = content.id

        # Perform individual quality checks
        length_score = self._assess_content_length(content)
        structure_score = self._assess_content_structure(content)
        readability_score = self._assess_readability(content)
        technical_score = self._assess_technical_accuracy(content)
        engagement_score = self._assess_engagement(content)

        # Calculate weighted overall score
        overall_score = (
            length_score["score"] * self._quality_rules["content_length"]["weight"] +
            structure_score["score"] * self._quality_rules["structure"]["weight"] +
            readability_score["score"] * self._quality_rules["readability"]["weight"] +
            technical_score["score"] * self._quality_rules["technical_accuracy"]["weight"] +
            engagement_score["score"] * self._quality_rules["engagement"]["weight"]
        )

        assessment = {
            "content_id": str(content_id),
            "overall_score": overall_score,
            "quality_level": self._get_quality_level(overall_score),
            "assessed_at": datetime.now(timezone.utc).isoformat(),
            "breakdown": {
                "content_length": length_score,
                "structure": structure_score,
                "readability": readability_score,
                "technical_accuracy": technical_score,
                "engagement": engagement_score,
            },
            "recommendations": self._generate_recommendations(overall_score, {
                "length": length_score,
                "structure": structure_score,
                "readability": readability_score,
                "technical": technical_score,
                "engagement": engagement_score,
            }),
        }

        self._quality_scores[content_id] = assessment
        return assessment

    def _assess_content_length(self, content: Content) -> Dict[str, Any]:
        """Assess content length."""
        if not content.content_body:
            return {"score": 0, "issues": ["No content"], "details": {}}

        word_count = len(content.content_body.split())
        rules = self._quality_rules["content_length"]

        score = 100
        issues = []

        if word_count < rules["min_words"]:
            score -= 50
            issues.append(f"Content too short: {word_count} < {rules['min_words']} words")
        elif word_count > rules["max_words"]:
            score -= 20
            issues.append(f"Content very long: {word_count} > {rules['max_words']} words")

        # Ideal length bonus
        if rules["min_words"] <= word_count <= rules["max_words"]:
            ideal_diff = abs(word_count - rules["ideal_words"])
            if ideal_diff < 100:
                score += 10  # Bonus for near-ideal length

        return {
            "score": max(0, score),
            "issues": issues,
            "details": {
                "word_count": word_count,
                "min_words": rules["min_words"],
                "max_words": rules["max_words"],
                "ideal_words": rules["ideal_words"],
            },
        }

    def _assess_content_structure(self, content: Content) -> Dict[str, Any]:
        """Assess content structure."""
        if not content.content_body:
            return {"score": 0, "issues": ["No content to analyze"], "details": {}}

        content_text = content.content_body.lower()
        rules = self._quality_rules["structure"]

        score = 100
        issues = []
        found_sections = []

        for section in rules["required_sections"]:
            if section in content_text:
                found_sections.append(section)
            else:
                score -= 30
                issues.append(f"Missing required section: {section}")

        # Check for recommended sections
        recommended_found = 0
        for section in rules["recommended_sections"]:
            if section in content_text:
                recommended_found += 1

        # Bonus for having recommended sections
        score += min(recommended_found * 5, 15)

        return {
            "score": max(0, score),
            "issues": issues,
            "details": {
                "required_sections_found": len(found_sections),
                "recommended_sections_found": recommended_found,
                "total_required": len(rules["required_sections"]),
                "total_recommended": len(rules["recommended_sections"]),
            },
        }

    def _assess_readability(self, content: Content) -> Dict[str, Any]:
        """Assess content readability."""
        if not content.content_body:
            return {"score": 0, "issues": ["No content to analyze"], "details": {}}

        content_text = content.content_body
        rules = self._quality_rules["readability"]

        # Simple readability metrics
        sentences = re.split(r'[.!?]+', content_text)
        sentences = [s.strip() for s in sentences if s.strip()]

        paragraphs = [p.strip() for p in content_text.split('\n\n') if p.strip()]

        long_sentences = [s for s in sentences if len(s.split()) > rules["max_sentence_length"]]
        long_paragraphs = [p for p in paragraphs if len(p.split()) > rules["max_paragraph_length"]]

        score = 100
        issues = []

        if long_sentences:
            score -= min(len(long_sentences) * 5, 30)
            issues.append(f"{len(long_sentences)} sentences too long (> {rules['max_sentence_length']} words)")

        if long_paragraphs:
            score -= min(len(long_paragraphs) * 3, 20)
            issues.append(f"{len(long_paragraphs)} paragraphs too long (> {rules['max_paragraph_length']} words)")

        # Simple Flesch score approximation
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        avg_syllables_per_word = 1.5  # Approximation

        flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        if flesch_score < rules["ideal_flesch_score"] - 10:
            score -= 15
            issues.append(f"Content may be too difficult to read (Flesch score: {flesch_score:.1f})")

        return {
            "score": max(0, score),
            "issues": issues,
            "details": {
                "total_sentences": len(sentences),
                "total_paragraphs": len(paragraphs),
                "long_sentences": len(long_sentences),
                "long_paragraphs": len(long_paragraphs),
                "avg_sentence_length": avg_sentence_length,
                "estimated_flesch_score": flesch_score,
            },
        }

    def _assess_technical_accuracy(self, content: Content) -> Dict[str, Any]:
        """Assess technical accuracy of content."""
        if not content.content_body:
            return {"score": 0, "issues": ["No content to analyze"], "details": {}}

        content_text = content.content_body.lower()
        rules = self._quality_rules["technical_accuracy"]

        score = 100
        issues = []

        # Basic spelling check (very simple - in production, use proper spell checker)
        common_typos = ["teh", "recieve", "seperate", "occured"]
        found_typos = [typo for typo in common_typos if typo in content_text]

        if found_typos:
            score -= len(found_typos) * 10
            issues.append(f"Possible typos found: {', '.join(found_typos)}")

        # Check for broken links (basic pattern matching)
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, content_text)

        if urls:
            issues.append(f"Found {len(urls)} URLs that should be verified")

        return {
            "score": max(0, score),
            "issues": issues,
            "details": {
                "urls_found": len(urls),
                "potential_typos": len(found_typos),
                "spelling_check": rules["check_spelling"],
                "grammar_check": rules["check_grammar"],
            },
        }

    def _assess_engagement(self, content: Content) -> Dict[str, Any]:
        """Assess content engagement potential."""
        if not content.content_body:
            return {"score": 0, "issues": ["No content to analyze"], "details": {}}

        content_text = content.content_body.lower()
        rules = self._quality_rules["engagement"]

        score = 100
        issues = []
        found_elements = []

        # Check for examples
        example_count = content_text.count("example") + content_text.count("for example")
        if example_count < rules["min_examples"]:
            score -= (rules["min_examples"] - example_count) * 15
            issues.append(f"Need at least {rules['min_examples']} examples")
        else:
            found_elements.append(f"examples: {example_count}")

        # Check for exercises
        exercise_count = (
            content_text.count("exercise") +
            content_text.count("practice") +
            content_text.count("activity")
        )
        if exercise_count < rules["min_exercises"]:
            score -= (rules["min_exercises"] - exercise_count) * 20
            issues.append(f"Need at least {rules['min_exercises']} exercises")
        else:
            found_elements.append(f"exercises: {exercise_count}")

        # Check for interactive elements
        interactive_indicators = ["question", "quiz", "test", "interactive"]
        interactive_count = sum(content_text.count(indicator) for indicator in interactive_indicators)

        if rules["interactive_elements"] and interactive_count == 0:
            score -= 15
            issues.append("Consider adding interactive elements")

        return {
            "score": max(0, score),
            "issues": issues,
            "details": {
                "examples_found": example_count,
                "exercises_found": exercise_count,
                "interactive_elements": interactive_count,
                "engagement_elements": found_elements,
            },
        }

    def _get_quality_level(self, score: float) -> str:
        """Get quality level based on score."""
        if score >= 90:
            return "excellent"
        elif score >= 75:
            return "good"
        elif score >= 60:
            return "satisfactory"
        elif score >= 40:
            return "needs_improvement"
        else:
            return "poor"

    def _generate_recommendations(self, overall_score: float, breakdown: Dict[str, Any]) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []

        if overall_score < 60:
            recommendations.append("Major revisions recommended")

        for category, results in breakdown.items():
            if results["score"] < 70:
                if category == "length":
                    if results["details"].get("word_count", 0) < 300:
                        recommendations.append("Expand content with more detailed explanations")
                    elif results["details"].get("word_count", 0) > 2000:
                        recommendations.append("Consider breaking into multiple sections")
                elif category == "structure":
                    recommendations.append("Ensure all required sections are present")
                elif category == "readability":
                    recommendations.append("Simplify complex sentences and improve flow")
                elif category == "technical":
                    recommendations.append("Review for spelling and grammar issues")
                elif category == "engagement":
                    recommendations.append("Add more examples and interactive elements")

        if not recommendations:
            recommendations.append("Content quality is good")

        return recommendations

    def create_quality_checklist(
        self,
        content_type: str,
        difficulty: str,
    ) -> List[Dict[str, Any]]:
        """Create a quality checklist for content creation."""
        base_checklist = [
            {
                "category": "Structure",
                "item": "Has clear introduction",
                "required": True,
                "points": 10,
            },
            {
                "category": "Structure",
                "item": "Has learning objectives",
                "required": True,
                "points": 15,
            },
            {
                "category": "Content",
                "item": "Provides clear explanations",
                "required": True,
                "points": 20,
            },
            {
                "category": "Examples",
                "item": "Includes practical examples",
                "required": True,
                "points": 15,
            },
            {
                "category": "Exercises",
                "item": "Has practice exercises",
                "required": False,
                "points": 10,
            },
            {
                "category": "Assessment",
                "item": "Includes knowledge checks",
                "required": False,
                "points": 10,
            },
        ]

        # Adjust for content type
        if content_type == "assessment":
            base_checklist.extend([
                {
                    "category": "Questions",
                    "item": "Questions are clear and unambiguous",
                    "required": True,
                    "points": 15,
                },
                {
                    "category": "Answers",
                    "item": "Correct answers are provided",
                    "required": True,
                    "points": 10,
                },
            ])

        return base_checklist

    def validate_against_checklist(
        self,
        content: Content,
        checklist: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Validate content against quality checklist."""
        content_text = content.content_body.lower() if content.content_body else ""

        results = []
        total_points = 0
        earned_points = 0

        for item in checklist:
            required = item["required"]
            points = item["points"]

            # Simple validation logic (in production, would be more sophisticated)
            passed = False

            if "introduction" in item["item"].lower():
                passed = "introduction" in content_text or "intro" in content_text
            elif "learning objectives" in item["item"].lower():
                passed = "objective" in content_text or "goal" in content_text or "learn" in content_text
            elif "explanation" in item["item"].lower():
                passed = len(content_text.split()) > 200  # Basic check for sufficient content
            elif "example" in item["item"].lower():
                passed = "example" in content_text or "for example" in content_text
            elif "exercise" in item["item"].lower():
                passed = "exercise" in content_text or "practice" in content_text
            elif "question" in item["item"].lower():
                passed = "question" in content_text or "quiz" in content_text
            elif "answer" in item["item"].lower():
                passed = True  # Assume answers are provided for assessments

            total_points += points
            if passed:
                earned_points += points

            results.append({
                "item": item["item"],
                "required": required,
                "points": points,
                "passed": passed,
                "category": item["category"],
            })

        score = (earned_points / total_points) * 100 if total_points > 0 else 0

        return {
            "content_id": str(content.id),
            "checklist_results": results,
            "total_points": total_points,
            "earned_points": earned_points,
            "score": score,
            "quality_level": self._get_quality_level(score),
            "validated_at": datetime.now(timezone.utc).isoformat(),
        }

    def get_quality_trends(self, user_id: UUID) -> Dict[str, Any]:
        """Get quality trends for a user's content."""
        # Mock quality trends
        return {
            "user_id": str(user_id),
            "period": "Last 30 days",
            "trend_data": [
                {"date": "2024-01-01", "score": 75},
                {"date": "2024-01-08", "score": 78},
                {"date": "2024-01-15", "score": 82},
                {"date": "2024-01-22", "score": 85},
            ],
            "improvement_rate": 2.5,  # points per week
            "consistency_score": 0.85,  # how consistent quality is
            "areas_of_improvement": [
                "Content structure",
                "Technical accuracy",
            ],
        }

    def suggest_quality_improvements(
        self,
        content: Content,
        target_score: float = 85.0,
    ) -> List[str]:
        """Suggest specific improvements to reach target quality score."""
        current_assessment = self.assess_content_quality(content)
        current_score = current_assessment["overall_score"]

        if current_score >= target_score:
            return ["Content quality is already excellent"]

        suggestions = []

        # Analyze what needs improvement
        breakdown = current_assessment["breakdown"]

        if breakdown["content_length"]["score"] < 80:
            suggestions.append("Expand content with more detailed explanations and examples")

        if breakdown["structure"]["score"] < 80:
            suggestions.append("Add missing required sections and improve organization")

        if breakdown["readability"]["score"] < 80:
            suggestions.append("Simplify complex sentences and improve readability")

        if breakdown["technical_accuracy"]["score"] < 80:
            suggestions.append("Review content for spelling, grammar, and factual accuracy")

        if breakdown["engagement"]["score"] < 80:
            suggestions.append("Add more examples, exercises, and interactive elements")

        if not suggestions:
            suggestions.append("General content refinement recommended")

        return suggestions

    def create_quality_report(
        self,
        content_id: UUID,
        include_recommendations: bool = True,
    ) -> Dict[str, Any]:
        """Generate a comprehensive quality report."""
        content = None  # Would get from content service
        if not content:
            return {"error": "Content not found"}

        assessment = self.assess_content_quality(content)

        report = {
            "content_id": str(content_id),
            "report_type": "quality_assessment",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "overall_score": assessment["overall_score"],
                "quality_level": assessment["quality_level"],
                "word_count": len(content.content_body.split()) if content.content_body else 0,
            },
            "detailed_analysis": assessment["breakdown"],
        }

        if include_recommendations:
            report["recommendations"] = assessment["recommendations"]
            report["improvement_suggestions"] = self.suggest_quality_improvements(content)

        return report

    def benchmark_content_quality(
        self,
        content_ids: List[UUID],
        benchmark_criteria: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Benchmark content quality against criteria."""
        # Mock benchmarking
        return {
            "benchmark_id": f"benchmark_{len(content_ids)}",
            "content_count": len(content_ids),
            "criteria": benchmark_criteria,
            "results": [
                {
                    "content_id": str(content_id),
                    "score": 82.5,
                    "rank": i + 1,
                    "performance": "above_average",
                }
                for i, content_id in enumerate(content_ids)
            ],
            "benchmark_summary": {
                "average_score": 78.5,
                "top_performer": str(content_ids[0]),
                "areas_for_improvement": ["Readability", "Engagement"],
            },
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    def get_quality_analytics(self) -> Dict[str, Any]:
        """Get overall quality analytics for the system."""
        # Mock system-wide quality analytics
        return {
            "total_content_assessed": 1250,
            "average_quality_score": 78.5,
            "quality_distribution": {
                "excellent": 15,  # percentage
                "good": 45,
                "satisfactory": 25,
                "needs_improvement": 12,
                "poor": 3,
            },
            "common_issues": [
                "Content too short",
                "Missing examples",
                "Poor readability",
                "Lack of structure",
            ],
            "improvement_trends": {
                "monthly_average": [75, 77, 78, 79, 80, 78],
                "improvement_rate": 1.2,  # points per month
            },
        }
