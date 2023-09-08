"""Test registration"""

from app import config
from app.registration import validate_access_key, \
                         get_registration_link, \
                         get_reset_link, \
                         send_registration_email, \
                         send_reset_password_email

from app.dynamodb_tables import get_tokens_table

tokens_table = get_tokens_table(config.TOKENS_TABLE)

def test_validate_access_key():
    """Test validate_access_key"""
    tokens_table.put_item(Item={
        "UserName": "user@test.com",
        "AccessKey": "abc123",
        "Valid": True
    })
    assert validate_access_key("abc123") == "user@test.com"

    tokens_table.delete_item(Key={"AccessKey": "abc123"})

def test_get_registration_link(mocker):
    """Test get_registration_link"""
    mocker.patch('uuid.uuid4', return_value='uuid1234')
    expected_result = f'{config.API_URL}/confirm_email?accessKey='
    assert get_registration_link("testuser@gmail.com")[:len(expected_result)] == expected_result
    tokens_table.delete_item(Key={"AccessKey": "uuid1234"})

def test_get_reset_link(mocker):
    """Test get_reset_link"""
    mocker.patch('uuid.uuid4', return_value='uuid1234')
    expected_result = f'{config.API_URL}/set_new_password?accessKey='
    assert get_reset_link("testuser@gmail.com")[:len(expected_result)] == expected_result
    tokens_table.delete_item(Key={"AccessKey": "uuid1234"})

def test_send_reset_password_email(mocker):
    """Test send_reset_password_email"""
    mocker.patch('uuid.uuid4', return_value='uuid1234')
    mocker.patch('smtplib.SMTP_SSL')
    tokens_table.put_item(Item={
        "UserName": "user@test.com",
        "AccessKey": "abc123",
        "Valid": True
    })
    
    assert send_reset_password_email("testuser@gmail.com") is True

    tokens_table.delete_item(Key={"AccessKey": "abc123"})
    tokens_table.delete_item(Key={"AccessKey": "uuid1234"})

def test_send_registration_email(mocker):
    """Test send registration email"""
    mocker.patch('uuid.uuid4', return_value='uuid1234')
    mocker.patch('smtplib.SMTP_SSL')
    assert send_registration_email("testuser@gmail.com") is True
    tokens_table.delete_item(Key={"AccessKey": "uuid1234"})
