from datetime import datetime
from decimal import Decimal

from ..dynamodb_tables import get_users_table, get_tokens_table
from ..dynamodb_tables import get_queries_table, get_flagged_docs_table

def test_get_users_table():
    table = get_users_table("Users")
    login_time = str(datetime.utcnow()),
    table.put_item(Item={
        "UserName": "user@test.com",
        "Password": "abc123",
        "RateLimit": 1000,
        "LastLogin": login_time,
        "AuthRole": "viewer",
        "ApiKey": "abc12345",
        "Active": True
    })

    result = table.get_item(Key={"UserName": "user@test.com"})

    assert result['Item'] == {
        "UserName": "user@test.com",
        "Password": "abc123",
        "RateLimit": Decimal('1000'),
        "LastLogin": [login_time[0]],
        "AuthRole": "viewer",
        "ApiKey": "abc12345",
        "Active": True
    }

    table.delete_item(Key={"UserName": "user@test.com"})

def test_get_tokens_table():
    table = get_tokens_table("Tokens")
    table.put_item(Item={
        "UserName": "user@test.com",
        "AccessKey": "abc123",
        "Valid": True
    })

    result = table.get_item(Key={"AccessKey": "abc123"})

    assert result['Item'] == {
        "UserName": "user@test.com",
        "AccessKey": "abc123",
        "Valid": True
    }

    table.delete_item(Key={"AccessKey": "abc123"})

def test_get_queries_table():
    table = get_queries_table("Queries")
    table.put_item(Item={
        "QueryId": 1234,
        "UserId": "user@test.com",
        "Query": "What is the moon made of?",
        "Context": "The moon is made of cheese.",
        "Response": "Cheese."
    })

    result = table.get_item(Key={"QueryId": 1234})

    assert result.get('Item') == {
            'Context': 'The moon is made of cheese.',
            'Query': 'What is the moon made of?',
            'QueryId': Decimal('1234'),
            'Response': 'Cheese.',
            'UserId': 'user@test.com'
        }

    table.delete_item(Key={"QueryId": 1234})

def test_get_flagged_docs_table():
    table = get_flagged_docs_table("Flagged")
    table.put_item(Item={
        "FlaggedId": 1234,
        "Reason": "Boring",
        "FileName": "Test.pdf",
        "Page": 5,
        "Paragraph": 2
    })

    result = table.get_item(Key={"FlaggedId": 1234})

    assert result['Item'] == {
        "FlaggedId": Decimal('1234'),
        "Reason": "Boring",
        "FileName": "Test.pdf",
        "Page": Decimal('5'),
        "Paragraph": Decimal('2')
    }

    table.delete_item(Key={"FlaggedId": 1234})
