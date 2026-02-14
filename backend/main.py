"""
AI Navigation Assistant Backend
FastAPI server with YOLOv8 object detection for visually impaired users
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import cv2
import numpy as np
import base64
from typing import List, Dict, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Navigation Assistant API",
    description="Real-time object detection for visually impaired navigation",
    version="1.0.0"
)

# CORS configuration - allow requests from any origin for demo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model variable
model = None


class ImageRequest(BaseModel):
    """Request model for image detection"""
    image: str  # base64 encoded image
    min_confidence: Optional[float] = 0.4


class DetectionResponse(BaseModel):
    """Response model for detection results"""
    message: str
    detections: List[Dict]
    frame_width: int
    frame_height: int


def load_model():
    """Load YOLOv8 model"""
    global model
    try:
        from ultralytics import YOLO
        # Use YOLOv8 nano for speed
        model = YOLO('yolov8n.pt')
        logger.info("YOLOv8 model loaded successfully")
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        raise


def decode_image(base64_string: str) -> np.ndarray:
    """
    Decode base64 image to numpy array
    
    Args:
        base64_string: Base64 encoded image
        
    Returns:
        numpy array representing the image
    """
    try:
        # Remove data URL prefix if present
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        # Decode base64 to bytes
        img_bytes = base64.b64decode(base64_string)
        
        # Convert to numpy array
        nparr = np.frombuffer(img_bytes, np.uint8)
        
        # Decode image
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise ValueError("Failed to decode image")
            
        return img
    except Exception as e:
        logger.error(f"Error decoding image: {e}")
        raise


def determine_position(x_center: float, frame_width: int) -> str:
    """
    Determine if object is on left, center, or right
    
    Args:
        x_center: X coordinate of object center
        frame_width: Width of the frame
        
    Returns:
        Position string: 'left', 'center', or 'right'
    """
    left_threshold = frame_width * 0.33
    right_threshold = frame_width * 0.67
    
    if x_center < left_threshold:
        return "left"
    elif x_center > right_threshold:
        return "right"
    else:
        return "center"


def estimate_distance(bbox_area: float, frame_area: float) -> str:
    """
    Rough distance estimation based on bounding box size
    
    Args:
        bbox_area: Area of bounding box
        frame_area: Total frame area
        
    Returns:
        Distance category: 'very close', 'close', 'medium', or 'far'
    """
    ratio = bbox_area / frame_area
    
    if ratio > 0.3:
        return "very close"
    elif ratio > 0.15:
        return "close"
    elif ratio > 0.05:
        return "medium distance"
    else:
        return "far"


# Priority objects for navigation assistance
PRIORITY_OBJECTS = {
    'person': 10,
    'car': 9,
    'truck': 9,
    'bus': 9,
    'bicycle': 8,
    'motorcycle': 8,
    'chair': 7,
    'bench': 7,
    'couch': 7,
    'door': 6,
    'stairs': 10,  # Custom detection needed
    'table': 5,
    'traffic light': 8,
    'stop sign': 8,
    'dog': 7,
    'cat': 6,
}


def filter_important_objects(detections: List[Dict]) -> List[Dict]:
    """
    Filter and prioritize important objects for navigation
    
    Args:
        detections: List of all detected objects
        
    Returns:
        Filtered and sorted list of important objects
    """
    important = []
    
    for det in detections:
        obj_class = det['class']
        if obj_class in PRIORITY_OBJECTS:
            det['priority'] = PRIORITY_OBJECTS[obj_class]
            important.append(det)
    
    # Sort by priority (highest first) and then by size
    important.sort(key=lambda x: (x['priority'], x['bbox_area']), reverse=True)
    
    # Return top 5 most important
    return important[:5]


def generate_voice_message(detections: List[Dict], frame_width: int, frame_height: int) -> str:
    """
    Generate natural language message for voice output
    
    Args:
        detections: List of detected objects with positions
        frame_width: Width of frame
        frame_height: Height of frame
        
    Returns:
        Human-readable message string
    """
    if not detections:
        return "Path is clear."
    
    messages = []
    frame_area = frame_width * frame_height
    
    # Group by position
    positions = {'left': [], 'center': [], 'right': []}
    
    for det in detections:
        pos = det['position']
        obj_name = det['class']
        distance = det['distance']
        
        positions[pos].append(f"{obj_name} {distance}")
    
    # Build message with most important objects
    if positions['center']:
        messages.append(f"{positions['center'][0]} ahead")
    
    if positions['left']:
        messages.append(f"{positions['left'][0]} on your left")
    
    if positions['right']:
        messages.append(f"{positions['right'][0]} on your right")
    
    if not messages:
        return "Path is clear."
    
    return ". ".join(messages).capitalize() + "."


@app.on_event("startup")
async def startup_event():
    """Load model on startup"""
    load_model()


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "message": "AI Navigation Assistant API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "timestamp": "2026-02-14"
    }


@app.post("/detect", response_model=DetectionResponse)
async def detect_objects(request: ImageRequest):
    """
    Main detection endpoint
    
    Accepts base64 encoded image and returns detected objects with voice message
    """
    if model is None:
        raise HTTPException(status_code=503, message="Model not loaded")
    
    try:
        # Decode image
        img = decode_image(request.image)
        height, width = img.shape[:2]
        frame_area = width * height
        
        # Run YOLOv8 detection
        results = model(img, conf=request.min_confidence, verbose=False)
        
        # Process detections
        detections = []
        
        for result in results:
            boxes = result.boxes
            
            for box in boxes:
                # Extract box information
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                class_name = result.names[class_id]
                
                # Calculate center and area
                x_center = (x1 + x2) / 2
                y_center = (y1 + y2) / 2
                bbox_area = (x2 - x1) * (y2 - y1)
                
                # Determine position and distance
                position = determine_position(x_center, width)
                distance = estimate_distance(bbox_area, frame_area)
                
                detection = {
                    'class': class_name,
                    'confidence': round(confidence, 2),
                    'bbox': [float(x1), float(y1), float(x2), float(y2)],
                    'center': [float(x_center), float(y_center)],
                    'position': position,
                    'distance': distance,
                    'bbox_area': float(bbox_area)
                }
                
                detections.append(detection)
        
        # Filter important objects
        important_detections = filter_important_objects(detections)
        
        # Generate voice message
        message = generate_voice_message(important_detections, width, height)
        
        logger.info(f"Detected {len(detections)} objects, {len(important_detections)} important")
        
        return DetectionResponse(
            message=message,
            detections=important_detections,
            frame_width=width,
            frame_height=height
        )
        
    except Exception as e:
        logger.error(f"Detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/detect-with-query")
async def detect_with_query(request: ImageRequest, query: str = ""):
    """
    Detection with specific query (Phase 2 - Voice Commands)
    
    Example queries:
    - "What's in front?"
    - "Is there a person nearby?"
    - "Any obstacles?"
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Decode and detect
        img = decode_image(request.image)
        height, width = img.shape[:2]
        
        results = model(img, conf=request.min_confidence, verbose=False)
        
        # Process all detections
        all_objects = []
        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                class_name = result.names[class_id]
                confidence = float(box.conf[0])
                
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                x_center = (x1 + x2) / 2
                bbox_area = (x2 - x1) * (y2 - y1)
                
                all_objects.append({
                    'class': class_name,
                    'confidence': confidence,
                    'position': determine_position(x_center, width),
                    'distance': estimate_distance(bbox_area, width * height)
                })
        
        # Filter based on query
        query_lower = query.lower()
        
        if "person" in query_lower or "people" in query_lower:
            people = [obj for obj in all_objects if obj['class'] == 'person']
            if people:
                message = f"Yes, {len(people)} person" + ("s" if len(people) > 1 else "")
                message += f" detected. {people[0]['distance']} on your {people[0]['position']}."
            else:
                message = "No people detected nearby."
        
        elif "front" in query_lower or "ahead" in query_lower:
            center_objects = [obj for obj in all_objects if obj['position'] == 'center']
            if center_objects:
                obj = center_objects[0]
                message = f"{obj['class']} {obj['distance']} ahead."
            else:
                message = "Path ahead is clear."
        
        elif "obstacle" in query_lower:
            if all_objects:
                important = filter_important_objects(all_objects)
                message = f"{len(important)} obstacle" + ("s" if len(important) > 1 else "")
                message += f" detected. Main: {important[0]['class']} on your {important[0]['position']}."
            else:
                message = "No obstacles detected."
        
        else:
            # Default: describe scene
            important = filter_important_objects(all_objects)
            message = generate_voice_message(important, width, height)
        
        return {
            "message": message,
            "query": query,
            "detections": all_objects[:10]
        }
        
    except Exception as e:
        logger.error(f"Query detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)