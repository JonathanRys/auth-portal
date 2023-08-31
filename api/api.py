import re
import json
import hashlib
import logging
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import config
from dynamodb_tables import get_users_table
from registration import validate_access_key, send_reset_password_email, send_registration_email

origins = [
    "http://localhost:3000",
    "http://local.host:3000"
]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['GET', 'POST', 'OPTIONS', 'DELETE', 'HEAD']
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

user_table = get_users_table(config.USER_TABLE)

@app.get('/')
def home():
    return {"test": "success"}

# Utilities
def http_response(statusCode: int, body: any=None):
    """Generates a standard HTTP response"""
    response = {
        "statusCode": statusCode,
        "AccessKey": body.get('AccessKey') if body else None,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": config.APP_ORIGIN
        }
    }

    if body is not None:
        response['body'] = json.dumps(body)

    return response

def is_valid_password(password: str) -> bool:
    """Checks the format of the password"""
    pw_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[_!@#$%]).{8,24}$'
    return bool(re.match(pw_regex, password))

def is_valid_user(username: str) -> bool:
    """Checks the format of the username"""
    email_regex = r"([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\"([]!#-[^-~ \t]|(\\[\t -~]))+\")@([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\[[\t -Z^-~]*])"
    return bool(re.match(email_regex, username))

# Handler methods
@app.get("/confirm")
def confirm_email(params: object):
    """Confirm registration email endpoint (GET)"""
    acessKey = params.get('accessKey')
    username = validate_access_key(acessKey)
    if username:
        user_table.update_item(
            Key={"UserName": username},
            UpdateExpression="SET LastLogin = :last_login, AuthRole = :role, Valid = :valid",
            ExpressionAttributeValues={
                ":last_login": True,
                ":role": "Viewer",
                ":valid": True
            }
        )
        return http_response(200, {"AccessKey": acessKey, "message": "Email confirmed"})
    return http_response(403, {"message": 'Forbidden'})

@app.get("/refresh")
def refresh_access_token(params: object):
    """Refresh the user's access token (GET)"""
    pass

@app.post("/reset_password")
def reset_password(event: object):
    """Allow user to reset their password (POST)"""
    username = event.get('username')
    # send reset password link in an email
    if send_reset_password_email(username):
        return http_response(200, { "message": "Password reset email sent" })
    return http_response(500, {"message": 'Server error'})

@app.post("/change_password")
def change_password(event: object):
    """Allow user to change their password (POST)"""
    username = event.get('username')
    password = event.get('password')
    new_password = event.get('new_password')

    # validate data
    if not is_valid_user(username) or \
       not is_valid_password(password) or \
       not is_valid_password(new_password):
        # send alert, someone is hacking or front-end validation is broken 
        return http_response(403, {"message": 'Forbidden'})

    # validate user
    response = user_table.get_item(Key={"UserName": username})
    if "Item" in response:
        pw_hash = response.get('Item', {}).get('Password')
        if pw_hash != hashlib.sha3_256(password.encode()).hexdigest():
            return http_response(401, "Incorrect Password")

        # update password
        user_table.update_item(
            Key={"UserName": username},
            UpdateExpression="SET Password = :password",
            ExpressionAttributeValues={ ":password": new_password }
        )

    return http_response(200, {"UserName": username, "message": "Password updated"})

class NewUser(BaseModel):
    """Data class for register endpoint"""
    username: str
    password: str

@app.post("/register")
def register(new_user: NewUser):
    """Allow the user to register via (POST)"""
    logger.warning(f'Got request: "{new_user}"')
  
    username = new_user.username
    password = new_user.password
    # validate / scrub data
    if not is_valid_user(username) or not is_valid_password(password):
        # send alert, someone is hacking or front-end validation is broken 
        return http_response(403, {"message": 'Forbidden'})

    # check for existing records
    response = user_table.get_item(Key={"UserName": username})
    if "Item" in response:
        if username == response.get('Item', {}).get('UserName'):
            return http_response(409, {"message": 'Username taken'})

    # hash password
    pw_hash = hashlib.sha3_256(password.encode()).hexdigest()

    # write to DB
    try:
        user_table.put_item(Item={"UserName": username, "Password": pw_hash})
        send_registration_email(username)
    except Exception as e:
        print(f'Error registering user {username}: {e}')
        return http_response(500, {"message": 'Server error'})

    # craft response
    return http_response(200, { "message": "Registration success" })

class ExistingUser(BaseModel):
    """Data class for register endpoint"""
    username: str
    password: str
    accessKey: str

@app.post("/login")
def login(user: ExistingUser):
    """Allow the user to login (POST)"""
    username = user.username
    password = user.password
    access_key = user.accessKey
    # validate / scrub data
    if not is_valid_user(username) or not is_valid_password(password):
        # @todo send alert, someone is hacking or front-end validation is broken
        return http_response(403, {"message": 'Forbidden'})

    if not access_key:
        return http_response(401, {"message": 'Token expected'})

    response = user_table.get_item(Key={"UserName": username})
    if "Item" in response:
        pw_hash = response.get('Item', {}).get('Password')
        if pw_hash != hashlib.sha3_256(password.encode()).hexdigest():
            return http_response(401, {"message": "Unauthorized"})

    if not validate_access_key(access_key) == username:
            # user needs to confirm their email
            return http_response(401, {"message": 'Token invalid'})
    try:
        user_table.update_item(
            Key={"UserName": username},
            UpdateExpression="SET LastLogin = :last_login",
            ExpressionAttributeValues={":last_login": str(datetime.utcnow())}
        )
    except Exception as e:
        logger.warning(f'Error updating user {username}: {e}')
        return http_response(500, {"message": 'Server Error'})

    return http_response(200, {"AccessKey": access_key, "message": "Login success"})

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
    
    handler = routes.get(httpMethod, {}).get(path)

    if httpMethod == 'GET':
        qs_params = event['queryStringParameters']
        return handler(qs_params)
    elif httpMethod == 'POST':
        return handler(event)
