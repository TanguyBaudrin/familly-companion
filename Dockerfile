# Use an official Python runtime as a parent image
FROM python:3.13-slim

# Set the working directory in the container
WORKDIR /app

# Install uv
RUN pip install uv

# Copy the pyproject.toml and uv.lock files
COPY pyproject.toml uv.lock* ./

# Install dependencies
RUN uv sync --frozen

# Copy the current directory contents into the container at /app
COPY src/ ./src/

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME=World

# Run main.py when the container launches
CMD ["python", "src/main.py"]