FROM python:3.9-slim

# Install the PDF tool into the server's OS
RUN apt-get update && apt-get install -y wkhtmltopdf && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install your Python libraries
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your code into the server
COPY . .

# Set the path variable so app.py knows where to look
ENV WKHTMLTOPDF_PATH=/usr/bin/wkhtmltopdf

# Start the app
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]