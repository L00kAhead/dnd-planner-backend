# Use the official Python image as a base
FROM python:3.10

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file first for caching
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code explicitly
COPY ./app ./app

# Set PYTHONPATH to ensure the `app` module is recognized
ENV PYTHONPATH=/app

# Expose the port that the application runs on
EXPOSE 8000

# Run the seeder script and start the app
CMD ["sh", "-c", "python /app/app/admin_seeder.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]