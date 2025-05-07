"""
Pytest configuration for the Kids Book Generator.

This module provides fixtures and configuration for testing.
"""
import os
import sys
import pytest
from fastapi.testclient import TestClient

# Add source directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.main import app
from src.config import settings


@pytest.fixture
def test_client():
    """
    Create a test client for FastAPI.
    
    Returns:
        TestClient: FastAPI test client
    """
    with TestClient(app) as client:
        yield client


@pytest.fixture
def test_settings():
    """
    Provide test settings.
    
    Returns:
        dict: Test configuration settings
    """
    # Override settings for testing
    test_config = settings.dict()
    
    # Use test database
    test_config["DATABASE_URL"] = test_config["DATABASE_URL"].replace(
        "kids_book_generator", "kids_book_generator_test"
    )
    
    # Use test Redis instance
    test_config["REDIS_URL"] = test_config["REDIS_URL"].replace("/0", "/1")
    
    return test_config


@pytest.fixture
def mock_openai_api_key():
    """
    Provide a mock OpenAI API key for testing.
    
    Returns:
        str: Mock API key
    """
    return "sk-test-key-12345"


@pytest.fixture
def mock_canva_credentials():
    """
    Provide mock Canva credentials for testing.
    
    Returns:
        dict: Mock credentials
    """
    return {
        "client_id": "test-client-id",
        "client_secret": "test-client-secret",
        "redirect_uri": "http://localhost:8000/api/v1/auth/canva/callback",
    }
