# Python Vision Tracking Engine

![Python](https://img.shields.io/badge/Python-3.12-blue)
![C++](https://img.shields.io/badge/C%2B%2B-17-blue)
![Computer Vision](https://img.shields.io/badge/Computer%20Vision-Tracking-success)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow)

Real-time multi-object tracking system built with Python and C++ implementing:

* YOLOv8-based object detection
* Kalman Filter (constant velocity model)
* Hungarian Algorithm (C++ accelerated)
* Multi-object track lifecycle management
* Real-time video processing and visualization

This project focuses on **state estimation, data association, and real-time tracking performance**.

---

## Quick Start

```bash
pip install -r requirements.txt
python main.py
```

---

## Example Output

The system performs real-time tracking with:

* Stable object IDs
* Smooth trajectories (Kalman filter)
* No frequent ID switching
* Real-time FPS display

Overlay includes:

* Bounding boxes
* Track IDs
* Motion direction
* Active track count
* Backend type (Python / C++)

---

## System Pipeline

```text
Video Input
→ YOLO Detection
→ Cost Matrix Computation
→ Hungarian Assignment (C++)
→ Kalman Filter Update
→ Track Management
→ Visualization
```

---

## Detection

* YOLOv8 (Ultralytics)
* Real-time inference
* Confidence filtering
* Person-class filtering

---

## Tracking Core

### Kalman Filter

* Constant velocity model
* State: `[x, y, vx, vy]`
* Prediction + update cycle
* Smooth trajectory estimation

### Data Association

* Cost matrix based on Euclidean distance
* Hungarian Algorithm (optimal assignment)
* C++ backend via `ctypes`

Fallback:

* Python (SciPy) implementation

---

## Multi-Object Tracking

* Unique track IDs
* Track creation from new detections
* Track deletion after missed frames
* Occlusion handling (short-term)
* Motion-based prediction

---

## C++ Integration

* Hungarian algorithm implemented in C++
* Compiled as shared library (`.dll`)
* Loaded in Python using `ctypes`
* Static linking to remove runtime dependency issues

---

## Project Structure

```text
python-vision-tracking-engine/
│
├── main.py
├── config.py
├── requirements.txt
├── .gitignore
│
├── cpp/
│   ├── hungarian_bridge.cpp
│   ├── build_hungarian.ps1
│   └── build/
│
├── src/
│   ├── detection/
│   │   └── yolo_detector.py
│   │
│   ├── tracking/
│   │   ├── kalman_filter.py
│   │   ├── track.py
│   │   ├── tracker.py
│   │   ├── assignment.py
│   │   └── utils.py
│   │
│   ├── io/
│   │   ├── video_reader.py
│   │   └── video_writer.py
│   │
│   └── visualization/
│       └── draw.py
│
└── data/
    └── input/
        └── sample_video.mp4
```

---

## Build C++ Hungarian

```bash
powershell -ExecutionPolicy Bypass -File .\\cpp\\build_hungarian.ps1
```

---

## Performance

* Real-time tracking (~20–35 FPS depending on hardware)
* Stable ID assignment
* Reduced ID switching
* Efficient assignment via C++ backend

---

## Engineering Highlights

* Real-time multi-object tracking pipeline
* Kalman-based motion estimation
* Optimal assignment via Hungarian algorithm
* Python ↔ C++ integration
* Modular and scalable architecture

---

## Technologies

* Python (OpenCV, NumPy, SciPy)
* YOLOv8 (Ultralytics)
* C++17 (Hungarian Algorithm)
* ctypes (Python-C++ bridge)

---

## License

MIT

---

## Author

Ali Eray Kalaycı
Computer Engineering
Focus: Computer Vision, Tracking Systems, Real-Time AI
