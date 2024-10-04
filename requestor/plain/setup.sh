#!/bin/bash

# Function to print success or failure based on the command exit status
check_status() {
  if [ $? -eq 0 ]; then
    echo "[SUCCESS] $1"
  else
    echo "[FAILURE] $1"
  fi
}

# Step 1: Clone yapapi repository or pull the latest changes if it exists
if [ -d "yapapi" ]; then
  echo "yapapi directory already exists. Pulling the latest changes..."
  cd yapapi || exit
  git pull origin main
  check_status "Updating yapapi repository"
else
  git clone https://github.com/anchalshivank/yapapi
  check_status "Cloning yapapi repository"
  cd yapapi || exit
fi

# Step 2: Create and activate a Python virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
  python3 -m venv venv
  check_status "Creating Python virtual environment"
fi

source venv/bin/activate
check_status "Activating Python virtual environment"

# Step 3: Install pipx (skip if already installed)
if ! command -v pipx &> /dev/null; then
  apt update
  check_status "Updating package list"
  
  apt install -y pipx
  check_status "Installing pipx"
  
  pipx ensurepath
  check_status "Ensuring pipx path"
else
  echo "pipx is already installed. Skipping installation."
fi

# Step 4: Install Poetry using pipx (skip if already installed)
if ! command -v poetry &> /dev/null; then
  pipx install poetry
  check_status "Installing Poetry using pipx"
else
  echo "Poetry is already installed. Skipping installation."
fi

# Step 5: Check and install project dependencies with Poetry
poetry install
check_status "Installing dependencies with Poetry"

# Step 6: Run unit tests
poetry run poe tests_unit
check_status "Running unit tests"

# Step 7: Connect yapapi with requestor by generating an app key and exporting it as an environment variable
APPKEY=$(yagna app-key create requestor | tail -n 1)
check_status "Creating app key for requestor"

export YAGNA_APPKEY=$APPKEY
check_status "Exporting YAGNA_APPKEY environment variable"
echo "YAGNA_APPKEY=$APPKEY exported"

# Step 8: Create payment fund
yagna payment fund
check_status "Creating payment fund"
