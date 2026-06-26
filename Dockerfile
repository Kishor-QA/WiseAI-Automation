# Use a Python image compatible with Playwright
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Environment variables for Python and test configuration
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HEADLESS=true \
    ENV=stage \
    DEV_URL=https://dev.wiseai.wiseyak.com/login \
    STAGE_URL=https://stage.wiseai.wiseyak.com/login \
    PROD_URL=https://prod.wiseai.wiseyak.com/login

# Install system dependencies required by Playwright browsers
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    ca-certificates \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libgtk-3-0 \
    libasound2 \
    libxss1 \
    libxtst6 \
    fonts-liberation \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers with necessary dependencies
RUN python -m playwright install --with-deps

# Copy project files
COPY . .

# Default command to run tests; can be overridden at runtime
CMD ["pytest", "tests", "-v", "--tb=short", "--alluredir=reports/allure-results"]
