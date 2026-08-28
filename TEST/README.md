# Vehicle Detection System with Roboflow

A Flask web application that captures video frames from an ESP32 camera, processes them using Roboflow's vehicle detection AI, and displays real-time object detection with bounding boxes and confidence scores.

## Features

- **Real-time Video Streaming**: Connects to an ESP32 camera module and streams live video feed
- **AI-Powered Vehicle Detection**: Uses Roboflow's pre-trained bike-vehicle-detection model
- **Multi-class Detection**: Identifies multiple vehicle types:
  - Cars (Green)
  - Motorcycles (Red)
  - Trucks (Blue)
  - Buses (Orange)
  - Bicycles (Magenta)
- **Live Bounding Boxes**: Displays detection results with class labels and confidence scores
- **LED Feedback**: Toggles an ESP32 LED based on car detection
- **Status Monitoring**: Provides real-time detection status via REST API

## Requirements

- Python 3.7+
- Flask
- OpenCV (cv2)
- NumPy
- Requests
- ESP32 camera module
- Roboflow API account

## Installation

1. **Clone/download the project** to your local machine

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install flask opencv-python numpy requests
   ```

## Configuration

Update the following settings in `roboflow.py`:

```python
ESP32_IP = "192.168.1.08"  # Your ESP32 camera IP address
ROBOFLOW_URL = "http://localhost:9001/snowies-workspace/workflows/..."  # Your Roboflow workflow URL
API_KEY = "Kno6UrEbmrpiEYq3SLBW"  # Your Roboflow API key
```

## Usage

1. **Start the Flask server**:
   ```bash
   python roboflow.py
   ```

2. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

3. **View the live stream** with real-time vehicle detection and annotations

## API Endpoints

### GET `/`
- Returns the main HTML interface with video stream
- **Response**: HTML page with embedded video player

### GET `/stream`
- Real-time MJPEG video stream with detections
- **Response**: Multipart/JPEG stream (continuous video frames)
- **Mimetype**: `multipart/x-mixed-replace; boundary=frame`

### GET `/status`
- Returns current car detection status
- **Response**: JSON object
  ```json
  {
    "car": true/false
  }
  ```

## How It Works

1. **Frame Capture**: Retrieves video frames from the ESP32 camera via HTTP
2. **Object Detection**: Sends each frame to Roboflow API for vehicle classification
3. **Drawing**: Annotates frames with bounding boxes, class labels, and confidence percentages
4. **LED Control**: Toggles the ESP32 LED based on car detection
5. **Streaming**: Sends annotated frames to the web interface in real-time

## File Structure

```
TEST/
├── roboflow.py                 # Main Flask application
├── testscript.py               # Test script on single images
├── test_v4.html                # Frontend HTML interface
├── video estrada.mp4           # Sample video file
├── local-file-processed-*.mp4  # Processed video output
└── README.md                
```

## Troubleshooting

### Connection Issues
- Verify ESP32 is powered and connected to the network
- Ensure ESP32_IP address matches device's IP
- Check firewall settings on port 5000

### Roboflow API Errors
- Verify API_KEY is correct and valid
- Check the Roboflow workflow URL is correct
- Ensure Roboflow service is running (if using local deployment)

### Frame Parsing Errors
- Check console output for detailed error messages
- Verify the response format from Roboflow matches expected structure
- Test manually: `curl http://{ESP32_IP}/image`

## Performance Tips

- Reduce image resolution on ESP32 for faster processing
- Increase timeout values if experiencing slow connections
- Use threading (enabled: `threaded=True`) for better concurrent handling

## Author

Developed for the AM2R project
