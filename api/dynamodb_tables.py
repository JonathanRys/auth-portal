"""
Functions to get or create DynamoDB tables
"""

import boto3

# connect to DB
dynamodb = boto3.resource('dynamodb')

def get_users_table(users_table_name: str = "Users") -> dynamodb.Table:
    """Creates the User table if it doesn't exist and returns the client"""
    if users_table_name not in [table.name for table in dynamodb.tables.all()]:
        client = boto3.client('dynamodb')
        client.create_table(
            TableName=users_table_name,
            ProvisionedThroughput={
                "ReadCapacityUnits": 5,
                "WriteCapacityUnits": 5
            },
            KeySchema=[
                {
                    "AttributeName": "UserName",
                    "KeyType": "HASH"
                }
            ],
            AttributeDefinitions=[
                {
                    "AttributeName": "UserName",
                    "AttributeType": "S"
                }
            ],
        )

    return dynamodb.Table(users_table_name)

def get_tokens_table(tokens_table_name: str = "Tokens") -> dynamodb.Table:
    """Creates the Token table if it doesn't exist and returns the client"""
    if tokens_table_name not in [table.name for table in dynamodb.tables.all()]:
        client = boto3.client('dynamodb')
        client.create_table(
            TableName=tokens_table_name,
            ProvisionedThroughput={
                "ReadCapacityUnits": 5,
                "WriteCapacityUnits": 5
            },
            KeySchema=[
                {
                    "AttributeName": "AccessKey",
                    "KeyType": "HASH"
                }
            ],
            AttributeDefinitions=[
                {
                    "AttributeName": "AccessKey",
                    "AttributeType": "S"
                }
            ],
        )

    return dynamodb.Table(tokens_table_name)

def get_queries_table(queries_table_name: str = "Queries") -> dynamodb.Table:
    """Creates the Queries table if it doesn't exist and returns the client"""
    if queries_table_name not in [table.name for table in dynamodb.tables.all()]:
        client = boto3.client('dynamodb')
        client.create_table(
            TableName=queries_table_name,
            ProvisionedThroughput={
                "ReadCapacityUnits": 5,
                "WriteCapacityUnits": 5
            },
            KeySchema=[
                {
                    "AttributeName": "QueryId",
                    "KeyType": "HASH"
                }
            ],
            AttributeDefinitions=[
                {
                    "AttributeName": "QueryId",
                    "AttributeType": "N"
                }
            ],
        )

    return dynamodb.Table(queries_table_name)

def get_flagged_docs_table(flagged_docs_table_name: str = "Flagged") -> dynamodb.Table:
    """Creates the Flagged table if it doesn't exist and returns the client"""
    if flagged_docs_table_name not in [table.name for table in dynamodb.tables.all()]:
        client = boto3.client('dynamodb')
        client.create_table(
            TableName=flagged_docs_table_name,
            ProvisionedThroughput={
                "ReadCapacityUnits": 5,
                "WriteCapacityUnits": 5
            },
            KeySchema=[
                {
                    "AttributeName": "FlaggedId",
                    "KeyType": "HASH"
                }
            ],
            AttributeDefinitions=[
                {
                    "AttributeName": "FlaggedId",
                    "AttributeType": "N"
                }
            ],
        )

    return dynamodb.Table(flagged_docs_table_name)
