# Use Python 3.9 base image
FROM python:3.9

# Set the workdir
WORKDIR /code

# Set non-private env vars
ENV PYTHON_PATH "${PYTHON_PATH}:/home/app"

# Copy requirements file
COPY ./requirements.txt /code/requirements.txt

# Install requirements
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the code
COPY ./app /code/app

# Set the workdir
WORKDIR /code/app

# Start the app
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "80"]
