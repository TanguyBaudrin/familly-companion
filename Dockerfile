# Use an official Python runtime as a parent image
FROM python:3.13-slim

# Set the working directory in the container
WORKDIR /app

RUN pip install uv

# Copy the requirements file
COPY uv.lock pyproject.toml ./

# Install dependencies
RUN uv sync --frozen

# Copy the current directory contents into the container at /app
COPY src/ ./src/

# Make port 80 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV NAME=World
ENV PYTHONPATH=/app

# Run main.py when the container launches
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
