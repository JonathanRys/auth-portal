import re
import json
import uuid
import hashlib
import logging
from datetime import datetime

from fastapi import FastAPI, HTTPException
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
    allow_methods=['GET', 'POST', 'OPTIONS', 'HEAD']
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

user_table = get_users_table(config.USER_TABLE)

class LogedInUser(BaseModel):
    """Return type for User"""
    username: str
    role: str
    authKey: str
    sessionKey: str

@app.get('/')
def home():
    return {"test": "success"}

# Utilities
def http_response(statusCode: int, body: any=None):
    """Generates a standard HTTP response"""
    if statusCode >= 400:
        raise HTTPException(status_code=statusCode, detail=body.get('message'))

    response = {
        "statusCode": statusCode,
        "authKey": body.get('authKey') if body else None,
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

def validate_auth_key(username: str, auth_key: str):
    """Verify the user's auth key"""
    response = user_table.get_item(Key={"UserName": username})
    db_auth_key = response.get('Item', {}).get('AuthKey')
    if auth_key:
        if db_auth_key == auth_key:
            return auth_key
        return None
    return db_auth_key

class EmailConfirmation(BaseModel):
    """Class for email confirmation endpoint"""
    accessKey: str

# Handler methods
@app.get("/confirm_email", response_model=LogedInUser)
def confirm_email(user: EmailConfirmation):
    """Confirm registration email endpoint (GET)"""
    accessKey = user.accessKey
    username = validate_access_key(accessKey)
    if username:
        auth_key = str(uuid.uuid4())
        user_table.update_item(
            Key={"UserName": username},
            UpdateExpression="SET LastLogin = :last_login, AuthRole = :role, AuthKey = :auth_key, Valid = :valid",
            ExpressionAttributeValues={
                ":last_login": str(datetime.utcnow()),
                ":role": "Viewer",
                ":auth_key": auth_key,
                ":valid": True
            }
        )
        return http_response(200, {"authKey": auth_key, "message": "Email confirmed"})
    return http_response(403, {"message": 'Forbidden'})

class ResetPassword(BaseModel):
    """Class for resetting password"""
    username: str

@app.post("/reset_password")
def reset_password(user: ResetPassword):
    """Allow user to reset their password (POST)"""
    username = user.username
    # send reset password link in an email
    if send_reset_password_email(username):
        return http_response(200, { "message": "Password reset email sent" })
    return http_response(500, {"message": 'Server error'})

class UpdatePassword(BaseModel):
    """Class for changing the password"""
    username: str
    password: str
    newPassword: str

@app.post("/change_password")
def change_password(user: UpdatePassword):
    """Allow user to change their password (POST)"""
    username = user.username
    password = user.password
    new_password = user.newPassword

    # validate data
    if not is_valid_user(username) or \
       not is_valid_password(password) or \
       not is_valid_password(new_password):
        logger.error(f'User {username} attempted to bypass frontend security using password {password}.')
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
        logger.error(f'User {username} attempted to bypass frontend security using password {password}.')
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
        logger.error(f'Error registering user {username}: {e}')
        return http_response(500, {"message": 'Server error'})

    # craft response
    return http_response(201, {"message": "Registration success"})

class ExistingUser(BaseModel):
    """Data class for register endpoint"""
    username: str
    password: str
    authKey: str

@app.post("/login", response_model=LogedInUser)
def login(user: ExistingUser):
    """Allow the user to login (POST)"""
    username = user.username
    password = user.password
    auth_key = user.authKey
    # validate / scrub data
    if not is_valid_user(username) or not is_valid_password(password):
        logger.error(f'User {username} attempted to bypass frontend security using password {password}.')
        return http_response(403, {"message": 'Forbidden'})

    if not validate_auth_key(username, auth_key):
        # The user hasn't validated their email yet
        return http_response(401, {"message": 'Please validate your email address.'})

    response = user_table.get_item(Key={"UserName": username})
    if "Item" in response:
        pw_hash = response.get('Item', {}).get('Password')
        if pw_hash != hashlib.sha3_256(password.encode()).hexdigest():
            # log pw attempts and lock account for 10 min if failed more than 5 times
            logger.warning(f'Faild password attempt by {username}')
            return http_response(401, {"message": "Invalid username or password attempt."})

    try:
        user_table.update_item(
            Key={"UserName": username},
            UpdateExpression="SET LastLogin = :last_login",
            ExpressionAttributeValues={":last_login": str(datetime.utcnow())}
        )
    except Exception as e:
        logger.warning(f'Error updating user {username}: {e}')
        return http_response(500, {"message": 'Server Error'})
    
    payload = {
        "username": username,
        "role": response.get('Item', {}).get('AuthRole'),
        "authKey": response.get('Item', {}).get('AuthKey'),
        "message": "Login success"
    }

    # connect to session table
    payload["sessionKey"] = response.get('Item', {}).get('SessionKey'),

    return http_response(200, payload)

@app.post("/logout")
def logout(user: ExistingUser):
    """Allow the user to logout (POST)"""
    username = user.username
    if validate_auth_key(username):
        # clear cookies
        pass



# Handler
routes = {
    "GET": {
        "/confirm_email": confirm_email
    },
    "POST": {
        "/login": login,
        "/register": register,
        "/reset_password": reset_password,
        "/change_password": change_password
    }
}

data_types = {
    "/confirm_email": EmailConfirmation,
    "/login": ExistingUser,
    "/register": NewUser,
    "/reset_password": ResetPassword,
    "/change_password": UpdatePassword
}

def lambda_handler(event: any, context: any):
    httpMethod = event.get('httpMethod')
    path = event.get('path')
    logger.error('event:', event)
    logger.error(f'method: {httpMethod}')
    logger.error(f'path: {path}')

    handler = routes.get(httpMethod, {}).get(path)
    data_class = data_types[path]

    if httpMethod == 'GET':
        qs_params = event.get('queryStringParameters')
        logger.error(f'event: {event}')
        logger.error(f'qs: {qs_params}')
        return handler(data_class(**qs_params))
    elif httpMethod == 'POST':
        return handler(data_class(event))
