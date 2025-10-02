"""Tests for Distribution Service."""

import pytest
import asyncio
from uuid import uuid4

from curriculum.integration.distribution import DistributionService


class TestDistributionService:
    """Tests for DistributionService."""

    @pytest.fixture
    def distribution_service(self):
        """Distribution service fixture."""
        return DistributionService()

    @pytest.mark.asyncio
    async def test_distribute_content(self, distribution_service, sample_content):
        """Test distributing content."""
        result = await distribution_service.distribute_content(sample_content.id)

        assert result["content_id"] == str(sample_content.id)
        assert result["status"] == "completed"
        assert "cdn_urls" in result
        assert "edge_locations" in result
        assert "distributed_at" in result

    @pytest.mark.asyncio
    async def test_invalidate_cache(self, distribution_service, sample_content):
        """Test cache invalidation."""
        success = await distribution_service.invalidate_cache(sample_content.id, ["/content/*"])

        assert success is True

    @pytest.mark.asyncio
    async def test_warm_cache(self, distribution_service, sample_content):
        """Test cache warming."""
        urls = [
            f"https://cdn.example.com/content/{sample_content.id}/index.html",
            f"https://cdn.example.com/content/{sample_content.id}/assets/style.css",
        ]

        results = await distribution_service.warm_cache(sample_content.id, urls)

        assert len(results) == 2
        for url, result in results.items():
            assert result["status"] == "warmed"
            assert result["response_time"] > 0
            assert "cached_at" in result

    def test_generate_cache_key(self, distribution_service, sample_content):
        """Test cache key generation."""
        cache_key = distribution_service.generate_cache_key(sample_content.id, "html")

        assert cache_key == f"content:{sample_content.id}:html"

    def test_calculate_content_hash(self, distribution_service):
        """Test content hash calculation."""
        content = "This is test content for hashing"
        hash_value = distribution_service.calculate_content_hash(content)

        assert len(hash_value) == 64  # SHA-256 hex length
        assert hash_value.isalnum()

    @pytest.mark.asyncio
    async def test_get_distribution_status(self, distribution_service, sample_content):
        """Test getting distribution status."""
        status = await distribution_service.get_distribution_status(sample_content.id)

        assert status["content_id"] == str(sample_content.id)
        assert "status" in status
        assert "cdn_urls" in status

    @pytest.mark.asyncio
    async def test_batch_distribute(self, distribution_service, sample_content):
        """Test batch distribution."""
        content_ids = [sample_content.id, uuid4(), uuid4()]

        result = await distribution_service.batch_distribute(content_ids)

        assert result["total"] == 3
        assert result["successful"] == 1  # Only the valid content ID
        assert result["failed"] == 2  # Invalid UUIDs
        assert "results" in result
        assert "errors" in result

    @pytest.mark.asyncio
    async def test_optimize_for_delivery(self, distribution_service, sample_content):
        """Test content optimization."""
        optimizations = {
            "minify": True,
            "compress": True,
            "image_optimization": True,
        }

        result = await distribution_service.optimize_for_delivery(
            sample_content.id,
            optimizations,
        )

        assert result["content_id"] == str(sample_content.id)
        assert result["optimizations_applied"]["minify"] is True
        assert result["optimizations_applied"]["compress"] is True
        assert result["compression_ratio"] == 0.75

    def test_generate_presigned_url(self, distribution_service, sample_content):
        """Test presigned URL generation."""
        filename = "document.pdf"
        expires_in = 3600

        url = distribution_service.generate_presigned_url(
            sample_content.id,
            filename,
            expires_in,
        )

        assert sample_content.id in url
        assert filename in url
        assert f"expires={expires_in}" in url

    @pytest.mark.asyncio
    async def test_get_content_metrics(self, distribution_service, sample_content):
        """Test getting content metrics."""
        metrics = await distribution_service.get_content_metrics(sample_content.id)

        assert metrics["content_id"] == str(sample_content.id)
        assert "total_requests" in metrics
        assert "cache_hits" in metrics
        assert "average_response_time" in metrics
