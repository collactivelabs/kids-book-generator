"""
Direct JWT token validation utility.

This script allows us to validate JWT tokens directly without going through the FastAPI framework.
"""
import sys
import os
import json
import jwt
from datetime import datetime, timedelta
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Set the SECRET_KEY environment variable if not already set
if 'SECRET_KEY' not in os.environ:
    os.environ['SECRET_KEY'] = "7+bL4Z7RmDgHMXk+MKj0cMoQ9zEtyIZcVcYrnMF5XnE="

# Import settings after setting the SECRET_KEY
from src.config import settings


def create_test_token():
    """Create a test JWT token."""
    # Define token data
    data = {
        "sub": "testuser",
        "scopes": ["books:read", "books:write"],
    }
    
    # Set expiration time - using a timestamp far in the future to avoid any timezone issues
    # This is just for testing purposes
    now = datetime.utcnow()
    expire = now + timedelta(days=365)  # 1 year in the future
    
    # Print current time info
    print(f"Current UTC time: {now}")
    print(f"Expiration UTC time: {expire}")
    print(f"Current timestamp: {int(now.timestamp())}")
    print(f"Expiration timestamp: {int(expire.timestamp())}")
    
    # Add expiration time (as integer timestamp)
    data["exp"] = int(expire.timestamp())
    
    print(f"Token data: {json.dumps(data, indent=2)}")
    
    # Create token
    token = jwt.encode(
        data,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    print(f"Generated token: {token}")
    return token


def decode_token(token):
    """Decode a JWT token."""
    try:
        print(f"Attempting to decode token using SECRET_KEY: {settings.SECRET_KEY[:5]}...")
        
        # Decode token
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_nbf": False,
                "verify_iat": False,
                "verify_aud": False,
                "verify_iss": False,
                "require": ["exp"]
            }
        )
        
        print(f"Token decoded successfully!")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        # Verify expiration
        if "exp" in payload:
            exp_time = datetime.fromtimestamp(payload["exp"])
            now = datetime.utcnow()
            print(f"Token expiration time: {exp_time}")
            print(f"Current time: {now}")
            print(f"Time until expiration: {(exp_time - now).total_seconds()} seconds")
            
        return payload
    
    except jwt.ExpiredSignatureError:
        print("Token signature has expired!")
        return None
    except jwt.InvalidTokenError as e:
        print(f"Invalid token: {str(e)}")
        return None


def validate_provided_token(token):
    """Validate a provided JWT token."""
    # Try to decode the token
    decoded = decode_token(token)
    
    if decoded:
        print("\nToken is valid!")
        return True
    else:
        print("\nToken validation failed!")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Validate provided token
        token = sys.argv[1]
        print(f"Validating provided token: {token[:10]}...")
        validate_provided_token(token)
    else:
        # Create and validate a test token
        print("Creating a test token...")
        token = create_test_token()
        
        print("\nValidating the test token...")
        validate_provided_token(token)
