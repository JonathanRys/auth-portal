"""Tests for the user module"""

import pytest

from .. import config
from ..dynamodb_tables import get_users_table

from ..user import get_user, \
                update_timestamp, \
                validate_auth_key, \
                is_valid_user, \
                is_valid_password, \
                set_user_auth, \
                create_new_user, \
                set_user_role, \
                update_password

users_table = get_users_table(config.USERS_TABLE)

def test_is_valid_password():
    """Test is_valid_password"""
    assert is_valid_password('thi$shouldntw0rk') == False
    assert is_valid_password('ThisShouldntw0rk') == False
    assert is_valid_password('Thi$Shouldntwork') == False
    assert is_valid_password('thi$w0ntwork') == False
    assert is_valid_password('Nf6$') == False
    assert is_valid_password('THI$W0NTWORK') == False
    assert is_valid_password('thiswontwork') == False
    assert is_valid_password('Thi$Shouldw0rk') == True

def test_is_valid_user():
    """Test is_valid_user"""
    assert is_valid_user('TestUser') == False
    assert is_valid_user('Testgmail.com') == False
    assert is_valid_user('testuser@gmail.com') == True

@pytest.fixture(autouse=True)
def create_records():
    """Create user record for testing"""
    username = "test@gmail.com"
    password = "P@ssw0rd"

    users_table.put_item(Item={
        "UserName": username,
        "Password": password,
        "AuthKey": "abc123",
        "Role": 'viewer',
        "Active": True
    })

    yield

    users_table.delete_item(Key={"UserName": username})

def test_validate_auth_key():
    """Test validate_auth_key"""
    username = "test@gmail.com"
    auth_key = "abc123"
    assert validate_auth_key(username, auth_key) == auth_key

def test_create_new_user():
    """Test create_new_user"""
    username = "test@gmail.com"
    password = "P@ssw0rd"
    assert create_new_user(username, password) == None

def test_get_user():
    """Test get_user"""
    username = "test@gmail.com"

    expected_result = {
        'Active': True,
        "AuthKey": "abc123",
        'Password': 'P@ssw0rd',
        "Role": 'viewer',
        'UserName': 'test@gmail.com'
    }
    assert get_user(username) == expected_result

def test_update_timestamp():
    """Test update_timestamp"""
    username = "test@gmail.com"
    response = update_timestamp(username)
    response_status = response.get('ResponseMetadata', {}).get('HTTPStatusCode')

    assert response_status == 200

@pytest.mark.asyncio
async def test_set_user_auth():
    """Test set_user_auth"""
    username = "test@gmail.com"
    auth_key = "abc123"
    response =  await set_user_auth(username, auth_key)
    response_status = response.get('ResponseMetadata', {}).get('HTTPStatusCode')

    assert response_status == 200

@pytest.mark.asyncio
async def test_set_user_role():
    """Test set_user_role"""
    username = "test@gmail.com"
    role = "viewer"
    response = await set_user_role(username, role)
    response_status = response.get('ResponseMetadata', {}).get('HTTPStatusCode')

    assert response_status == 200

@pytest.mark.asyncio
async def test_update_password():
    """Test update_password"""
    username = "test@gmail.com"
    password = "P@ssw0rd"

    response = await update_password(username, password)
    response_status = response.get('ResponseMetadata', {}).get('HTTPStatusCode')

    assert response_status == 200
