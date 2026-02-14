# AI Navigation Assistant - Backend

FastAPI backend with YOLOv8 object detection for real-time navigation assistance for visually impaired users.

## Features

- **Real-time Object Detection**: YOLOv8 nano model for fast, accurate detection
- **Position Awareness**: Determines if objects are left, center, or right
- **Distance Estimation**: Rough distance based on object size
- **Priority Filtering**: Focuses on navigation-critical objects
- **Voice Message Generation**: Natural language output for TTS
- **Query Mode**: Answer specific questions about the scene

## Setup

### Option 1: Local Development

```bash
# Run setup script
chmod +x setup.sh
./setup.sh

# Activate virtual environment
source venv/bin/activate

# Start server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Option 2: Docker

```bash
# Build image
docker build -t ai-nav-backend .

# Run container
docker run -p 8000:8000 ai-nav-backend
```

### Option 3: Cloud Deployment

#### AWS EC2
1. Launch Ubuntu 20.04 instance (t2.medium recommended)
2. SSH into instance
3. Install dependencies:
```bash
sudo apt update
sudo apt install python3-pip python3-venv
```
4. Clone/upload code
5. Run setup.sh
6. Use screen/tmux or systemd for persistent running

#### Google Cloud Platform
1. Create Compute Engine instance
2. Same steps as AWS

#### Render (Free Tier)
1. Create new Web Service
2. Connect repository
3. Use these settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

## API Endpoints

### GET /health
Health check endpoint
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

### POST /detect
Main detection endpoint

**Request:**
```json
{
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
  "min_confidence": 0.4
}
```

**Response:**
```json
{
  "message": "Person close ahead. Chair on your left.",
  "detections": [
    {
      "class": "person",
      "confidence": 0.89,
      "position": "center",
      "distance": "close",
      "bbox": [120, 80, 340, 480]
    }
  ],
  "frame_width": 640,
  "frame_height": 480
}
```

### POST /detect-with-query
Detection with voice query

**Parameters:**
- `query`: Natural language question (e.g., "Is there a person nearby?")

**Response:**
```json
{
  "message": "Yes, 1 person detected. Close on your center.",
  "query": "Is there a person nearby?",
  "detections": [...]
}
```

## Architecture

```
Frontend (Safari/Browser)
    ↓ POST /detect
Backend API (FastAPI)
    ↓
Image Preprocessing (OpenCV)
    ↓
YOLOv8 Detection Model
    ↓
Object Filtering & Logic
    ↓
Message Generation
    ↓ JSON Response
Frontend (Text-to-Speech)
```

## Object Priority

High Priority (9-10):
- person, car, truck, bus, stairs

Medium Priority (7-8):
- bicycle, motorcycle, chair, bench, traffic light

Lower Priority (5-6):
- table, door, couch

## Testing

```bash
# Test API
python test_api.py

# Manual test with curl
curl -X POST http://localhost:8000/detect \
  -H "Content-Type: application/json" \
  -d '{"image": "data:image/jpeg;base64,..."}'
```

## Performance

- Model: YOLOv8 nano (fastest)
- Average inference: ~50-100ms on CPU
- Recommended: GPU for <30ms inference
- Memory: ~500MB

## Environment Variables

```bash
export MODEL_NAME=yolov8n.pt  # or yolov8s.pt for better accuracy
export MIN_CONFIDENCE=0.4
export MAX_DETECTIONS=10
```

## Production Considerations

1. **HTTPS**: Use reverse proxy (nginx) with SSL
2. **Rate Limiting**: Add rate limiting middleware
3. **Authentication**: Add API keys if needed
4. **Monitoring**: Use logging and metrics
5. **Scaling**: Use multiple workers or container orchestration

## License

MIT