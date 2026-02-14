/**
 * Vision Guide - AI Navigation Assistant
 * Frontend Application Logic
 */

class VisionGuide {
    constructor() {
        // DOM Elements
        this.video = document.getElementById('video');
        this.canvas = document.getElementById('canvas');
        this.startBtn = document.getElementById('startBtn');
        this.stopBtn = document.getElementById('stopBtn');
        this.statusText = document.getElementById('statusText');
        this.detectionMessage = document.getElementById('detectionMessage');
        this.detectionCount = document.getElementById('detectionCount');
        this.responseTime = document.getElementById('responseTime');
        this.voiceStatus = document.getElementById('voiceStatus');
        
        // Settings
        this.apiUrl = document.getElementById('apiUrl');
        this.voiceRate = document.getElementById('voiceRate');
        this.detectionInterval = document.getElementById('detectionInterval');
        this.confidence = document.getElementById('confidence');
        
        // State
        this.stream = null;
        this.detectionLoop = null;
        this.isRunning = false;
        this.lastMessage = '';
        this.synth = window.speechSynthesis;
        this.currentUtterance = null;
        
        // Statistics
        this.stats = {
            totalDetections: 0,
            averageResponseTime: 0,
            responseTimes: []
        };
        
        // Initialize
        this.init();
    }
    
    init() {
        // Event listeners
        this.startBtn.addEventListener('click', () => this.start());
        this.stopBtn.addEventListener('click', () => this.stop());
        
        // Settings change handlers
        this.voiceRate.addEventListener('input', (e) => {
            document.getElementById('voiceRateValue').textContent = `${e.target.value}x`;
        });
        
        this.detectionInterval.addEventListener('input', (e) => {
            document.getElementById('intervalValue').textContent = `${e.target.value}s`;
            if (this.isRunning) {
                this.restartDetectionLoop();
            }
        });
        
        this.confidence.addEventListener('input', (e) => {
            document.getElementById('confidenceValue').textContent = e.target.value;
        });
        
        // Load saved settings
        this.loadSettings();
        
        // Check browser support
        this.checkBrowserSupport();
        
        console.log('Vision Guide initialized');
    }
    
    checkBrowserSupport() {
        // Check for required APIs
        const requirements = {
            camera: navigator.mediaDevices && navigator.mediaDevices.getUserMedia,
            speech: 'speechSynthesis' in window,
            canvas: !!document.createElement('canvas').getContext
        };
        
        const missing = Object.entries(requirements)
            .filter(([key, value]) => !value)
            .map(([key]) => key);
        
        if (missing.length > 0) {
            alert(`Missing required features: ${missing.join(', ')}. Please use a modern browser.`);
        }
        
        return missing.length === 0;
    }
    
