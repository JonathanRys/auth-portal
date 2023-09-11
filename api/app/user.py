"""
User table tools
"""
import re
import hashlib
from datetime import datetime

from botocore.exceptions import ClientError

from . import logger
from . import config
from .util import http_response
from .dynamodb_tables import get_users_table

user_table = get_users_table(config.USERS_TABLE)

def is_valid_password(password: str) -> bool:
    """Checks the format of the password"""
    pw_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[_!@#$%]).{8,24}$'
    return bool(re.match(pw_regex, password))

def is_valid_user(username: str) -> bool:
    """Checks the format of the username"""
    email_regex = r"([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\"([]!#-[^-~ \t]|(\\[\t -~]))+\")@([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\[[\t -Z^-~]*])"
    return bool(re.match(email_regex, username))

def compare_to_hash(password: str, user_hash: str):
    """Compares a str against a hash"""
    pw_hash = hashlib.sha3_256(password.encode()).hexdigest()
    return pw_hash == user_hash

def validate_auth_key(username: str):
    """Verify the user's auth key"""
    db_auth_key = get_user(username).get('AuthKey')
    return db_auth_key

def create_new_user(username: dict, password: str):
    """Create a new user record"""
    pw_hash = hashlib.sha3_256(password.encode()).hexdigest()
    user_table.put_item(Item={"UserName": username, "Password": pw_hash})

def get_user(username: str) -> dict:
    """Gets the user record"""
    response = user_table.get_item(Key={"UserName": username})
    return response.get('Item', {})

def update_timestamp(username: str):
    """Updates the LastLogin timestamp"""
    try:
        return user_table.update_item(
            Key={"UserName": username},
            UpdateExpression="SET LastLogin = :last_login",
            ExpressionAttributeValues={":last_login": str(datetime.utcnow())}
        )
    except ClientError as err:
        logger.warning('Error updating user %s: %s', username, err)
        return http_response(500, {"message": 'Server Error'})

async def set_user_auth(username: str, auth_key: str):
    """Sets the authKey for the user"""
    return user_table.update_item(
        Key={"UserName": username},
        UpdateExpression="SET LastLogin = :last_login, AuthKey = :auth_key, Valid = :valid",
        ExpressionAttributeValues={
            ":last_login": str(datetime.utcnow()),
            ":auth_key": auth_key,
            ":valid": True
        }
    )

async def set_user_role(username: str, role: str):
    """Sets the role for the user"""
    return user_table.update_item(
        Key={"UserName": username},
        UpdateExpression="SET AuthRole = :role",
        ExpressionAttributeValues={":role": role}
    )

async def update_user_password(username: str, new_password: str):
    """Update the user's password"""
    pw_hash = hashlib.sha3_256(new_password.encode()).hexdigest()
    return user_table.update_item(
        Key={"UserName": username},
        UpdateExpression="SET Password = :password",
        ExpressionAttributeValues={ ":password": pw_hash }
    )
