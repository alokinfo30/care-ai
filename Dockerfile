# ---- Builder Stage ----
# This stage builds the Python virtual environment with all dependencies.
FROM python:3.11-slim as builder

# Set the working directory in the container
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PATH="/opt/venv/bin:$PATH"

# Install build dependencies needed for some Python packages (like numpy, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

# Create a virtual environment
RUN python -m venv /opt/venv

# Copy the requirements file into the container
COPY requirements.txt .

# Install production dependencies into the virtual environment
RUN pip install --no-cache-dir -r requirements.txt

# ---- Final Stage ----
# This stage creates the final, smaller production image.
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PATH="/opt/venv/bin:$PATH"
ENV FLASK_ENV="production"

# Create a non-root user for security
RUN addgroup --system nonroot && adduser --system --ingroup nonroot nonroot

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy the rest of the application's code into the container
WORKDIR /app
COPY --chown=nonroot:nonroot . .

# Expose the port the app runs on
EXPOSE 5000

# Switch to the non-root user
USER nonroot

# Define the command to run your app using a production-grade server (gunicorn)
CMD ["gunicorn", "--workers", "2", "-k", "gevent", "--timeout", "120", "--bind", "0.0.0.0:5000", "run:app"]