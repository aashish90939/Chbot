# Use Python 3.12 base image
FROM python:3.12.7-slim

# Set the working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire app directory to the container
COPY app/ /app/

# Expose the port for Streamlit (default is 8501)
EXPOSE 8501

# Environment variables for Streamlit (optional, for better behavior in Docker)
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ENABLE_CORS=false

# Default command (will be overridden in docker-compose.yml)
CMD ["bash"]
