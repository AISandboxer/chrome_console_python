#!/bin/bash
# Script to quickly test chrome-console-capture in a virtual environment

echo "Chrome Console Capture - Virtual Environment Test"
echo "================================================"

# Check if venv exists
if [ -d "venv" ]; then
    echo "Virtual environment already exists."
    read -p "Do you want to recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing existing virtual environment..."
        rm -rf venv
    fi
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --quiet

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt --quiet

# Install package in development mode
echo "Installing chrome-console-capture in development mode..."
pip install -e . --quiet

# Show installed packages
echo ""
echo "Installed packages:"
pip list | grep -E "(chrome-console-capture|websocket-client|requests|psutil)"

# Run test
echo ""
echo "Running test script..."
python test_package.py

# Deactivate virtual environment
deactivate

echo ""
echo "Test complete! Virtual environment has been deactivated."
echo "To manually activate the environment, run: source venv/bin/activate" 