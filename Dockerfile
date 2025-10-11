FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Copy requirements first for better caching
COPY --chown=app:app requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Add user local bin to PATH
ENV PATH="/home/app/.local/bin:${PATH}"

# Copy application code
COPY --chown=app:app . .

# Add src to Python path for imports
ENV PYTHONPATH="/app/src:${PYTHONPATH}"

# Create .streamlit directory and config
RUN mkdir -p /home/app/.streamlit
COPY --chown=app:app .streamlit/ /home/app/.streamlit/

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8080/_stcore/health || exit 1

# Run streamlit with production settings
CMD ["streamlit", "run", "app.py", \
     "--server.address", "0.0.0.0", \
     "--server.port", "8080", \
     "--server.headless", "true", \
     "--server.enableCORS", "false", \
     "--server.enableXsrfProtection", "false"]