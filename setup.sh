#!/bin/bash

# setup.sh
# This script automates the setup of the backend and frontend for the project.
# It assumes Python, pip, Node.js, and npm are installed and in your PATH.

# Exit immediately if a command exits with a non-zero status.
set -e

# Navigate to the root of the project (where this script is located)
SCRIPT_DIR=$(dirname "$0")
cd "$SCRIPT_DIR"

echo "--- Starting project setup ---"

# --- Backend Setup ---
echo -e "\n--- Setting up backend (Python) ---"
cd "./apps/backend"

# Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment in './apps/backend/venv'..."
    python3 -m venv venv
fi

echo "Installing Python dependencies into virtual environment..."
# Use the pip from the virtual environment to install requirements
./venv/bin/pip install -r requirements.txt
echo "Backend setup complete."
cd "$SCRIPT_DIR" # Go back to root

# --- Frontend Setup ---
echo -e "\n--- Setting up frontend (React) ---"
cd "./apps/frontend"

echo "Installing Node.js dependencies (npm install)..."
npm install
echo "Frontend setup complete."
cd "$SCRIPT_DIR" # Go back to root

echo -e "\n--- Project setup complete! ---"
echo "You can now run your backend and serve the frontend using the 'npm run dev:*' scripts."
