"""
Development settings for local testing.

This module provides default settings for local development and testing.
Do not use these settings in production.
"""
import os
from pathlib import Path
from datetime import datetime

# Create a development secret key for local testing
# This is not secure for production use
DEFAULT_SECRET_KEY = "7+bL4Z7RmDgHMXk+MKj0cMoQ9zEtyIZcVcYrnMF5XnE="

# Ensure we have a SECRET_KEY
if 'SECRET_KEY' not in os.environ:
    print(f"WARNING: Using default SECRET_KEY for development. Do not use in production!")
    os.environ['SECRET_KEY'] = DEFAULT_SECRET_KEY
    
# Set default values for other required settings
if 'ACCESS_TOKEN_EXPIRE_MINUTES' not in os.environ:
    os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'] = '60'  # 1 hour
    
# Output directory
output_dir = Path(__file__).parent.parent / "output"
output_dir.mkdir(exist_ok=True)

print(f"[{datetime.now()}] Development settings loaded. Using SECRET_KEY: {os.environ['SECRET_KEY'][:5]}...")
