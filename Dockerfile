FROM python:3.9-bullseye

# Install wkhtmltopdf and system dependencies
RUN apt-get update && apt-get install -y \
    wkhtmltopdf \
    libfontconfig1 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Set environment variables for Render
ENV WKHTMLTOPDF_PATH=/usr/bin/wkhtmltopdf
ENV PORT=10000

# Bind to port 10000 which Render expects
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
