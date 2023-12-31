"""
API controllers
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from botocore.exceptions import ClientError

from . import logger
from .util import http_response
from .user import get_user, \
                create_new_user, \
                set_user_role, \
                update_timestamp, \
                update_user_password, \
                validate_auth_key, \
                compare_to_hash, \
                is_valid_user, \
                is_valid_password

from .registration import validate_access_key, \
                        send_reset_password_email, \
                        send_registration_email

from .session import new_session, validate_session_key, invalidate_session

from .models import LoggedInUser, \
                EmailConfirmation, \
                ResetPassword, \
                UpdatePassword, \
                SetNewPassword, \
                NewUser, \
                ExistingUser, \
                AuthenticatingUser

origins = [
    "http://localhost",
    "http://local.host",
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
    """Default route """
    return {"test": "success"}

# Handler methods
@app.post("/confirm_email", response_model=LoggedInUser)
async def confirm_email(user: EmailConfirmation):
    """Confirm registration email endpoint (GET)"""
    access_key = user.accessKey
    username = validate_access_key(access_key)
    if username:
        await set_user_role(username, 'viewer')
        session_key = await new_session(username)

        payload = {
            "username": username,
            "role": "viewer",
            "authKey": session_key,
            "sessionKey": session_key,
            "message": "Email confirmed"
        }

        return http_response(200, payload)
    return http_response(403, {"message": 'Forbidden'})

@app.post("/reset_password")
async def reset_password(user: ResetPassword):
    """Allow user to reset their password (POST)"""
    username = user.username
    # send reset password link in an email
    if send_reset_password_email(username):
        return http_response(200, { "message": "Password reset email sent." })
    return http_response(500, {"message": 'Server error'})

@app.post("/update_password", response_model=LoggedInUser)
async def update_password(user: UpdatePassword):
    """Allow user to change their password (POST)"""
    username = user.username
    password = user.password
    new_password = user.newPassword

    # validate data
    if not is_valid_user(username) or \
       not is_valid_password(password) or \
       not is_valid_password(new_password):
        logger.error('User %s attempted to bypass frontend security.', username)
        return http_response(403, {"message": 'Forbidden'})

    # validate user and password
    pw_hash = get_user(username).get('Password')
    if not compare_to_hash(password, pw_hash):
        return http_response(401, {"message": "Incorrect Password"})
    
    await update_user_password(username, new_password)

    _user = get_user(username)

    payload = {
        "username": username,
        "role": _user.get('AuthRole'),
        "authKey": _user.get('AuthKey', ''),
        "message": "Password updated."
    }
    # Invalidate old session
    payload["sessionKey"] = await new_session(username)

    return http_response(200, payload)

@app.post("/set_new_password", response_model=LoggedInUser)
async def set_new_password(user: SetNewPassword):
    """Allow user to change their password (POST)"""
    username = user.username
    access_key = user.accessKey
    password = user.password

    # validate data
    if not is_valid_user(username) or \
       not is_valid_password(password):
        logger.error('User %s attempted to bypass frontend security.', username)
        return http_response(403, {"message": 'Forbidden'})

    # validate user
    if not username == validate_access_key(access_key):
        return http_response(401, {"message": "Invalid access key."})
    
    await update_user_password(username, password)
    _user = get_user(username)
    payload = {
        "username": username,
        "role": _user.get('AuthRole', ''),
        "authKey": _user.get('AuthKey', ''),
        "message": "New password set."
    }
    # Invalidate old session
    payload["sessionKey"] = await new_session(username)

    return http_response(200, payload)

@app.post("/register")
async def register(new_user: NewUser):
    """Allow the user to register via (POST)"""
    username = new_user.username
    password = new_user.password
    # validate / scrub data
    if not is_valid_user(username) or not is_valid_password(password):
        logger.error('User %s attempted to bypass frontend security.', username)
        return http_response(403, {"message": 'Forbidden'})

    # check for existing records
    if username == get_user(username).get('UserName'):
        return http_response(409, {"message": 'Username taken'})

    # write to DB
    try:
        create_new_user(username, password)
        send_registration_email(username)
    except ClientError as err:
        logger.error('Error registering user %s: %s', username, err)
        return http_response(500, {"message": 'Server error'})

    # craft response
    return http_response(201, {"message": "Registration success"})

@app.post("/login", response_model=LoggedInUser)
async def login(user: ExistingUser):
    """Allow the user to login (POST)"""
    username = user.username
    password = user.password
    # validate / scrub data
    if not is_valid_user(username) or not is_valid_password(password):
        logger.error('User %s attempted to bypass frontend security.', username)
        return http_response(403, {"message": 'Forbidden'})

    user = get_user(username)
    pw_hash = user.get('Password')

    auth_key = validate_auth_key(username)

    if not auth_key:
        # The user hasn't validated their email yet
        return http_response(401, {"message": 'Please validate your email address.'})

    if not compare_to_hash(password, pw_hash):
        # log pw attempts and lock account for 10 min if failed more than 5 times
        logger.warning('Faild password attempt by %s', username)
        return http_response(401, {"message": "Invalid username or password attempt."})

    try:
        update_timestamp(username)
    except ClientError as err:
        logger.warning('Error updating user %s: %s', username, err)
        return http_response(500, {"message": 'Server Error'})
    
    payload = {
        "username": username,
        "role": user.get('AuthRole'),
        "authKey": user.get('AuthKey', '') or auth_key,
        "message": "Login success"
    }

    payload["sessionKey"] = await new_session(username)
    
    return http_response(200, payload)

@app.post("/logout")
async def logout(user: AuthenticatingUser):
    """Allow the user to logout (POST)"""
    username = user.username
    session_key = user.authKey
    if validate_auth_key(username) and validate_session_key(session_key):
        invalidate_session(session_key)

    payload = {
        "username": username,
        "authKey": "",
        "message": "Logged out"
    }

    return http_response(200, payload)
