"""
Sessions table tools
"""

import uuid
from datetime import datetime

from . import config
from .user import get_user, set_user_auth
from .dynamodb_tables import get_sessions_table

sessions_table = get_sessions_table(config.SESSIONS_TABLE)

async def new_session(username: str):
    """Create a new session"""
    session_key = get_user(username).get('AuthKey')
    if session_key:
        # check if the session is in use
        response = sessions_table.get_item(
            Key={"SessionKey": session_key}
        ).get('Item', {})

        if response.get('Active'):
            sessions_table.update_item(
                Key={"SessionKey": session_key},
                UpdateExpression="SET Active = :active, LastModified = :last_modified",
                ExpressionAttributeValues={":active": False, ":last_modified": str(datetime.utcnow())},
            )
    
    session_key = str(uuid.uuid4())
    sessions_table.put_item(Item={
        "SessionKey": session_key,
        "UserName": username,
        "Active": True,
        "Created": str(datetime.utcnow()),
        "LastModified": str(datetime.utcnow())
    })

    await set_user_auth(username, session_key)

    return session_key

def validate_session_key(session_key: str):
    """Verify the session key is active"""
    response = sessions_table.get_item(
        Key={"SessionKey": session_key}
    ).get('Item', {})

    if response.get('Active'):
        return response.get('UserName')
    return None

def invalidate_session(session_key: str):
    """Set the session key to inactive"""
    response = sessions_table.get_item(
        Key={"SessionKey": session_key}
    ).get('Item', {})

    if response.get('Active'):
        sessions_table.update_item(
            Key={"SessionKey": session_key},
            UpdateExpression="SET Active = :active, LastModified = :last_modified",
            ExpressionAttributeValues={":active": False, ":last_modified": str(datetime.utcnow())}
        )
