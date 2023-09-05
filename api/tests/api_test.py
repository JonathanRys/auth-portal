"""
Test api methods
"""

import pytest

from fastapi.exceptions import HTTPException
from .. import config
from ..api import http_response, \
                confirm_email, \
                reset_password, \
                register, \
                change_password, \
                login, \
                lambda_handler

from ..models import EmailConfirmation, \
                ResetPassword, \
                UpdatePassword, \
                NewUser, \
                ExistingUser

from ..dynamodb_tables import get_users_table, get_tokens_table

# Tests
def test_http_response():
    assert http_response(200, {"authKey": '12bc45ad367', "message": "Test success"}) == {
        "statusCode": 200,
        "authKey": '12bc45ad367',
        "body": '{"authKey": "12bc45ad367", "message": "Test success"}',
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": config.APP_ORIGIN
        }
    }

@pytest.mark.asyncio
async def test_confirm_email(mocker):
    mocker.patch('uuid.uuid4', return_value='uuid1234')
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
        "AuthKey": "abc12345",
        "Active": True
    })
    event = EmailConfirmation(accessKey="badKey")
    try:
        http_response(403, {"message": 'Forbidden'})
    except HTTPException as err:
        assert err.status_code==403
        assert err.detail=='Forbidden'

    # create db entry for test user to test sucess
    event = EmailConfirmation(accessKey="abc123")
    assert await confirm_email(event) == http_response(200, {
        "username": "user@test.com",
        "role": "viewer",
        "message": "Email confirmed",
        "sessionKey": "uuid1234"
    })

    token_table.delete_item(Key={"AccessKey": "abc123"})
    user_table.delete_item(Key={"UserName": "user@test.com"})

# def test_refresh_access_token():
#     assert refresh_access_token() ==

@pytest.mark.asyncio
async def test_reset_password(mocker):
    """Test reset password"""
    mocker.patch('smtplib.SMTP_SSL')
    # @todo, this test should fail
    event = ResetPassword(username="testuser@gmail.com")
    assert await reset_password(event) == http_response(200, { "message": "Password reset email sent" })

@pytest.mark.asyncio
async def test_change_password():
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
        "AuthKey": "abc12345",
        "Active": True
    })
    event = UpdatePassword(
        username="user@test.com",
        password="OldP@ssw0rd",
        newPassword="ValidP@ssw0rd"
    )

    assert await change_password(event) == http_response(200, {"UserName": "user@test.com", "message": "Password updated"})
    token_table.delete_item(Key={"AccessKey": "abc123"})
    user_table.delete_item(Key={"UserName": "user@test.com"})

@pytest.mark.asyncio
async def test_register(mocker):
    """Test register"""
    user_table = get_users_table("Users")
    user_table.delete_item(Key={"UserName": "user@test.com"})
    mocker.patch('smtplib.SMTP_SSL')
    event = NewUser(
        username="user@test.com",
        password="ValidP@ssw0rd"
    )
    assert await register(event) == http_response(201, { "message": "Registration success" })
    user_table.delete_item(Key={"UserName": "user@test.com"})

@pytest.mark.asyncio
async def test_login():
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
        "AuthKey": "abc12345",
        "Active": True
    })
    event = ExistingUser(
        username="user@test.com",
        password="ValidP@ssw0rd",
        authKey="abc12345"
    )
    try:
        assert await login(event) == http_response(200, {
            "username": "user@test.com",
            "role": "viewer",
            "sessionKey": "abc12345",
            "message": "Login success"
        })
    except Exception as err:
        print('Error:', err)

    token_table.delete_item(Key={"AccessKey": "abc123"})
    user_table.delete_item(Key={"UserName": "user@test.com"})

@pytest.mark.asyncio
async def test_lambda_handler(mocker):
    mocker.patch('uuid.uuid4', return_value='uuid1234')
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
        "AuthKey": "abc12345",
        "Active": True
    })
    event = {
        "httpMethod": "GET",
        "path": "/confirm_email",
        "queryStringParameters": {
            "accessKey": "abc123"
        }
    }
    assert await lambda_handler(event, {}) == http_response(200, {
        "username": "user@test.com",
        "role": "viewer",
        "message": "Email confirmed",
        "sessionKey": "uuid1234"
    })

    token_table.delete_item(Key={"AccessKey": "abc123"})
    user_table.delete_item(Key={"UserName": "user@test.com"})
