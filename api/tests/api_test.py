"""
Test api methods
"""

import pytest

from fastapi.exceptions import HTTPException
from app import config
from app.api import confirm_email, \
                reset_password, \
                register, \
                set_new_password, \
                update_password, \
                login

from app.models import EmailConfirmation, \
                ResetPassword, \
                UpdatePassword, \
                NewUser, \
                ExistingUser, \
                SetNewPassword

from app.dynamodb_tables import get_users_table, get_tokens_table

from app.util import http_response

users_table = get_users_table(config.USERS_TABLE)
tokens_table = get_tokens_table(config.TOKENS_TABLE)

@pytest.mark.asyncio
async def test_confirm_email(mocker):
    """Test confirm_email"""
    mocker.patch('uuid.uuid4', return_value='uuid1234')

    tokens_table.put_item(Item={
        "UserName": "user@test.com",
        "AccessKey": "abc123",
        "Valid": True
    })
    users_table.put_item(Item={
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
        "authKey": "uuid1234",
        "sessionKey": "uuid1234",
        "message": "Email confirmed"
        
    })

    tokens_table.delete_item(Key={"AccessKey": "abc123"})
    users_table.delete_item(Key={"UserName": "user@test.com"})

@pytest.mark.asyncio
async def test_reset_password(mocker):
    """Test reset password"""
    mocker.patch('uuid.uuid4', return_value='uuid1234')
    mocker.patch('smtplib.SMTP_SSL')
    # @todo, this test should fail
    event = ResetPassword(username="testuser@gmail.com")
    assert await reset_password(event) == http_response(200, { "message": "Password reset email sent." })
    tokens_table.delete_item(Key={"AccessKey": "uuid1234"})

@pytest.mark.asyncio
async def test_set_new_password(mocker):
    """Test set_new_password"""
    mocker.patch('uuid.uuid4', return_value='uuid1234')
    tokens_table.put_item(Item={
        "UserName": "user@test.com",
        "AccessKey": "abc123",
        "Valid": True
    })
    users_table.put_item(Item={
        "UserName": "user@test.com",
        "Password": "1523bc8e0ba72600083dcf5dfb37a8582994183d784a747e3f6fbc963dc882b6",
        "RateLimit": 1000,
        "LastLogin": '2023-08-25 12:12:56.530613',
        "AuthRole": "viewer",
        "AuthKey": "abc12345",
        "Active": True
    })
    event = SetNewPassword(
        username="user@test.com",
        password="OldP@ssw0rd",
        accessKey="abc123"
    )

    assert await set_new_password(event) == http_response(200, {
        "username": "user@test.com",
        "role": "viewer",
        "authKey": "abc12345",
        "sessionKey": "uuid1234",
        "message": "New password set."
    })
    tokens_table.delete_item(Key={"AccessKey": "abc123"})
    users_table.delete_item(Key={"UserName": "user@test.com"})

@pytest.mark.asyncio
async def test_update_password(mocker):
    """Test update_password"""
    mocker.patch('uuid.uuid4', return_value='uuid1234')
    tokens_table.put_item(Item={
        "UserName": "user@test.com",
        "AccessKey": "abc123",
        "Valid": True
    })
    users_table.put_item(Item={
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
        newPassword="NewP@ssw0rd"
    )

    assert await update_password(event) == http_response(200, {
        "username": "user@test.com",
        "role": "viewer",
        "authKey": "abc12345",
        "sessionKey": "uuid1234",
        "message": "Password updated."})
    tokens_table.delete_item(Key={"AccessKey": "abc123"})
    users_table.delete_item(Key={"UserName": "user@test.com"})

@pytest.mark.asyncio
async def test_register(mocker):
    """Test register"""
    mocker.patch('uuid.uuid4', return_value='uuid1234')
    mocker.patch('smtplib.SMTP_SSL')

    users_table.delete_item(Key={"UserName": "user@test.com"})
    event = NewUser(
        username="user@test.com",
        password="ValidP@ssw0rd"
    )
    assert await register(event) == http_response(201, { "message": "Registration success" })
    users_table.delete_item(Key={"UserName": "user@test.com"})
    tokens_table.delete_item(Key={"AccessKey": "uuid1234"})

@pytest.mark.asyncio
async def test_login(mocker):
    """Test login"""
    mocker.patch('uuid.uuid4', return_value='uuid1234')
    tokens_table.put_item(Item={
        "UserName": "user@test.com",
        "AccessKey": "abc123",
        "Valid": True
    })
    users_table.put_item(Item={
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
    assert await login(event) == http_response(200, {
        "username": "user@test.com",
        "role": "viewer",
        "authKey": "abc12345",
        "sessionKey": "uuid1234",
        "message": "Login success"
    })

    tokens_table.delete_item(Key={"AccessKey": "abc123"})
    users_table.delete_item(Key={"UserName": "user@test.com"})
