"""
API Utilities
"""

import json
import config
from fastapi import HTTPException

# Utilities
def http_response(statusCode: int, body: any=None):
    """Generates a standard HTTP response"""
    if statusCode >= 400:
        raise HTTPException(status_code=statusCode, detail=body.get('message'))

    response = {
        "statusCode": statusCode,
        "authKey": body.get('authKey') if body else None,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": config.APP_ORIGIN
        }
    }

    if body is not None:
        response['body'] = json.dumps(body)

    return response