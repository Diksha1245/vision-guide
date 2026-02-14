# Vision Guide - Frontend

Web-based AI navigation assistant interface for visually impaired users.

## Features

- **📹 Camera Access**: Uses device camera (preferably rear camera)
- **🎯 Real-time Detection**: Processes frames every 1-3 seconds
- **🔊 Voice Feedback**: Text-to-speech for navigation guidance
- **🎤 Voice Commands**: Quick query buttons for specific questions
- **⚙️ Customizable Settings**: Adjust detection interval, voice speed, confidence
- **📊 Live Statistics**: Detection count, response time monitoring
- **♿ Accessible Design**: High contrast, large touch targets

## Setup

### Local Development

1. **Simple HTTP Server** (Python):
```bash
cd frontend
python3 -m http.server 8080
```

2. **Node.js HTTP Server**:
```bash
npm install -g http-server
cd frontend
http-server -p 8080
```

3. Open browser: `http://localhost:8080`

### Deployment

#### GitHub Pages (Free)
1. Create GitHub repository
2. Push frontend files
3. Enable GitHub Pages in repository settings
4. Access at: `https://yourusername.github.io/repo-name/`

#### Netlify (Free)
1. Create Netlify account
2. Drag and drop frontend folder
3. Get instant HTTPS URL

#### Vercel (Free)
1. Install Vercel CLI: `npm i -g vercel`
2. Run: `vercel` in frontend directory
3. Follow prompts

## Configuration

### API URL
Set the backend API URL in settings:
- Local development: `http://localhost:8000`
- Production: Your deployed backend URL (must be HTTPS for camera access)

### Settings Explained

| Setting | Default | Description |
|---------|---------|-------------|
| API URL | localhost:8000 | Backend server address |
| Voice Speed | 1.0x | Speech rate (0.5x - 2.0x) |
| Detection Interval | 1.0s | Time between detections |
| Confidence | 0.4 | Minimum detection confidence |

## Browser Requirements

### Required Features
- ✅ Camera API (getUserMedia)
- ✅ Canvas API
- ✅ Web Speech API (Text-to-Speech)
- ✅ ES6+ JavaScript

### Supported Browsers
- ✅ Safari 14+ (iOS/macOS)
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Edge 90+

### iOS Safari Specific
- **Camera permission**: User must grant access
- **HTTPS required**: Camera only works on HTTPS (except localhost)
- **No autoplay**: User must tap "Start Navigation"

## Usage Guide

### Basic Navigation
1. Open website in browser
2. Tap "Start Navigation"
3. Grant camera permission
4. Hold phone in front of you
5. Listen to voice guidance

### Voice Commands
Tap buttons to ask specific questions:
- "What's in front?" - Describes objects ahead
- "People nearby?" - Detects persons
- "Any obstacles?" - Lists all obstacles

### Tips for Best Results
- 📱 Hold phone steady
- 💡 Ensure good lighting
- 🎯 Point camera forward
- 🔊 Enable sound
- 📶 Stable internet connection

## Architecture

```
┌─────────────────┐
│   User Device   │
│  (iPhone/iPad)  │
└────────┬────────┘
         │
    ┌────▼────┐
    │ Safari  │
    │ Browser │
    └────┬────┘
         │
    ┌────▼────────────────┐
    │  Vision Guide UI    │
    ├─────────────────────┤
    │ • Camera Capture    │
    │ • Frame Compression │
    │ • API Communication │
    │ • Voice Output      │
    └────┬────────────────┘
         │ HTTPS
    ┌────▼────────────────┐
    │   Backend API       │
    │ (FastAPI + YOLO)    │
    └─────────────────────┘
```

## File Structure

```
frontend/
├── index.html          # Main HTML structure
├── styles.css          # Beautiful, accessible styles
├── app.js             # Application logic
└── README.md          # This file
```

## Customization

### Change Colors
Edit `styles.css` CSS variables:
```css
:root {
    --primary: #0066FF;      /* Main accent color */
    --secondary: #00D9A3;    /* Secondary color */
    --bg-dark: #0A0E1A;      /* Background */
}
```

### Add Custom Voice Commands
Edit `app.js` and add buttons in `index.html`:
```javascript
function askQuestion(query) {
    // Existing implementation
}
```

### Modify Detection Interval
Change default in HTML:
```html
<input id="detectionInterval" value="1" ... >
```

## Accessibility Features

- 🎨 High contrast design
- 🔤 Large, readable fonts
- 👆 Large touch targets (min 44x44px)
- 🔊 Screen reader friendly
- ⌨️ Keyboard navigation support
- 🌓 Reduced motion support
- 🎯 ARIA labels

## Performance Optimization

### Image Compression
- Captures at 640x480 resolution
- JPEG compression at 80% quality
- ~50-100KB per frame

### Network Usage
- 1 detection/second = ~6MB/minute
- Adjust interval to reduce data usage
- Consider WiFi for extended use

### Battery Life
- Camera usage is intensive
- Recommend portable charger
- Reduce detection interval if needed

## Troubleshooting

### Camera Not Working
- ✅ Check permissions in browser settings
- ✅ Ensure HTTPS (required for camera)
- ✅ Try different browser
- ✅ Restart browser/device

### No Voice Output
- ✅ Check device volume
- ✅ Disable silent mode
- ✅ Test in browser settings
- ✅ Try different browser

### API Connection Failed
- ✅ Check API URL in settings
- ✅ Verify backend is running
- ✅ Check network connection
- ✅ Look at browser console (F12)

### Slow Detection
- ✅ Increase detection interval
- ✅ Check internet speed
- ✅ Backend may need better server
- ✅ Reduce image quality

## Security & Privacy

- 🔒 All processing on your server
- 📵 No data stored
- 🚫 No tracking or analytics
- 🔐 HTTPS required in production
- 👤 Camera access only when active

## Future Enhancements

- [ ] Offline mode (WebGL.js for local detection)
- [ ] GPS integration for location context
- [ ] Haptic feedback
- [ ] Multiple language support
- [ ] History log
- [ ] Custom alert sounds
- [ ] Geofencing for known locations
- [ ] Integration with smart glasses

## Contributing

Suggestions welcome! Focus areas:
- Accessibility improvements
- Performance optimization
- UI/UX enhancements
- Voice command expansion

## License

MIT License - Free to use and modify