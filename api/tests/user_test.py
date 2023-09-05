"""Tests for the user module"""

from ..user import get_user, \
                update_timestamp, \
                validate_auth_key, \
                is_valid_user, \
                is_valid_password

def test_is_valid_password():
    assert is_valid_password('thi$shouldntw0rk') == False
    assert is_valid_password('ThisShouldntw0rk') == False
    assert is_valid_password('Thi$Shouldntwork') == False
    assert is_valid_password('thi$w0ntwork') == False
    assert is_valid_password('Nf6$') == False
    assert is_valid_password('THI$W0NTWORK') == False
    assert is_valid_password('thiswontwork') == False
    assert is_valid_password('Thi$Shouldw0rk') == True

def test_is_valid_user():
    assert is_valid_user('TestUser') == False
    assert is_valid_user('Testgmail.com') == False
    assert is_valid_user('testuser@gmail.com') == True
