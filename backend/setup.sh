#!/bin/bash

# AI Navigation Assistant Backend Deployment Script

echo "=== AI Navigation Assistant Backend Deployment ==="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Download YOLOv8 model
echo "Downloading YOLOv8 nano model..."
python3 -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"

echo ""
echo "=== Setup Complete ==="
echo ""
echo "To start the server, run:"
echo "  source venv/bin/activate"
echo "  uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
echo ""
echo "Or for production:"
echo "  uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4"
echo ""