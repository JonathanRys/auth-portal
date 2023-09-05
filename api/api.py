"""
API controllers
"""

import uuid
import hashlib
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import api
from .util import http_response
from user import get_user, \
                create_new_user, \
                set_user_role, \
                update_timestamp, \
                update_password, \
                validate_auth_key, \
                is_valid_user, \
                is_valid_password

from registration import validate_access_key, \
                        send_reset_password_email, \
                        send_registration_email

from session import new_session, validate_session_key, invalidate_session

from models import LoggedInUser, \
                EmailConfirmation, \
                ResetPassword, \
                UpdatePassword, \
                NewUser, \
                ExistingUser

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

@app.get('/')
async def home():
    return {"test": "success"}

# Handler methods
@app.post("/confirm_email", response_model=LoggedInUser)
async def confirm_email(user: EmailConfirmation):
    """Confirm registration email endpoint (GET)"""
    accessKey = user.accessKey
    username = validate_access_key(accessKey)
    if username:
        auth_key = str(uuid.uuid4())
        await set_user_role(username, 'viewer')

        payload = {
            "username": username,
            "role": "viewer",
            "message": "Email confirmed"
        }

        payload["sessionKey"] = await new_session(username)

        return http_response(200, payload)
    return http_response(403, {"message": 'Forbidden'})

@app.post("/reset_password")
async def reset_password(user: ResetPassword):
    """Allow user to reset their password (POST)"""
    username = user.username
    # send reset password link in an email
    if send_reset_password_email(username):
        return http_response(200, { "message": "Password reset email sent" })
    return http_response(500, {"message": 'Server error'})

@app.post("/change_password")
async def change_password(user: UpdatePassword):
    """Allow user to change their password (POST)"""
    username = user.username
    password = user.password
    new_password = user.newPassword

    # validate data
    if not is_valid_user(username) or \
       not is_valid_password(password) or \
       not is_valid_password(new_password):
        api.logger.error(f'User {username} attempted to bypass frontend security using incorrect password.')
        return http_response(403, {"message": 'Forbidden'})

    # validate user
    pw_hash = get_user(username).get('Password')

    if pw_hash != hashlib.sha3_256(password.encode()).hexdigest():
        return http_response(401, "Incorrect Password")
    
    await update_password(username, new_password)
    return http_response(200, {"UserName": username, "message": "Password updated"})

@app.post("/register")
async def register(new_user: NewUser):
    """Allow the user to register via (POST)"""
    username = new_user.username
    password = new_user.password
    # validate / scrub data
    if not is_valid_user(username) or not is_valid_password(password):
        api.logger.error(f'User {username} attempted to bypass frontend security using incorrect password.')
        return http_response(403, {"message": 'Forbidden'})

    # check for existing records
    if username == get_user(username).get('UserName'):
        return http_response(409, {"message": 'Username taken'})

    # hash password
    pw_hash = hashlib.sha3_256(password.encode()).hexdigest()

    # write to DB
    try:
        create_new_user(username, pw_hash)
        send_registration_email(username)
    except Exception as e:
        api.logger.error(f'Error registering user {username}: {e}')
        return http_response(500, {"message": 'Server error'})

    # craft response
    return http_response(201, {"message": "Registration success"})

@app.post("/login", response_model=LoggedInUser)
async def login(user: ExistingUser):
    """Allow the user to login (POST)"""
    username = user.username
    password = user.password
    session_key = user.authKey
    # validate / scrub data
    if not is_valid_user(username) or not is_valid_password(password):
        api.logger.error(f'User {username} attempted to bypass frontend security using incorrect password.')
        return http_response(403, {"message": 'Forbidden'})

    if not validate_auth_key(username, session_key):
        # The user hasn't validated their email yet
        return http_response(401, {"message": 'Please validate your email address.'})
    
    user = get_user(username)
    pw_hash = user.get('Password')
    if pw_hash != hashlib.sha3_256(password.encode()).hexdigest():
        # log pw attempts and lock account for 10 min if failed more than 5 times
        api.logger.warning(f'Faild password attempt by {username}')
        return http_response(401, {"message": "Invalid username or password attempt."})

    try:
        update_timestamp(username)
    except Exception as e:
        api.logger.warning(f'Error updating user {username}: {e}')
        return http_response(500, {"message": 'Server Error'})
    
    payload = {
        "username": username,
        "role": user.get('AuthRole'),
        "authKey": user.get('AuthKey'),
        "message": "Login success"
    }

    payload["sessionKey"] = await new_session(username)
    
    return http_response(200, payload)

@app.post("/logout")
async def logout(user: ExistingUser):
    """Allow the user to logout (POST)"""
    username = user.username
    auth_key = user.authKey
    if validate_auth_key(username, auth_key) and validate_session_key(auth_key):
        invalidate_session(auth_key)

    payload = {
        "username": username,
        "authKey": None,
        "message": "Logged out"
    }

    return http_response(200, payload)

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

async def lambda_handler(event: any, context: any):
    httpMethod = event.get('httpMethod')
    path = event.get('path')
    handler = routes.get(httpMethod, {}).get(path)
    data_class = data_types[path]

    if httpMethod == 'GET':
        qs_params = event.get('queryStringParameters')
        return await handler(data_class(**qs_params))
    elif httpMethod == 'POST':
        return await handler(data_class(event))
