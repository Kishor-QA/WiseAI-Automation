# Use a Python image compatible with Playwright
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Environment variables for Python and test configuration
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HEADLESS=true \
    TZ=Asia/Kathmandu \
    ENV=prod \
    DEV_URL=https://dev.wiseai.wiseyak.com/login \
    STAGE_URL=https://stage.wiseai.wiseyak.com/login \
    PROD_URL=https://wiseai.wiseyak.com/login

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
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Use Nepal Time for pytest-html's generated timestamp and test logs.
RUN ln -snf /usr/share/zoneinfo/${TZ} /etc/localtime \
    && echo ${TZ} > /etc/timezone

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers with necessary dependencies
RUN python -m playwright install --with-deps

# Copy project files
COPY . .

# Default command to run tests; can be overridden at runtime
CMD ["pytest", "tests", "-v", "--tb=short", "--alluredir=reports/allure-results"]
