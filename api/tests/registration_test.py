from .. import config
from ..registration import validate_access_key, \
                         get_registration_link, \
                         get_reset_link, \
                         send_registration_email, \
                         send_reset_password_email

from ..dynamodb_tables import get_tokens_table

token_table = "Tokens"

def test_validate_access_key():
    table = get_tokens_table(token_table)
    table.put_item(Item={
        "UserName": "user@test.com",
        "AccessKey": "abc123",
        "Valid": True
    })
    assert validate_access_key("abc123") == "user@test.com"

    table.delete_item(Key={"AccessKey": "abc123"})

def test_get_registration_link():
    expected_result = f'{config.API_URL}/confirm_email?accessKey='
    assert get_registration_link("testuser@gmail.com")[:len(expected_result)] == expected_result

def test_get_reset_link():
    expected_result = f'{config.API_URL}/resetPassword?accessKey='
    assert get_reset_link("testuser@gmail.com")[:len(expected_result)] == expected_result

def test_send_reset_password_email(mocker):
    table = get_tokens_table(token_table)
    table.put_item(Item={
        "UserName": "user@test.com",
        "AccessKey": "abc123",
        "Valid": True
    })
    mocker.patch('smtplib.SMTP_SSL')
    assert send_reset_password_email("testuser@gmail.com") == True

    table.delete_item(Key={"AccessKey": "abc123"})

def test_send_registration_email(mocker):
    """Test send registration email"""
    mocker.patch('smtplib.SMTP_SSL')
    assert send_registration_email("testuser@gmail.com") == True
