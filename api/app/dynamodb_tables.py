"""
Functions to get or create DynamoDB tables
"""

import boto3
from . import config

# connect to DB
dynamodb = boto3.resource('dynamodb')

def get_users_table(table_name: str = config.USERS_TABLE) -> dynamodb.Table:
    """Creates the User table if it doesn't exist and returns the client"""
    if table_name not in [table.name for table in dynamodb.tables.all()]:
        client = boto3.client('dynamodb')
        client.create_table(
            TableName=table_name,
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

    return dynamodb.Table(table_name)

def get_tokens_table(table_name: str = config.TOKENS_TABLE) -> dynamodb.Table:
    """Creates the Token table if it doesn't exist and returns the client"""
    if table_name not in [table.name for table in dynamodb.tables.all()]:
        client = boto3.client('dynamodb')
        client.create_table(
            TableName=table_name,
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

    return dynamodb.Table(table_name)

def get_sessions_table(table_name: str = config.SESSIONS_TABLE) -> dynamodb.Table:
    """Creates the Token table if it doesn't exist and returns the client"""
    if table_name not in [table.name for table in dynamodb.tables.all()]:
        client = boto3.client('dynamodb')
        client.create_table(
            TableName=table_name,
            ProvisionedThroughput={
                "ReadCapacityUnits": 5,
                "WriteCapacityUnits": 5
            },
            KeySchema=[
                {
                    "AttributeName": "SessionKey",
                    "KeyType": "HASH"
                }
            ],
            AttributeDefinitions=[
                {
                    "AttributeName": "SessionKey",
                    "AttributeType": "S"
                }
            ],
        )

    return dynamodb.Table(table_name)

def get_queries_table(table_name: str = config.QUERIES_TABLE) -> dynamodb.Table:
    """Creates the Queries table if it doesn't exist and returns the client"""
    if table_name not in [table.name for table in dynamodb.tables.all()]:
        client = boto3.client('dynamodb')
        client.create_table(
            TableName=table_name,
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

    return dynamodb.Table(table_name)

def get_flagged_docs_table(table_name: str = config.FLAGGED_DOCS_TABLE) -> dynamodb.Table:
    """Creates the Flagged table if it doesn't exist and returns the client"""
    if table_name not in [table.name for table in dynamodb.tables.all()]:
        client = boto3.client('dynamodb')
        client.create_table(
            TableName=table_name,
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

    return dynamodb.Table(table_name)
