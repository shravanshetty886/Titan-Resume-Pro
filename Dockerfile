# We are switching to 'bullseye' which is very stable for wkhtmltopdf
FROM python:3.9-bullseye

# Install wkhtmltopdf and its dependencies
RUN apt-get update && apt-get install -y \
    wkhtmltopdf \
    xvfb \
    libfontconfig1 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python libraries
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your code
COPY . .

# Environment variable for the app to find the tool
ENV WKHTMLTOPDF_PATH=/usr/bin/wkhtmltopdf

# Run with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]