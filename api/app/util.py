"""
API Utilities
"""

from fastapi import HTTPException
from . import config

# Utilities
def http_response(status_code: int, body: any=None):
    """Generates a standard HTTP response"""
    if status_code >= 400:
        raise HTTPException(status_code=status_code, detail=body.get('message'))

    response = {
        **body,
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": config.APP_ORIGIN
        }
    }

    return response
