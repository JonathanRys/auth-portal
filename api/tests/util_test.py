"""
Test for util module
"""

from ..app import config

from ..app.util import http_response

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

# Tests
def test_http_response_with_data():
    """Test """
    assert http_response(200, {"authKey": '12bc45ad367', "message": "Test success"}) == {
        "statusCode": 200,
        "authKey": '12bc45ad367',
        "body": '{"authKey": "12bc45ad367", "message": "Test success"}',
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": config.APP_ORIGIN
        }
    }