from . import config
from registration import validate_access_key, \
                         get_registration_link, \
                         get_reset_link, \
                         send_registration_email, \
                         send_reset_password_email

def test_validate_access_key():
    assert validate_access_key("test") == "testuser@gmail.com"

def test_get_registration_link():
    assert get_registration_link("testuser@gmail.com") == f'{config.API_URL}/confirm?accessKey=test'

def test_get_reset_link():
    assert get_reset_link("testuser@gmail.com") == f'{config.API_URL}/resetPassword?accessKey=test'

def test_send_reset_password_email():
    assert send_reset_password_email("testuser@gmail.com") == True

def test_send_registration_email():
    assert send_registration_email("testuser@gmail.com") == True
