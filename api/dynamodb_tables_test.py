from .dynamodb_tables import get_user_table, get_token_table

def test_get_user_table():
    assert get_user_table() == None

def test_get_token_table():
    assert get_token_table() == None