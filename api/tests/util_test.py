"""
Test for util module
"""

from .. import config

from ..util import http_response

def test_http_response():
    """Test hhtp_response"""
    expected_result = {
        "statusCode": 200,
        "authKey": None,
        "body": '{"message": "Success!"}',
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": config.APP_ORIGIN
        }
    }
    assert http_response(200, { "message": "Success!" }) == expected_result
