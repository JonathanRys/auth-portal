import uuid
from . import config
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

token_table_name = config.TOKEN_TABLE

# connect to DB
dynamodb = boto3.resource('dynamodb')

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

token_table = dynamodb.Table(token_table_name)

def validate_access_key(access_key: str) -> str:
    """Checks the access key against the DB"""
    response = token_table.get_item(Key={"AccessKey": access_key})
    if "Item" in response:
        username = response.get('Item', {}).get('UserName')
        token_table.update_item(Item={"AccessKey": access_key, "Valid": True})

        return username
    return ''

def get_registration_link(recipient: str) -> str:
    """Gets a registration link for the user"""
    access_key = uuid.uuid4()
    token_table.put_item(Item={"UserName": username, "AccessKey": access_key, "Valid": False})
    return f'{config.API_URL}/registration?accessKey={access_key}'

def get_reset_link(recipient: str) -> str:
    """Gets a reset password link"""
    access_key = uuid.uuid4()
    token_table.update_item(Item={"UserName": username, "AccessKey": access_key, "Valid": False})
    return f'{config.API_URL}/resetPassword?accessKey={access_key}'

def send_reset_password_email(recipient: str) -> bool:
    """Sends a password reset email to the recipient"""
    sender_email = config.SERVICE_EMAIL
    password = config.EMAIL_PW

    message = MIMEMultipart("alternative")
    message["Subject"] = "Reset password request"
    message["From"] = sender_email
    message["To"] = recipient

    reset_link = get_reset_link(recipient)

    # Create the plain-text and HTML version of your message
    text = f"""
    Hello,
    Someone (hopefully you) requested your password be reset.
    Please click the link below to reset your password:
    {reset_link}
    """
    html = f"""
    <html>
      <body>
        <p>Hello,<br />
           Someone (hopefully you) requested your password be reset.<br />
           <a href="{reset_link}">Click here</a> to reset your password. 
        </p>
      </body>
    </html>
    """

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, recipient, message.as_string()
        )
    return True

def send_registration_email(recipient: str) -> bool:
    """Sends a registration email to the recipient"""
    sender_email = config.SERVICE_EMAIL
    password = config.EMAIL_PW

    message = MIMEMultipart("alternative")
    message["Subject"] = "Please confirm your email address"
    message["From"] = sender_email
    message["To"] = recipient

    # this method creates the user record
    registration_link = get_registration_link(recipient)

    # Create the plain-text and HTML version of your message
    text = f"""
    Hello,
    Thank you for choosing PhysGPT.
    Please click the link below to get started:
    {registration_link}
    """
    html = f"""
    <html>
      <body>
        <p>Hello,<br />
           Thank you for choosing PhysGPT.<br />
           <a href="{registration_link}">Confirm your email address</a> to get started. 
        </p>
      </body>
    </html>
    """

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, recipient, message.as_string()
        )
    return True
