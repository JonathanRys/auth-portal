# Getting Started

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

## Front-end

To install the project dependencies, in the project directory, run:

```console
npm install
```

Then start the development server:

```console
npm start
```

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

The page will reload when you make changes.\
You may also see any lint errors in the console.

## Back-end

##### Set you AWS profile and credentials so the app can talk to the database.

```console
aws configure --profile physgpt
```

Windows

```cmd
SET AWS_PROFILE=physgpt
SET AWS_ACCESS_KEY_ID=AK..YZ
SET AWS_SECRET_ACCESS_KEY=abc...xyz
```

Mac/Linux

```bash
export AWS_PROFILE=physgpt
export AWS_ACCESS_KEY_ID=AK..YZ
export AWS_SECRET_ACCESS_KEY=abc...xyz
```

##### Activate the virtual environment so the app has access to the Python libraries

Change to the api directory

```console
cd api
```

Windows

```cmd
.\venv\Scripts\activate
```

Mac/Linux

```bash
source ./venv/bin/activate
```

##### Start the API server

```console
uvicorn api:app --port: 80 --reload
```

### Update your hosts file

Add this line to your [hosts file](https://www.hostinger.com/tutorials/how-to-edit-hosts-file)

```console
127.0.0.1 local.host
```

## Config

```python
API_URL = "http://local.host"
SERVICE_EMAIL
EMAIL_PW

APP_ORIGIN = "https://physgpt.com"

USERS_TABLE = "Users"
TOKENS_TABLE = "Tokens"
SESSIONS_TABLE = "Sessions"
QUERIES_TABLE = "Queries"
FLAGGED_DOCS_TABLE = "FlaggedDocuments"
```
