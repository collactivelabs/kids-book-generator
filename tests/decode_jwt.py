"""Decode JWT token payload."""
import sys
import base64
import json

def decode_jwt_payload(token):
    """
    Decode the payload part of a JWT token.
    
    Args:
        token: JWT token
    
    Returns:
        Decoded payload as dict
    """
    parts = token.split('.')
    if len(parts) != 3:
        return {"error": "Invalid JWT token format"}
    
    # Decode the payload (second part)
    payload_b64 = parts[1]
    # Add padding if needed
    padding = len(payload_b64) % 4
    if padding > 0:
        payload_b64 += '=' * (4 - padding)
    
    try:
        payload_bytes = base64.urlsafe_b64decode(payload_b64)
        payload_str = payload_bytes.decode('utf-8')
        payload = json.loads(payload_str)
        return payload
    except Exception as e:
        return {"error": f"Failed to decode payload: {str(e)}"}

if __name__ == "__main__":
    if len(sys.argv) > 1:
        token = sys.argv[1]
    else:
        token = input("Enter JWT token: ")
    
    payload = decode_jwt_payload(token)
    print(json.dumps(payload, indent=2))
