"""
Test api methods
"""

from .. import config
from ..api import http_response, \
                is_valid_password, \
                is_valid_user, \
                confirm_email, \
                reset_password, \
                register, \
                change_password, \
                login, \
                lambda_handler

from ..dynamodb_tables import get_users_table, get_tokens_table

# Tests
def test_http_response():
    assert http_response(200, {"AccessKey": '12bc45ad367', "message": "Test success"}) == {
        "statusCode": 200,
        "AccessKey": '12bc45ad367',
        "body": '{"AccessKey": "12bc45ad367", "message": "Test success"}',
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": config.APP_ORIGIN
        }
    }

def test_is_valid_password():
    assert is_valid_password('thi$shouldntw0rk') == False
    assert is_valid_password('ThisShouldntw0rk') == False
    assert is_valid_password('Thi$Shouldntwork') == False
    assert is_valid_password('thi$w0ntwork') == False
    assert is_valid_password('Nf6$') == False
    assert is_valid_password('THI$W0NTWORK') == False
    assert is_valid_password('thiswontwork') == False
    assert is_valid_password('Thi$Shouldw0rk') == True

def test_is_valid_user():
    assert is_valid_user('TestUser') == False
    assert is_valid_user('Testgmail.com') == False
    assert is_valid_user('testuser@gmail.com') == True

def test_confirm_email():
    token_table = get_tokens_table("Tokens")
    token_table.put_item(Item={
        "UserName": "user@test.com",
        "AccessKey": "abc123",
        "Valid": True
    })
    user_table = get_users_table("Users")
    user_table.put_item(Item={
        "UserName": "user@test.com",
        "Password": "password",
        "RateLimit": 1000,
        "LastLogin": '2023-08-25 12:12:56.530613',
        "AuthRole": "viewer",
        "ApiKey": "abc12345",
        "Active": True
    })
    assert confirm_email({ "accessKey": "badKey" }) == http_response(403, {"message": 'Forbidden'})
    # create db entry for test user to test sucess
    assert confirm_email({ "accessKey": "abc123" }) == http_response(200, {"AccessKey": "abc123", "message": "Email confirmed"})

    token_table.delete_item(Key={"AccessKey": "abc123"})
    user_table.delete_item(Key={"UserName": "user@test.com"})

# def test_refresh_access_token():
#     assert refresh_access_token() ==

def test_reset_password(mocker):
    """Test reset password"""
    mocker.patch('smtplib.SMTP_SSL')
    # @todo, this test should fail
    assert reset_password({ "username": "testuser@gmail.com" }) == http_response(200, { "message": "Password reset email sent" })

def test_change_password():
    token_table = get_tokens_table("Tokens")
    token_table.put_item(Item={
        "UserName": "user@test.com",
        "AccessKey": "abc123",
        "Valid": True
    })
    user_table = get_users_table("Users")
    user_table.put_item(Item={
        "UserName": "user@test.com",
        "Password": "1523bc8e0ba72600083dcf5dfb37a8582994183d784a747e3f6fbc963dc882b6",
        "RateLimit": 1000,
        "LastLogin": '2023-08-25 12:12:56.530613',
        "AuthRole": "viewer",
        "ApiKey": "abc12345",
        "Active": True
    })
    event = {
        "username": "user@test.com",
        "password": "OldP@ssw0rd",
        "new_password": "ValidP@ssw0rd",
        "ApiKey": "abc12345"
    }
    assert change_password(event) == http_response(200, {"UserName": "user@test.com", "message": "Password updated"})
    token_table.delete_item(Key={"AccessKey": "abc123"})
    user_table.delete_item(Key={"UserName": "user@test.com"})

def test_register(mocker):
    """Test register"""
    user_table = get_users_table("Users")
    user_table.delete_item(Key={"UserName": "user@test.com"})
    mocker.patch('smtplib.SMTP_SSL')
    event = {"username": "user@test.com", "password": "ValidP@ssw0rd"}
    assert register(event) == http_response(200, { "message": "Registration success" })
    user_table.delete_item(Key={"UserName": "user@test.com"})

def test_login():
    token_table = get_tokens_table("Tokens")
    token_table.put_item(Item={
        "UserName": "user@test.com",
        "AccessKey": "abc123",
        "Valid": True
    })
    user_table = get_users_table("Users")
    user_table.put_item(Item={
        "UserName": "user@test.com",
        "Password": "8d3f8e0d344be93893a5ca049c2ce630471c5f7557156487bfd7e98fb82f1e44",
        "RateLimit": 1000,
        "LastLogin": '2023-08-25 12:12:56.530613',
        "AuthRole": "viewer",
        "ApiKey": "abc12345",
        "Active": True
    })
    event = {
        "username": "user@test.com",
        "password": "ValidP@ssw0rd",
        "accessKey": "abc123"
    }
    assert login(event) == http_response(200, {"AccessKey": "abc123", "message": "Login success"})

    token_table.delete_item(Key={"AccessKey": "abc123"})
    user_table.delete_item(Key={"UserName": "user@test.com"})

def test_lambda_handler():
    token_table = get_tokens_table("Tokens")
    token_table.put_item(Item={
        "UserName": "user@test.com",
        "AccessKey": "abc123",
        "Valid": True
    })
    user_table = get_users_table("Users")
    user_table.put_item(Item={
        "UserName": "user@test.com",
        "Password": "8d3f8e0d344be93893a5ca049c2ce630471c5f7557156487bfd7e98fb82f1e44",
        "RateLimit": 1000,
        "LastLogin": '2023-08-25 12:12:56.530613',
        "AuthRole": "viewer",
        "ApiKey": "abc12345",
        "Active": True
    })
    event = {
        "httpMethod": "GET",
        "path": "/confirm",
        "queryStringParameters": {
            "accessKey": "abc123"
        }
    }
    assert lambda_handler(event, {}) == http_response(200, {"AccessKey": "abc123", "message": "Email confirmed"})

    token_table.delete_item(Key={"AccessKey": "abc123"})
    user_table.delete_item(Key={"UserName": "user@test.com"})
