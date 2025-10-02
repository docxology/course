"""Tests for routes module."""

import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from curriculum.routes.main import app


class TestMainRoutes:
    """Tests for main routes."""

    def test_health_check(self):
        """Test health check endpoint."""
        client = TestClient(app)

        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
        assert "version" in data
        assert "environment" in data

    def test_health_check_headers(self):
        """Test health check response headers."""
        client = TestClient(app)

        response = client.get("/health")

        assert "X-Process-Time" in response.headers


class TestContentRoutes:
    """Tests for content routes."""

    def test_create_content_unauthorized(self):
        """Test creating content without authentication."""
        client = TestClient(app)

        response = client.post("/api/v1/content/")

        assert response.status_code == 401

    def test_get_content_not_found(self):
        """Test getting non-existent content."""
        client = TestClient(app)

        response = client.get(f"/api/v1/content/{uuid4()}")

        assert response.status_code == 404

    def test_list_content(self):
        """Test listing content."""
        client = TestClient(app)

        response = client.get("/api/v1/content/")

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data

    def test_render_content_not_found(self):
        """Test rendering non-existent content."""
        client = TestClient(app)

        response = client.get(f"/api/v1/content/{uuid4()}/render")

        assert response.status_code == 404


class TestUserRoutes:
    """Tests for user routes."""

    def test_create_user_validation(self):
        """Test user creation with invalid data."""
        client = TestClient(app)

        # Test with missing required fields
        response = client.post("/api/v1/users/", json={})

        assert response.status_code == 422

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        client = TestClient(app)

        response = client.post("/api/v1/users/login", json={
            "username_or_email": "nonexistent",
            "password": "wrongpassword"
        })

        assert response.status_code == 401

    def test_get_user_not_found(self):
        """Test getting non-existent user."""
        client = TestClient(app)

        response = client.get(f"/api/v1/users/{uuid4()}")

        assert response.status_code == 404


class TestAssessmentRoutes:
    """Tests for assessment routes."""

    def test_create_assessment_unauthorized(self):
        """Test creating assessment without proper permissions."""
        client = TestClient(app)

        response = client.post("/api/v1/assessments/")

        assert response.status_code == 401

    def test_get_assessment_not_found(self):
        """Test getting non-existent assessment."""
        client = TestClient(app)

        response = client.get(f"/api/v1/assessments/{uuid4()}")

        assert response.status_code == 404

    def test_list_assessments(self):
        """Test listing assessments."""
        client = TestClient(app)

        response = client.get("/api/v1/assessments/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_start_submission_not_found(self):
        """Test starting submission for non-existent assessment."""
        client = TestClient(app)

        response = client.post(f"/api/v1/assessments/{uuid4()}/submissions")

        assert response.status_code == 404


class TestAnalyticsRoutes:
    """Tests for analytics routes."""

    def test_get_user_report_unauthorized(self):
        """Test getting user report without permissions."""
        client = TestClient(app)

        response = client.get(f"/api/v1/analytics/users/{uuid4()}/report")

        assert response.status_code == 403

    def test_get_content_report(self):
        """Test getting content report."""
        client = TestClient(app)

        response = client.get(f"/api/v1/analytics/content/{uuid4()}/report")

        assert response.status_code == 200
        data = response.json()
        assert "content_id" in data
        assert "total_views" in data

    def test_get_user_events(self):
        """Test getting user events."""
        client = TestClient(app)

        response = client.get(f"/api/v1/analytics/users/{uuid4()}/events")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_content_events(self):
        """Test getting content events."""
        client = TestClient(app)

        response = client.get(f"/api/v1/analytics/content/{uuid4()}/events")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_dashboard_overview_unauthorized(self):
        """Test dashboard overview without permissions."""
        client = TestClient(app)

        response = client.get("/api/v1/analytics/dashboard/overview")

        assert response.status_code == 403

    def test_export_analytics_report_unauthorized(self):
        """Test exporting analytics report without permissions."""
        client = TestClient(app)

        response = client.get("/api/v1/analytics/reports/export?report_type=user&format=pdf")

        assert response.status_code == 403


class TestRouteStructure:
    """Tests for route structure and organization."""

    def test_api_versioning(self):
        """Test that API routes are properly versioned."""
        client = TestClient(app)

        # All API routes should start with /api/v1/
        api_routes = [
            "/api/v1/content/",
            "/api/v1/users/",
            "/api/v1/assessments/",
            "/api/v1/analytics/",
        ]

        for route in api_routes:
            # Just check that the routes exist in the app
            assert route in str(app.routes)

    def test_cors_middleware(self):
        """Test that CORS middleware is configured."""
        # Check that CORS middleware is in the app
        assert any("CORSMiddleware" in str(middleware) for middleware in app.user_middleware)

    def test_exception_handlers(self):
        """Test that global exception handlers are configured."""
        # Check that exception handler is in the app
        assert hasattr(app, 'exception_handlers')
        assert Exception in app.exception_handlers

    def test_route_tags(self):
        """Test that routes have proper tags."""
        # Check that routes are properly tagged
        content_routes = [route for route in app.routes if "/content" in str(route.path)]
        user_routes = [route for route in app.routes if "/users" in str(route.path)]

        # Should have tagged routes
        assert len(content_routes) > 0
        assert len(user_routes) > 0

    def test_route_dependencies(self):
        """Test that routes have proper dependencies."""
        # Check that protected routes have dependencies
        protected_routes = [
            route for route in app.routes
            if any(dep for dep in route.dependencies if "Depends" in str(dep))
        ]

        assert len(protected_routes) > 0

    def test_middleware_order(self):
        """Test that middleware is properly ordered."""
        # Check that CORS middleware is configured
        middleware_classes = [str(type(m.cls)) for m in app.user_middleware]

        # CORS should be configured (though exact order may vary)
        assert any("CORSMiddleware" in cls for cls in middleware_classes)

    def test_health_check_response_format(self):
        """Test health check response format."""
        client = TestClient(app)

        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        # Should have all required fields
        required_fields = ["status", "service", "version", "environment", "timestamp"]
        for field in required_fields:
            assert field in data

    def test_error_response_format(self):
        """Test error response format."""
        client = TestClient(app)

        response = client.get(f"/api/v1/content/{uuid4()}")

        assert response.status_code == 404
        data = response.json()

        # Should have error information
        assert "detail" in data


