"""
Test for session module
"""

import pytest
from app import config

from app.session import new_session, validate_session_key, invalidate_session
from app.dynamodb_tables import get_sessions_table, get_users_table

sessions_table = get_sessions_table(config.SESSIONS_TABLE)
users_table = get_users_table(config.USERS_TABLE)

@pytest.mark.asyncio
async def test_new_session(mocker):
    """Test new_session"""
    mocker.patch('uuid.uuid4', return_value='uuid1234')
    username = "test@gmail.com"
    session_key = "uuid1234"

    users_table.put_item(Item={
        "AuthKey": 'invalid',
        "UserName": username,
        "Active": True
    })

    assert await new_session(username) == session_key

    response = sessions_table.get_item(
        Key={"SessionKey": session_key}
    ).get('Item', {})

    assert response.get('UserName') == username
    
    # check that it sets user auth
    response = users_table.get_item(
        Key={"UserName": username}
    ).get('Item', {})

    assert response.get('AuthKey') == session_key

    # clean up
    users_table.delete_item(Key={"UserName": username})
    sessions_table.delete_item(Key={"SessionKey": session_key})

def test_validate_session_key(mocker):
    """Test validate_session_key"""
    mocker.patch('uuid.uuid4', return_value='uuid1234')
    username = "test@gmail.com"
    session_key = "uuid1234"

    # Test it returns None when no value has been set
    assert validate_session_key(session_key) is None

    # Test active records return properly
    sessions_table.put_item(Item={
        "SessionKey": session_key,
        "UserName": username,
        "Active": True
    })
    assert validate_session_key(session_key) == username
    
    # Test inactive records return None
    sessions_table.update_item(
        Key={"SessionKey": session_key},
        UpdateExpression="SET Active = :active",
        ExpressionAttributeValues={":active": False}
    )
    assert validate_session_key(session_key) is None

    # clean up
    sessions_table.delete_item(Key={"SessionKey": session_key})

def test_invalidate_session():
    """Test invalidate_session"""
    session_key = "uuid1234"
    username = "test@gmail.com"

    sessions_table.put_item(Item={
        "SessionKey": session_key,
        "UserName": username,
        "Active": True
    })

    assert invalidate_session(session_key) == None

    response = sessions_table.get_item(
        Key={"SessionKey": session_key}
    ).get('Item', {})

    assert response.get('Active') == False

    # clean up
    sessions_table.delete_item(Key={"SessionKey": session_key})
