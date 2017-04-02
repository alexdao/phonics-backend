# Phonics Server
Backend for Phonics written in Node.js. Uses YOLO, a real-time object detection ML framework for processing. Interfaces with the Phonics Android app and the Phonics Google Home app.

## Clients
Google home app can be found [here](https://github.com/alexdao/phonics-google-home-app)

Android app can be found [here](https://github.com/alexdao/phonics-android)
## Usage
Start server:
```
$node index.js
```

Process a single image with YOLO, which outputs to `predictions.png`:
```
$./darknet detect cfg/yolo.cfg yolo.weights out.png
```
