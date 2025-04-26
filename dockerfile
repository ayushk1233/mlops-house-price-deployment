# Use a light version of Python
FROM python:3.8-slim

# Set folder where app will run
WORKDIR /app

# Copy everything from your project folder into the Docker container
COPY . .

# Install Python libraries
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8000 (where FastAPI will run)
EXPOSE 8000

# Command to run app
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000"]

