# Phonics Server
Backend for Phonics written in Node.js. Uses YOLO, a real-time object detection ML framework for processing. Interfaces with the Phonics Android app and the Phonics Google Home app. 

## Usage
Start server:
```
$node index.js
```

Process a single image with YOLO, which outputs to `predictions.png`:
```
$./darknet detect cfg/yolo.cfg yolo.weights out.png
```
