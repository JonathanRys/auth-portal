"""
Models for API endpoints
"""

from pydantic import BaseModel

class LoggedInUser(BaseModel):
    """Return type for User"""
    username: str
    role: str
    authKey: str
    sessionKey: str

class EmailConfirmation(BaseModel):
    """Class for email confirmation endpoint"""
    accessKey: str

class ResetPassword(BaseModel):
    """Class for resetting password"""
    username: str

class UpdatePassword(BaseModel):
    """Class for changing the password"""
    username: str
    password: str
    newPassword: str

class NewUser(BaseModel):
    """Data class for register endpoint"""
    username: str
    password: str

class ExistingUser(BaseModel):
    """Data class for register endpoint"""
    username: str
    password: str
    authKey: str
