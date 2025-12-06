# setup.ps1
# This script automates the setup of the backend and frontend for the project.
# It assumes Python, pip, Node.js, and npm are installed and in your PATH.

# Navigate to the root of the project (where this script is located)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $scriptDir

Write-Host "--- Starting project setup ---"

# --- Backend Setup ---
Write-Host "`n--- Setting up backend (Python) ---"
Set-Location ".\apps\backend"

# Create a virtual environment if it doesn't exist
if (-not (Test-Path ".\venv" -PathType Container)) {
    Write-Host "Creating Python virtual environment in '.\apps\backend\venv'..."
    python -m venv venv
    if ($LASTEXITCODE -ne 0) { Write-Error "Failed to create Python virtual environment. Please ensure Python is installed and in your PATH." ; exit 1 }
}

Write-Host "Installing Python dependencies into virtual environment..."
# Directly use the pip executable from the virtual environment to install dependencies
& ".\venv\Scripts\pip.exe" install -r requirements.txt
if ($LASTEXITCODE -ne 0) { Write-Error "Failed to install backend dependencies. Please ensure 'requirements.txt' exists." ; exit 1 }

Write-Host "Backend setup complete."
Set-Location $scriptDir # Go back to root

# --- Frontend Setup ---
Write-Host "`n--- Setting up frontend (React) ---"
Set-Location ".\apps\frontend"

Write-Host "Installing Node.js dependencies (npm install)..."
npm install
if ($LASTEXITCODE -ne 0) { Write-Error "Failed to install frontend dependencies. Please ensure 'package.json' exists and Node.js/npm are configured." ; exit 1 }

Write-Host "Frontend setup complete."
Set-Location $scriptDir # Go back to root

Write-Host "`n--- Project setup complete! ---"
Write-Host "You can now run your backend and serve the frontend using the 'npm run dev:*' scripts."
