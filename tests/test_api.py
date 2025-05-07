"""
API testing script for Kids Book Generator.

This script tests the main functionality of the backend API endpoints,
including user management, authentication, book creation, and batch processing.
"""
import sys
import os
import requests
import json
from typing import Dict, Any, Optional

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Base URL for the API
BASE_URL = "http://localhost:8000/api/v1"

# Test user credentials
TEST_USER = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "Test1234!",
    "full_name": "Test User"
}

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(message: str) -> None:
    """Print a header message."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}=== {message} ==={Colors.ENDC}\n")

def print_success(message: str) -> None:
    """Print a success message."""
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")

def print_error(message: str) -> None:
    """Print an error message."""
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")

def print_request(method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> None:
    """Print request details."""
    print(f"{Colors.OKBLUE}→ {method} {endpoint}{Colors.ENDC}")
    if data:
        print(f"  Data: {json.dumps(data, indent=2)}")

def print_response(response) -> None:
    """Print response details."""
    status_color = Colors.OKGREEN if response.status_code < 400 else Colors.FAIL
    print(f"{status_color}← Status: {response.status_code}{Colors.ENDC}")
    try:
        data = response.json()
        print(f"  Response: {json.dumps(data, indent=2)}")
    except:
        print(f"  Response: {response.text[:100]}...")

def test_user_registration() -> Dict[str, Any]:
    """Test user registration."""
    print_header("Testing User Registration")
    
    endpoint = f"{BASE_URL}/users"
    print_request("POST", endpoint, TEST_USER)
    
    response = requests.post(endpoint, json=TEST_USER)
    print_response(response)
    
    if response.status_code == 201:
        print_success("User registration successful")
        return response.json()
    elif response.status_code == 400 and ("Username already exists" in response.text or "Username already registered" in response.text):
        print_success("User already exists, proceeding with login")
        return {"username": TEST_USER["username"]}
    else:
        print_error("User registration failed")
        return {"username": TEST_USER["username"]}  # Continue anyway for testing purposes

def test_user_authentication() -> Dict[str, Any]:
    """Test user authentication."""
    print_header("Testing User Authentication")
    
    endpoint = f"{BASE_URL}/auth/token"
    auth_data = {
        "username": TEST_USER["username"],
        "password": TEST_USER["password"]
    }
    print_request("POST", endpoint, auth_data)
    
    response = requests.post(
        endpoint, 
        data=auth_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    print_response(response)
    
    if response.status_code == 200:
        print_success("Authentication successful")
        return response.json()
    else:
        print_error("Authentication failed")
        return {}

def test_book_creation(auth_token: str, auth_data: Dict[str, Any]) -> Dict[str, Any]:
    """Test book creation."""
    print_header("Testing Book Creation")
    
    endpoint = f"{BASE_URL}/books"
    book_data = {
        "metadata": {
            "title": "Test Book",
            "book_type": "story",
            "trim_size": "8.5x8.5",
            "age_group": "5-7",
            "author": "Test Author",
            "theme": "Adventure",
            "page_count": 24
        },
        "template_id": "canva_story_square_dbfe88cd"
    }
    
    print_request("POST", endpoint, book_data)
    
    # Make sure we're using the token_type from the auth response (capitalized)
    token_type = auth_data.get("token_type", "bearer").capitalize()
    response = requests.post(
        endpoint,
        json=book_data,
        headers={"Authorization": f"{token_type} {auth_token}"}
    )
    print_response(response)
    
    if response.status_code == 201:
        print_success("Book creation successful")
        return response.json()
    else:
        print_error("Book creation failed")
        return {}

def test_book_list(auth_token: str, auth_data: Dict[str, Any]) -> None:
    """Test book listing."""
    print_header("Testing Book Listing")
    
    endpoint = f"{BASE_URL}/books"
    print_request("GET", endpoint)
    
    # Make sure we're using the token_type from the auth response
    # Make sure we're using the token_type from the auth response (capitalized)
    token_type = auth_data.get("token_type", "bearer").capitalize()
    response = requests.get(
        endpoint,
        headers={"Authorization": f"{token_type} {auth_token}"}
    )
    print_response(response)
    
    if response.status_code == 200:
        print_success("Book listing successful")
        books = response.json()
        print(f"Found {len(books)} books")
    else:
        print_error("Book listing failed")

def test_batch_job_creation(auth_token: str, auth_data: Dict[str, Any]) -> Dict[str, Any]:
    """Test batch job creation."""
    print_header("Testing Batch Job Creation")
    
    endpoint = f"{BASE_URL}/batch"
    batch_data = {
        "name": "Test Batch Job",
        "description": "A test batch job created by the API test script",
        "books": [
            {
                "metadata": {
                    "title": "Batch Book 1",
                    "book_type": "story",
                    "trim_size": "8.5x8.5",
                    "age_group": "5-7",
                    "author": "Test Author",
                    "theme": "Adventure",
                    "page_count": 24
                },
                "template_id": "canva_story_square_dbfe88cd"
            },
            {
                "metadata": {
                    "title": "Batch Book 2",
                    "book_type": "coloring",
                    "trim_size": "8.5x11",
                    "age_group": "7-12",
                    "author": "Test Author",
                    "theme": "Animals",
                    "page_count": 32
                },
                "template_id": "canva_coloring_standard_f728f12b"
            }
        ]
    }
    
    print_request("POST", endpoint, batch_data)
    
    # Make sure we're using the token_type from the auth response
    # Make sure we're using the token_type from the auth response (capitalized)
    token_type = auth_data.get("token_type", "bearer").capitalize()
    response = requests.post(
        endpoint,
        json=batch_data,
        headers={"Authorization": f"{token_type} {auth_token}"}
    )
    print_response(response)
    
    if response.status_code == 201:
        print_success("Batch job creation successful")
        return response.json()
    else:
        print_error("Batch job creation failed")
        return {}

def test_batch_job_status(auth_token: str, auth_data: Dict[str, Any], job_id: str) -> None:
    """Test batch job status checking."""
    print_header("Testing Batch Job Status")
    
    endpoint = f"{BASE_URL}/batch/{job_id}"
    print_request("GET", endpoint)
    
    # Make sure we're using the token_type from the auth response
    # Make sure we're using the token_type from the auth response (capitalized)
    token_type = auth_data.get("token_type", "bearer").capitalize()
    response = requests.get(
        endpoint,
        headers={"Authorization": f"{token_type} {auth_token}"}
    )
    print_response(response)
    
    if response.status_code == 200:
        print_success("Batch job status check successful")
        status = response.json().get("status", "unknown")
        print(f"Batch job status: {status}")
    else:
        print_error("Batch job status check failed")

def run_tests() -> None:
    """Run all API tests."""
    print_header("STARTING API TESTS")
    
    # Test user registration
    user = test_user_registration()
    if not user:
        print_error("Cannot proceed without user registration")
        return
    
    # Test authentication
    auth_data = test_user_authentication()
    if not auth_data or "access_token" not in auth_data:
        print_error("Cannot proceed without authentication")
        return
    
    auth_token = auth_data["access_token"]
    
    # Test book creation
    book = test_book_creation(auth_token, auth_data)
    
    # Test book listing
    test_book_list(auth_token, auth_data)
    
    # Test batch job creation
    batch_job = test_batch_job_creation(auth_token, auth_data)
    
    # Test batch job status
    if batch_job and "id" in batch_job:
        test_batch_job_status(auth_token, auth_data, batch_job["id"])
    
    print_header("API TESTS COMPLETED")

if __name__ == "__main__":
    run_tests()
