#!/bin/bash
# Unified Directory Platform Startup Script
# Port: 9180

echo "Starting Unified Business Directory Platform on Port 9180..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/upgrade requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Set environment variables for unified system
export PYTHONPATH=/opt/webwise/unified-directory

echo "Starting server on port 9180..."
uvicorn backend.main_unified:app --host 0.0.0.0 --port 9180 --reload