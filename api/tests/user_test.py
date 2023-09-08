"""Tests for the user module"""

import hashlib

import pytest

from app import config
from app.dynamodb_tables import get_users_table

from app.user import get_user, \
                update_timestamp, \
                validate_auth_key, \
                is_valid_user, \
                is_valid_password, \
                compare_to_hash, \
                set_user_auth, \
                create_new_user, \
                set_user_role, \
                update_password

users_table = get_users_table(config.USERS_TABLE)

def test_is_valid_password():
    """Test is_valid_password"""
    assert is_valid_password('thi$shouldntw0rk') is False
    assert is_valid_password('ThisShouldntw0rk') is False
    assert is_valid_password('Thi$Shouldntwork') is False
    assert is_valid_password('thi$w0ntwork') is False
    assert is_valid_password('Nf6$') is False
    assert is_valid_password('THI$W0NTWORK') is False
    assert is_valid_password('thiswontwork') is False
    assert is_valid_password('Thi$Shouldw0rk') is True

def test_is_valid_user():
    """Test is_valid_user"""
    assert is_valid_user('TestUser') is False
    assert is_valid_user('Testgmail.com') is False
    assert is_valid_user('testuser@gmail.com') is True

def test_compare_to_hash():
    """Test compare_to_hash"""
    password = 'testpass'
    pw_hash = hashlib.sha3_256(password.encode()).hexdigest()
    assert compare_to_hash(password, pw_hash)

@pytest.fixture(autouse=True)
def create_records():
    """Create and destroy user record for testing"""
    username = "test@gmail.com"
    password = "P@ssw0rd"

    users_table.put_item(Item={
        "UserName": username,
        "Password": hashlib.sha3_256(password.encode()).hexdigest(),
        "AuthKey": "abc123",
        "AuthRole": 'viewer',
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
    username = "testuser@gmail.com"
    password = "P@ssw0rd"
    assert create_new_user(username, password) is None

    response = users_table.get_item(Key={"UserName": username}).get('Item', {})

    assert response.get('UserName') == username
    assert response.get('Password') == hashlib.sha3_256(password.encode()).hexdigest()
    assert response.get('AuthKey') is None
    assert response.get('Active') is None

    # This user has a different name than the test fixture
    users_table.delete_item(Key={"UserName": username})
    
def test_get_user():
    """Test get_user"""
    username = "test@gmail.com"
    password = "P@ssw0rd"

    expected_result = {
        'Active': True,
        "AuthKey": "abc123",
        'Password': hashlib.sha3_256(password.encode()).hexdigest(),
        "AuthRole": 'viewer',
        'UserName': 'test@gmail.com'
    }
    assert get_user(username) == expected_result

def test_update_timestamp():
    """Test update_timestamp"""
    username = "test@gmail.com"

    response = users_table.get_item(Key={"UserName": username}).get('Item', {})
    assert response.get('LastLogin') is None

    response = update_timestamp(username)
    response_status = response.get('ResponseMetadata', {}).get('HTTPStatusCode')

    assert response_status == 200

    response = users_table.get_item(Key={"UserName": username}).get('Item', {})
    assert response.get('LastLogin') is not None

@pytest.mark.asyncio
async def test_set_user_auth():
    """Test set_user_auth"""
    username = "test@gmail.com"
    auth_key = "xyz789"

    response = users_table.get_item(Key={"UserName": username}).get('Item', {})
    assert response.get('AuthKey') == 'abc123'

    response =  await set_user_auth(username, auth_key)
    response_status = response.get('ResponseMetadata', {}).get('HTTPStatusCode')
    assert response_status == 200

    response = users_table.get_item(Key={"UserName": username}).get('Item', {})
    assert response.get('AuthKey') == 'xyz789'

@pytest.mark.asyncio
async def test_set_user_role():
    """Test set_user_role"""
    username = "test@gmail.com"
    role = "editor"
    
    response = users_table.get_item(Key={"UserName": username}).get('Item', {})
    assert response.get('AuthRole') == 'viewer'

    response = await set_user_role(username, role)
    response_status = response.get('ResponseMetadata', {}).get('HTTPStatusCode')
    assert response_status == 200

    response = users_table.get_item(Key={"UserName": username}).get('Item', {})
    assert response.get('AuthRole') == 'editor'

@pytest.mark.asyncio
async def test_update_password():
    """Test update_password"""
    username = "test@gmail.com"
    password = "Super5e(ret"

    response = users_table.get_item(Key={"UserName": username}).get('Item', {})
    assert response.get('Password') == hashlib.sha3_256("P@ssw0rd".encode()).hexdigest()

    response = await update_password(username, password)
    response_status = response.get('ResponseMetadata', {}).get('HTTPStatusCode')
    assert response_status == 200

    response = users_table.get_item(Key={"UserName": username}).get('Item', {})
    assert response.get('Password') == hashlib.sha3_256(password.encode()).hexdigest()
