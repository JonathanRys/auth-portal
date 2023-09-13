# Use Python 3.9 base image
FROM python:3.9

# Set the workdir
WORKDIR /code

# Set non-private env vars
ENV PYTHON_PATH "$PYTHON_PATH:/code/app"

# Copy code
COPY . /code

# Install requirements
RUN python -m pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Set the workdir
WORKDIR /code

# Start the app
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "80"]
