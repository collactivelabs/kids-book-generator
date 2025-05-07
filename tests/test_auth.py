"""
Tests for authentication functionality.

This module contains tests for authentication endpoints and utilities,
including token generation and OAuth flows.
"""
import pytest
from fastapi.testclient import TestClient
import jwt
from datetime import datetime

from src.utils.auth import create_access_token


def test_login_endpoint(test_client: TestClient):
    """Test that the login endpoint returns a valid token with correct credentials."""
    response = test_client.post(
        "/api/v1/auth/token",
        data={"username": "admin", "password": "admin"},
    )
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"
    assert "expires_at" in data


def test_login_endpoint_invalid_credentials(test_client: TestClient):
    """Test that the login endpoint returns 401 with incorrect credentials."""
    response = test_client.post(
        "/api/v1/auth/token",
        data={"username": "wrong", "password": "wrong"},
    )
    assert response.status_code == 401


def test_canva_authorize_endpoint(test_client: TestClient):
    """Test that the Canva authorization endpoint returns a valid URL."""
    response = test_client.get("/api/v1/auth/canva/authorize")
    assert response.status_code == 200
    
    data = response.json()
    assert "authorization_url" in data
    assert "canva.com/oauth/authorize" in data["authorization_url"]
    assert "client_id=" in data["authorization_url"]


def test_openai_key_validation_endpoint(test_client: TestClient):
    """Test that the OpenAI key validation endpoint works correctly."""
    # Test with valid key format
    response = test_client.post(
        "/api/v1/auth/openai/validate",
        params={"api_key": "sk-test-validkeyformat12345678901234"},
    )
    assert response.status_code == 200
    
    data = response.json()
    assert "valid" in data
    assert data["valid"] is True
    
    # Test with invalid key format
    response = test_client.post(
        "/api/v1/auth/openai/validate",
        params={"api_key": "invalid"},
    )
    assert response.status_code == 200
    
    data = response.json()
    assert "valid" in data
    assert data["valid"] is False


def test_create_access_token():
    """Test that the create_access_token utility creates valid tokens."""
    token_data = {"sub": "test_user"}
    token = create_access_token(token_data)
    
    # Token should be a string
    assert isinstance(token, str)
    
    # We should be able to decode the token (this would raise an exception if invalid)
    try:
        jwt.decode(token, options={"verify_signature": False})
    except Exception as e:
        pytest.fail(f"Token decoding failed: {str(e)}")