    async start() {
        try {
            this.updateStatus('Starting camera...', 'warning');
            
            // Request camera access
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    facingMode: 'environment', // Use back camera on mobile
                    width: { ideal: 640 },
                    height: { ideal: 480 }
                }
            });
            
            // Set video source
            this.video.srcObject = this.stream;
            
            // Wait for video to be ready
            await new Promise((resolve) => {
                this.video.onloadedmetadata = resolve;
            });
            
            // Update UI
            this.startBtn.style.display = 'none';
            this.stopBtn.style.display = 'inline-flex';
            this.isRunning = true;
            
            this.updateStatus('Active', 'success');
            this.speak('Vision guide started. Navigation active.');
            
            // Start detection loop
            this.startDetectionLoop();
            
            console.log('Camera started successfully');
            
        } catch (error) {
            console.error('Error starting camera:', error);
            alert('Unable to access camera. Please check permissions.');
            this.updateStatus('Error', 'danger');
        }
    }
    
    stop() {
        // Stop camera stream
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
        
        // Stop detection loop
        this.stopDetectionLoop();
        
        // Update UI
        this.startBtn.style.display = 'inline-flex';
        this.stopBtn.style.display = 'none';
        this.isRunning = false;
        
        this.updateStatus('Stopped', 'warning');
        this.detectionMessage.textContent = 'Navigation stopped';
        
        // Stop speech
        this.synth.cancel();
        
        console.log('Camera stopped');
    }
    
    startDetectionLoop() {
        const interval = parseFloat(this.detectionInterval.value) * 1000;
        
        this.detectionLoop = setInterval(() => {
            this.detectObjects();
        }, interval);
        
        // Run first detection immediately
        this.detectObjects();
    }
    
    stopDetectionLoop() {
        if (this.detectionLoop) {
            clearInterval(this.detectionLoop);
            this.detectionLoop = null;
        }
    }
    
    restartDetectionLoop() {
        this.stopDetectionLoop();
        this.startDetectionLoop();
    }
    
    async detectObjects() {
        if (!this.isRunning) return;
        
        try {
            const startTime = performance.now();
            
            // Capture frame from video
            const imageData = this.captureFrame();
            
            // Send to API
            const response = await fetch(`${this.apiUrl.value}/detect`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    image: imageData,
                    min_confidence: parseFloat(this.confidence.value)
                })
            });
            
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }
            
            const result = await response.json();
            const endTime = performance.now();
            const responseTime = Math.round(endTime - startTime);
            
            // Update statistics
            this.updateStatistics(result, responseTime);
            
            // Update UI and speak message
            this.handleDetectionResult(result);
            
        } catch (error) {
            console.error('Detection error:', error);
            this.updateStatus('Connection Error', 'danger');
            this.detectionMessage.textContent = 'Unable to connect to server';
        }
    }
    
    captureFrame() {
        // Set canvas size to match video
        this.canvas.width = this.video.videoWidth;
        this.canvas.height = this.video.videoHeight;
        
        // Draw current video frame to canvas
        const ctx = this.canvas.getContext('2d');
        ctx.drawImage(this.video, 0, 0);
        
        // Convert to base64 data URL
        return this.canvas.toDataURL('image/jpeg', 0.8);
    }
    
    handleDetectionResult(result) {
        const message = result.message;
        
        // Update detection message
        this.detectionMessage.textContent = message;
        
        // Speak if message changed (avoid repetition)
        if (message !== this.lastMessage) {
            this.speak(message);
            this.lastMessage = message;
        }
    }
    
    speak(text) {
    this.synth.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = parseFloat(this.voiceRate.value);
    utterance.pitch = 1;
    utterance.volume = 1;

    // Get all available voices
    const voices = this.synth.getVoices();

    // Find a British English voice
    const britishVoice = voices.find(voice =>
        voice.lang === "en-GB"
    );

    if (britishVoice) {
        utterance.voice = britishVoice;
        console.log("Using British voice:", britishVoice.name);
    } else {
        console.log("British voice not found, using default");
    }

    utterance.onstart = () => {
        this.voiceStatus.textContent = 'Speaking';
    };

    utterance.onend = () => {
        this.voiceStatus.textContent = 'Ready';
    };

    this.synth.speak(utterance);
}

    
    updateStatistics(result, responseTime) {
        // Update detection count
        this.stats.totalDetections++;
        this.detectionCount.textContent = this.stats.totalDetections;
        
        // Update response time
        this.stats.responseTimes.push(responseTime);
        if (this.stats.responseTimes.length > 10) {
            this.stats.responseTimes.shift();
        }
        
        const avgTime = Math.round(
            this.stats.responseTimes.reduce((a, b) => a + b, 0) / 
            this.stats.responseTimes.length
        );
        
        this.responseTime.textContent = `${avgTime}ms`;
    }
    
    updateStatus(text, type = 'default') {
        this.statusText.textContent = text;
        
        const pulseRing = document.querySelector('.pulse-ring');
        
        // Update color based on type
        const colors = {
            success: '#00CC66',
            warning: '#FFB800',
            danger: '#FF3366',
            default: '#A0AEC0'
        };
        
        if (pulseRing) {
            pulseRing.style.background = colors[type] || colors.default;
        }
    }
    
    loadSettings() {
        // Load settings from localStorage
        const saved = localStorage.getItem('visionGuideSettings');
        if (saved) {
            try {
                const settings = JSON.parse(saved);
                if (settings.apiUrl) this.apiUrl.value = settings.apiUrl;
                if (settings.voiceRate) this.voiceRate.value = settings.voiceRate;
                if (settings.detectionInterval) this.detectionInterval.value = settings.detectionInterval;
                if (settings.confidence) this.confidence.value = settings.confidence;
            } catch (e) {
                console.error('Error loading settings:', e);
            }
        }
        
        // Save settings on change
        const saveSettings = () => {
            const settings = {
                apiUrl: this.apiUrl.value,
                voiceRate: this.voiceRate.value,
                detectionInterval: this.detectionInterval.value,
                confidence: this.confidence.value
            };
            localStorage.setItem('visionGuideSettings', JSON.stringify(settings));
        };
        
        this.apiUrl.addEventListener('change', saveSettings);
        this.voiceRate.addEventListener('change', saveSettings);
        this.detectionInterval.addEventListener('change', saveSettings);
        this.confidence.addEventListener('change', saveSettings);
    }
}

// Voice command function (for button triggers)
async function askQuestion(query) {
    const guide = window.visionGuide;
    
    if (!guide || !guide.isRunning) {
        alert('Please start navigation first');
        return;
    }
    
    try {
        guide.updateStatus('Processing query...', 'warning');
        
        // Capture current frame
        const imageData = guide.captureFrame();
        
        // Send query to API
        const response = await fetch(
            `${guide.apiUrl.value}/detect-with-query?query=${encodeURIComponent(query)}`,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    image: imageData,
                    min_confidence: parseFloat(guide.confidence.value)
                })
            }
        );
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        const result = await response.json();
        
        // Update UI and speak
        guide.detectionMessage.textContent = result.message;
        guide.speak(result.message);
        guide.updateStatus('Active', 'success');
        
        console.log('Query response:', result.message);
        
    } catch (error) {
        console.error('Query error:', error);
        guide.updateStatus('Error', 'danger');
        alert('Unable to process query. Check API connection.');
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.visionGuide = new VisionGuide();
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (window.visionGuide && window.visionGuide.isRunning) {
        if (document.hidden) {
            // Page hidden - pause detection
            window.visionGuide.stopDetectionLoop();
        } else {
            // Page visible - resume detection
            window.visionGuide.startDetectionLoop();
        }
    }
});

// Prevent accidental page refresh
window.addEventListener('beforeunload', (event) => {
    if (window.visionGuide && window.visionGuide.isRunning) {
        event.preventDefault();
        event.returnValue = 'Navigation is active. Are you sure you want to leave?';
    }
});