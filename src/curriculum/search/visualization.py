"""Visualization and interactive content service."""

from typing import Dict, List, Optional, Any
from uuid import UUID
import json

from curriculum.core.content import Content
from curriculum.config import settings


class VisualizationService:
    """Service for creating and managing interactive visualizations."""

    def __init__(self) -> None:
        """Initialize visualization service."""
        self._visualizations: dict[UUID, dict] = {}
        self._chart_templates: Dict[str, dict] = {
            "bar_chart": {
                "type": "bar",
                "config": {
                    "responsive": True,
                    "maintainAspectRatio": False,
                }
            },
            "line_chart": {
                "type": "line",
                "config": {
                    "responsive": True,
                    "maintainAspectRatio": False,
                }
            },
            "pie_chart": {
                "type": "pie",
                "config": {
                    "responsive": True,
                    "maintainAspectRatio": False,
                }
            },
            "scatter_plot": {
                "type": "scatter",
                "config": {
                    "responsive": True,
                    "maintainAspectRatio": False,
                }
            },
        }

    def create_visualization(
        self,
        content_id: UUID,
        title: str,
        visualization_type: str,
        data: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a new visualization."""
        visualization_id = UUID(f"viz_{content_id}_{len(self._visualizations)}")

        visualization = {
            "id": str(visualization_id),
            "content_id": str(content_id),
            "title": title,
            "type": visualization_type,
            "data": data,
            "config": config or {},
            "created_at": "2024-01-01T00:00:00Z",  # Would use datetime.now(timezone.utc)
            "is_interactive": True,
            "accessibility_features": {
                "alt_text": title,
                "screen_reader_support": True,
                "keyboard_navigation": True,
                "high_contrast": False,
            },
        }

        self._visualizations[visualization_id] = visualization
        return visualization

    def get_visualization(self, visualization_id: UUID) -> Optional[Dict[str, Any]]:
        """Get visualization by ID."""
        return self._visualizations.get(visualization_id)

    def get_content_visualizations(self, content_id: UUID) -> List[Dict[str, Any]]:
        """Get all visualizations for content."""
        return [
            viz for viz in self._visualizations.values()
            if viz["content_id"] == str(content_id)
        ]

    def create_progress_chart(
        self,
        content_id: UUID,
        user_id: UUID,
        progress_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create a progress visualization chart."""
        return self.create_visualization(
            content_id=content_id,
            title="Learning Progress",
            visualization_type="line_chart",
            data={
                "labels": progress_data.get("dates", []),
                "datasets": [{
                    "label": "Progress",
                    "data": progress_data.get("scores", []),
                    "borderColor": "#1f77b4",
                    "backgroundColor": "rgba(31, 119, 180, 0.1)",
                    "fill": True,
                }],
            },
            config={
                "plugins": {
                    "title": {"display": True, "text": "Learning Progress Over Time"},
                    "legend": {"display": False},
                },
                "scales": {
                    "y": {"beginAtZero": True, "max": 100},
                },
            },
        )

    def create_knowledge_map(
        self,
        content_id: UUID,
        concepts: List[Dict[str, Any]],
        connections: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Create an interactive knowledge map."""
        return self.create_visualization(
            content_id=content_id,
            title="Knowledge Map",
            visualization_type="network_graph",
            data={
                "nodes": concepts,
                "edges": connections,
            },
            config={
                "physics": {
                    "enabled": True,
                    "barnesHut": {
                        "gravitationalConstant": -2000,
                        "centralGravity": 0.3,
                        "springLength": 95,
                        "springConstant": 0.04,
                        "damping": 0.09,
                        "avoidOverlap": 0,
                    },
                },
                "interaction": {
                    "hover": True,
                    "tooltipDelay": 300,
                    "zoomView": True,
                    "dragView": True,
                },
            },
        )

    def create_quiz_results_chart(
        self,
        content_id: UUID,
        quiz_results: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create a chart showing quiz performance."""
        return self.create_visualization(
            content_id=content_id,
            title="Quiz Performance",
            visualization_type="bar_chart",
            data={
                "labels": quiz_results.get("quiz_names", []),
                "datasets": [{
                    "label": "Score",
                    "data": quiz_results.get("scores", []),
                    "backgroundColor": [
                        "#ff6384" if score < 70 else "#36a2eb"
                        for score in quiz_results.get("scores", [])
                    ],
                }],
            },
            config={
                "plugins": {
                    "title": {"display": True, "text": "Quiz Performance Results"},
                },
                "scales": {
                    "y": {"beginAtZero": True, "max": 100},
                },
            },
        )

    def create_study_time_heatmap(
        self,
        content_id: UUID,
        study_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create a heatmap showing study patterns."""
        return self.create_visualization(
            content_id=content_id,
            title="Study Time Heatmap",
            visualization_type="heatmap",
            data=study_data,
            config={
                "maintainAspectRatio": False,
                "plugins": {
                    "title": {"display": True, "text": "Study Time by Day and Hour"},
                },
                "scales": {
                    "x": {"type": "time", "time": {"unit": "hour"}},
                    "y": {"type": "time", "time": {"unit": "day"}},
                },
            },
        )

    def create_concept_relationship_diagram(
        self,
        content_id: UUID,
        concepts: List[str],
        relationships: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Create a concept relationship diagram."""
        nodes = [{"id": concept, "label": concept} for concept in concepts]
        edges = [
            {
                "from": rel["source"],
                "to": rel["target"],
                "label": rel.get("type", ""),
                "arrows": "to",
            }
            for rel in relationships
        ]

        return self.create_visualization(
            content_id=content_id,
            title="Concept Relationships",
            visualization_type="network_graph",
            data={"nodes": nodes, "edges": edges},
            config={
                "layout": {"hierarchical": {"direction": "UD"}},
                "physics": {"enabled": False},
                "interaction": {"dragNodes": True, "dragView": True, "zoomView": True},
            },
        )

    def export_visualization(
        self,
        visualization_id: UUID,
        format: str = "json",
    ) -> Dict[str, Any]:
        """Export visualization in specified format."""
        visualization = self.get_visualization(visualization_id)
        if not visualization:
            return {"error": "Visualization not found"}

        if format == "json":
            return visualization
        elif format == "png":
            # In production, this would generate actual image
            return {
                "id": visualization["id"],
                "format": "png",
                "url": f"/api/visualizations/{visualization_id}/export.png",
                "note": "Image generation requires additional libraries",
            }
        elif format == "svg":
            return {
                "id": visualization["id"],
                "format": "svg",
                "data": self._generate_svg(visualization),
            }
        else:
            return {"error": f"Unsupported format: {format}"}

    def _generate_svg(self, visualization: Dict[str, Any]) -> str:
        """Generate SVG representation of visualization (simplified)."""
        # This would use actual charting libraries in production
        return f'<svg><text x="10" y="20">{visualization["title"]}</text></svg>'

    def get_visualization_types(self) -> List[str]:
        """Get available visualization types."""
        return [
            "bar_chart",
            "line_chart",
            "pie_chart",
            "scatter_plot",
            "heatmap",
            "network_graph",
            "tree_diagram",
            "timeline",
            "word_cloud",
        ]

    def validate_visualization_data(self, data: Dict[str, Any], viz_type: str) -> Dict[str, Any]:
        """Validate visualization data format."""
        validation_rules = {
            "bar_chart": lambda d: "labels" in d and "datasets" in d,
            "line_chart": lambda d: "labels" in d and "datasets" in d,
            "pie_chart": lambda d: "labels" in d and "datasets" in d,
            "network_graph": lambda d: "nodes" in d and "edges" in d,
            "heatmap": lambda d: isinstance(d, dict) and len(d) > 0,
        }

        validator = validation_rules.get(viz_type)
        if not validator:
            return {"valid": False, "error": f"Unknown visualization type: {viz_type}"}

        is_valid = validator(data)

        return {
            "valid": is_valid,
            "type": viz_type,
            "data_size": len(str(data)),
        }
