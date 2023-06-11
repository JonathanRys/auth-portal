import re
import json
import uuid
import boto3
import hashlib

from datetime import datetime

from . import config
from .registration_email import validate_access_key, send_reset_password_email, send_registration_email

user_table_name = config.USER_TABLE

# connect to DB
dynamodb = boto3.resource('dynamodb')

if user_table_name not in [table.name for table in dynamodb.tables.all()]:
    client = boto3.client('dynamodb')
    client.create_table(
        TableName=user_table_name,
        ProvisionedThroughput={
            "ReadCapacityUnits": 5,
            "WriteCapacityUnits": 5
        },
        KeySchema=[
            {
                "AttributeName": "UserName",
                "KeyType": "HASH"
            }
        ],
        AttributeDefinitions=[
            {
                "AttributeName": "UserName",
                "AttributeType": "S"
            }, {
                "AttributeName": "Password",
                "AttributeType": "S"
            }, {
                "AttributeName": "RateLimit",
                "AttributeType": "N"
            }, {
                "AttributeName": "LastLogin",
                "AttributeType": "S"
            }, {
                "AttributeName": "Roles",
                "AttributeType": "S"
            }

        ],
    )

user_table = dynamodb.Table(user_table_name)

# Utilities
def http_response(statusCode: int, body: any=None):
    """Generates a standard HTTP response"""
    response = {
        "statusCode": statusCode,
        "accessToken": get_access_token(),
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
    """Confirm email endpoint (GET)"""
    access_key = params.get('accessKey')
    username = validate_access_key(access_key)
    if username:
        user_table.update_item(Item={"UserName": username, "AccessKey": access_key})
        return http_response(200, 'Email confirmed')
    return http_response(403, 'Forbidden')

def refresh_access_token(params: object):
    """Refresh the user's access token (GET)"""
    pass

def reset_password(event: object):
    """Allow user to reset their password (POST)"""
    username = event.get('username')
    # send reset password link in an email
    if send_reset_password_email(username):
        return http_response(200, 'Password reset email sent')
    return http_response(500, 'Server error')

def change_password(event: object):
    """Allow user to change their password (POST)"""
    username = event.get('username')
    password = event.get('password')
    new_password = event.get('new_password')
    access_key = event.get('access_key')

    # validate data
    if not is_valid_user(username) or \
       not is_valid_password(password) or \
       not is_valid_password(new_password):
        # send alert, someone is hacking or front-end validation is broken 
        return http_response(403, 'Forbidden')

    # validate user
    db_username = validate_access_key(access_key)
    if db_username and db_username == username:
        response = user_table.get_item(Key={"username": username})
        if "Item" in response:
            pw_hash = response.get('Item', {}).get('Password')
            if pw_hash != hashlib.sha3_256(password).hexdigest():
                return http_response(401, "Unauthorized")

            # update password
            user_table.update_item(Item={"UserName": username, "Password": new_password})

    return http_response(200, 'Password updated')

def registraion(params: object):
    """Validates the registration email link (GET)"""
    access_key = params.get('accessKey')
    username = validate_access_key(access_key)
    
    user_table.update_item(Item={"UserName": username, "LastLogin": datetime.now()})

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
    return http_response(200, 'Registration success')

def login(event: object):
    """Allow the user to login (POST)"""
    username = event.get('username')
    password = event.get('password')
    access_key = event.get('access_key')
    # validate / scrub data
    if not is_valid_user(username) or not is_valid_password(password):
        # @todo send alert, someone is hacking or front-end validation is broken 
        return http_response(403, 'Forbidden')

    if not access_key:
        return http_response(401, 'Token expected')

    response = user_table.get_item(Key={"username": username})
    if "Item" in response:
        
        pw_hash = response.get('Item', {}).get('Password')
        if pw_hash != hashlib.sha3_256(password).hexdigest():
            return http_response(401, "Unauthorized")
        if access_key != response.get('Item', {}).get('AccessKey'):
            # user needs to confirm their email
            return http_response(401, 'Token invalid')
    try:
        user_table.update_item(Item={"UserName": username, "LastLogin": datetime.now()})

    return http_response(200, "Login success")

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
