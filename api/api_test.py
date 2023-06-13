import pytest

from . import config
from api import http_response, \
                is_valid_password, \
                is_valid_user, \
                confirm_email, \
                reset_password, \
                register, \
                change_password, \
                login, \
                lambda_handler


# Tests
def test_http_response():
    assert http_response(200, {"accessKey": '12bc45ad367', "message": "Test success"}) == {
        "statusCode": 200,
        "accessToken": '12bc45ad367',
        "body": '{"accessKey": "12bc45ad367", "message": "Test success"}',
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": config.APP_ORIGIN
        }
    }

def test_is_valid_password():
    assert is_valid_password('Thi$Shouldw0rk') == True
    assert is_valid_password('thi$Shouldntw0rk') == False
    assert is_valid_password('ThisShouldntw0rk') == False
    assert is_valid_password('Thi$Shouldntwork') == False
    assert is_valid_password('thi$w0ntwork') == False
    assert is_valid_password('Nf6$') == False
    assert is_valid_password('THI$W0NTWORK') == False
    assert is_valid_password('thiswontwork') == False

def test_is_valid_user():
    assert is_valid_user('testuser@gmail.com') == True
    assert is_valid_user('TestUser') == False
    assert is_valid_user('Test@com') == False

def test_confirm_email():
    assert confirm_email({ "accessKey": "badKey" }) == http_response(403, 'Forbidden')
    # create db entry for test user to test sucess
    assert confirm_email({ "accessKey": "test" }) == http_response(200, {"accessKey": "test", "message": "Email confirmed"})

# def test_refresh_access_token():
#     assert refresh_access_token() ==

def test_reset_password():
    assert reset_password({ "username": "testuser@gmail.com" }) == http_response(200, { "message": "Password reset email sent" })

def test_change_password():
    event = {
        "username": "testuser@gmail.com",
        "password": "pastword",
        "new_password": "password",
        "acessKey": "test"
    }
    assert change_password(event) == http_response(200, {"accessKey": "test", "message": "Password updated"})

def test_register():
    event = {"username": "testuser@gmail.com", "password": "password"}
    assert register(event) == http_response(200, { "message": "Registration success" })

def test_login():
    event = {
        "username": "testuser@gmail.com",
        "password": "password",
        "acessKey": "test"
    }
    assert login(event) == http_response(200, {"accessKey": "test", "message": "Login success"})

def test_lambda_handler():
    event = {
        "httpMethod": "GET",
        "path": "/confirm",
        "queryStringParameters": {
            "acessKey": "test"
        }
    }
    assert lambda_handler(event) == http_response(200, {"accessKey": "test", "message": "Email confirmed"})

