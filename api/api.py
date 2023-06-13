import re
import json
import hashlib
import logging

from datetime import datetime

from . import config
from .dynamodb_tables import get_user_table
from .registration import validate_acessKey, send_reset_password_email, send_registration_email

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

user_table = get_user_table(config.USER_TABLE)

# Utilities
def http_response(statusCode: int, body: any=None):
    """Generates a standard HTTP response"""
    response = {
        "statusCode": statusCode,
        "accessToken": body.get('accessToken'),
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": config.APP_ORIGIN
        }
    }

    if body is not None:
        response['body'] = json.dumps(body)

    return response

def is_valid_password(password: str):
    """Checks the format of the password"""
    pw_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%]).{8,24}$'
    return re.match(password, pw_regex)

def is_valid_user(username: str):
    """Checks the format of the username"""
    email_regex = r"/^[a-zA-Z0-9.!#$%&'*+\/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/"
    return re.match(username, email_regex)

# Handler methods
def confirm_email(params: object):
    """Confirm registration email endpoint (GET)"""
    acessKey = params.get('accessKey')
    username = validate_acessKey(acessKey)
    if username:
        user_table.update_item(Item={
            "UserName": username,
            "AccessKey": acessKey,
            "LastLogin": datetime.now(),
            "Roles": "Viewer",
            "Valid": True
        })
        return http_response(200, {"accessKey": acessKey, "message": "Email confirmed"})
    return http_response(403, 'Forbidden')

def refresh_access_token(params: object):
    """Refresh the user's access token (GET)"""
    pass

def reset_password(event: object):
    """Allow user to reset their password (POST)"""
    username = event.get('username')
    # send reset password link in an email
    if send_reset_password_email(username):
        return http_response(200, { "message": "Password reset email sent" })
    return http_response(500, 'Server error')

def change_password(event: object):
    """Allow user to change their password (POST)"""
    username = event.get('username')
    password = event.get('password')
    new_password = event.get('new_password')
    acessKey = event.get('acessKey')

    # validate data
    if not is_valid_user(username) or \
       not is_valid_password(password) or \
       not is_valid_password(new_password):
        # send alert, someone is hacking or front-end validation is broken 
        return http_response(403, 'Forbidden')

    # validate user
    db_username = validate_acessKey(acessKey)
    if db_username and db_username == username:
        response = user_table.get_item(Key={"username": username})
        if "Item" in response:
            pw_hash = response.get('Item', {}).get('Password')
            if pw_hash != hashlib.sha3_256(password).hexdigest():
                return http_response(401, "Incorrect Password")

            # update password
            user_table.update_item(Item={"UserName": username, "Password": new_password})

    return http_response(200, {"accessKey": acessKey, "message": "Password updated"})

def register(event: object):
    """Allow the user to register (POST)"""
    username = event.get('username')
    password = event.get('password')
    # validate / scrub data
    if not is_valid_user(username) or not is_valid_password(password):
        # send alert, someone is hacking or front-end validation is broken 
        return http_response(403, 'Forbidden')

    # check for existing records
    response = user_table.get_item(Key={"UserName": username})
    if "Item" in response:
        if username == response.get('Item', {}).get('UserName'):
            return http_response(409, 'Username taken')

    # hash password
    pw_hash = hashlib.sha3_256(password).hexdigest()

    # write to DB
    try:
        user_table.put_item(Item={"UserName": username, "Password": pw_hash})
        send_registration_email(username)
    except Exception as e:
        print(f'Error registering user {username}: {e}')
        return http_response(500, 'Server error')

    # craft response
    return http_response(200, { "message": "Registration success" })

def login(event: object):
    """Allow the user to login (POST)"""
    username = event.get('username')
    password = event.get('password')
    acessKey = event.get('acessKey')
    # validate / scrub data
    if not is_valid_user(username) or not is_valid_password(password):
        # @todo send alert, someone is hacking or front-end validation is broken 
        return http_response(403, 'Forbidden')

    if not acessKey:
        return http_response(401, 'Token expected')

    response = user_table.get_item(Key={"username": username})
    if "Item" in response:
        
        pw_hash = response.get('Item', {}).get('Password')
        if pw_hash != hashlib.sha3_256(password).hexdigest():
            return http_response(401, "Unauthorized")
        if acessKey != response.get('Item', {}).get('AccessKey'):
            # user needs to confirm their email
            return http_response(401, 'Token invalid')
    try:
        user_table.update_item(Item={"UserName": username, "LastLogin": datetime.now()})
    except Exception as e:
        logger.warn(f'Error updating user {username}: {e}')
        return http_response(500, 'Server Error')

    return http_response(200, {"accessKey": acessKey, "message": "Login success"})

# Handler
routes = {
    "GET": {
        "/refresh": refresh_access_token,
        "/confirm": confirm_email
    },
    "POST": {
        "/login": login,
        "/register": register,
        "/resetPassword": reset_password,
        "/changePassword": change_password
    }
}

def lambda_handler(event: any, context: any):
    httpMethod = event.get('httpMethod')
    path = event.get('path')
    
    # @todo get the user's IP
    ip_address = None

    handler = routes.get(httpMethod, {}).get(path)

    if httpMethod == 'GET':
        qs_params = event['queryStringParameters']
        return handler(qs_params)
    elif httpMethod == 'POST':
        return handler(event)
