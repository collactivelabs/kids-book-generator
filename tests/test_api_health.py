"""
Tests for the API health endpoint.

This module contains tests to ensure the API health check endpoint
is working correctly.
"""
import pytest
from fastapi.testclient import TestClient


def test_health_endpoint(test_client: TestClient):
    """Test that the health endpoint returns the correct status."""
    response = test_client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"
    assert "version" in data
