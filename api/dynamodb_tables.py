import boto3

# connect to DB
dynamodb = boto3.resource('dynamodb')

def get_user_table(user_table_name: str) -> dynamodb.Table:
    if user_table_name not in [table.name for table in dynamodb.tables.all()]:
        client = boto3.client('dynamodb')
        client.create_table(
            TableName=user_table_name,
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
                }, {
                    "AttributeName": "Password",
                    "AttributeType": "S"
                }, {
                    "AttributeName": "RateLimit",
                    "AttributeType": "N"
                }, {
                    "AttributeName": "LastLogin",
                    "AttributeType": "S"
                }, {
                    "AttributeName": "Roles",
                    "AttributeType": "S"
                }

            ],
        )

    return dynamodb.Table(user_table_name)

def get_token_table(token_table_name):
    if token_table_name not in [table.name for table in dynamodb.tables.all()]:
        client = boto3.client('dynamodb')
        client.create_table(
            TableName=token_table_name,
            ProvisionedThroughput={
                "ReadCapacityUnits": 5,
                "WriteCapacityUnits": 5
            },
            KeySchema=[
                {
                    "AttributeName": "AccessKey",
                    "KeyType": "HASH"
                }, {
                    "AttributeName": "UserName",
                    "KeyType": "RANGE"
                }
            ],
            AttributeDefinitions=[
                {
                    "AttributeName": "AccessKey",
                    "AttributeType": "S"
                }, {
                    "AttributeName": "UserName",
                    "AttributeType": "S"
                }, {
                    "AttributeName": "Valid",
                    "AttributeType": "B"
                }
            ],
        )

    return dynamodb.Table(token_table_name)
