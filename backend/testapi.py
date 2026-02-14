#!/usr/bin/env python3
"""
Test script for AI Navigation Assistant Backend
"""

import requests
import base64
import json
from pathlib import Path

# API endpoint
API_URL = "http://localhost:8000"


def test_health():
    """Test health check endpoint"""
    print("Testing /health endpoint...")
    response = requests.get(f"{API_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()


def test_detection_with_image(image_path: str):
    """Test detection with image file"""
    print(f"Testing detection with {image_path}...")
    
    # Read and encode image
    with open(image_path, 'rb') as f:
        image_bytes = f.read()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    
    # Prepare request
    payload = {
        "image": f"data:image/jpeg;base64,{image_base64}",
        "min_confidence": 0.4
    }
    
    # Send request
    response = requests.post(f"{API_URL}/detect", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Message: {result['message']}")
        print(f"Detections: {len(result['detections'])}")
        for det in result['detections']:
            print(f"  - {det['class']}: {det['position']} ({det['distance']}) - {det['confidence']}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
    print()


def test_detection_with_query(image_path: str, query: str):
    """Test detection with voice query"""
    print(f"Testing query: '{query}'")
    
    with open(image_path, 'rb') as f:
        image_bytes = f.read()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    
    payload = {
        "image": f"data:image/jpeg;base64,{image_base64}",
        "min_confidence": 0.4
    }
    
    response = requests.post(
        f"{API_URL}/detect-with-query?query={query}",
        json=payload
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"Response: {result['message']}")
    else:
        print(f"Error: {response.status_code}")
    print()


def main():
    print("=== AI Navigation Assistant Backend Test ===\n")
    
    # Test health
    try:
        test_health()
    except Exception as e:
        print(f"Health check failed: {e}")
        print("Make sure the server is running!")
        return
    
    # Test with sample image (if available)
    test_image = "test_image.jpg"
    if Path(test_image).exists():
        test_detection_with_image(test_image)
        test_detection_with_query(test_image, "Is there a person nearby?")
        test_detection_with_query(test_image, "What's in front?")
    else:
        print(f"No test image found at {test_image}")
        print("Place a test image and run again.")


if __name__ == "__main__":
    main()