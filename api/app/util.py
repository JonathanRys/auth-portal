"""
API Utilities
"""

import json
from fastapi import HTTPException
from . import config

# Utilities
def http_response(status_code: int, body: any=None):
    """Generates a standard HTTP response"""
    if status_code >= 400:
        raise HTTPException(status_code=status_code, detail=body.get('message'))
    x = {**body}
    print(f'body: {x}')

    response = {
        **body,
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": config.APP_ORIGIN
        }
    }

    if body is not None:
        response['body'] = json.dumps(body)

    return response