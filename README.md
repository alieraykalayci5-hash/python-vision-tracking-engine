# Python Vision Tracking Engine

[![Python](https://img.shields.io/badge/Python-3.10--3.12-blue)](#requirements)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![Tests](https://github.com/alieraykalayci5-hash/python-vision-tracking-engine/actions/workflows/tests.yml/badge.svg)](https://github.com/alieraykalayci5-hash/python-vision-tracking-engine/actions/workflows/tests.yml)

**Research/educational baseline** for person tracking across video frames. Combines [Ultralytics YOLO](https://github.com/ultralytics/ultralytics) object detections, a constant-velocity Kalman filter and distance-gated Hungarian matching, with optional compiled C++ assignment.

> This is an experimental tracker, **not** a validated production tracking, surveillance, or safety system. No verified IDF1/HOTA or cross-device FPS claims are made.

## How it works

`Video → YOLO detections → person filter → Kalman predictions → gated assignment (SciPy / optional C++) → track lifecycle → overlay → output MP4`

Each track receives an integer ID. Tracks become visible after three associated detections, and expire after the configured number of consecutive missed frames. The rendered box uses the most recently detected width and height, centered on the estimated location; it is not a fully estimated shape.

## Demo

You can see the previous sample visualization in [assets/demo.gif](assets/demo.gif) and [assets/sample_output.png](assets/sample_output.png). These screenshots are illustrative, not evidence of measured tracking quality. Ensure you have rights to redistribute any media included in the repository.

![Demo](assets/demo.gif)

## Requirements

- Python **3.10–3.12** recommended (desktop Windows/Linux/macOS).
- Internet access on first setup to install packages and, if not present, download `yolov8n.pt` from Ultralytics.
- For optional C++ native library: a C++17 compiler. **SciPy fallback works without it.**
- A user-provided video with permission to process it, or the included generator for a synthetic I/O smoke test.

### Windows: one-click setup

Double-click **`start_windows.bat`**. It creates `.venv`, installs dependencies once and starts the video pipeline. If no sample input video is present, it generates a synthetic geometric sample.

**Important:** Synthetic shapes are not persons. YOLO may report **zero person tracks** on that clip. For a meaningful detection demo, use a video you are authorized to process and set `--input` manually.

The generated output goes to `data/output/tracked_video.mp4`. The first setup may require a large PyTorch download. If the preview window is not supported, run with `--headless`.

### Manual setup

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
python tools/make_synthetic_demo.py
python main.py --headless --input data/input/sample_video.mp4
```

For a real video:

```bash
python main.py --input /path/to/video.mp4 --output data/output/result.mp4 --headless
python main.py --help
```

Default filtering tracks COCO `class_id=0` (people). To track all detected classes, add `--all-classes` (IDs may swap more often when different classes are close). Webcam cameras can be selected with `--input 0`. `--max-frames 100` runs a short diagnostic.

### Optional C++ assignment

The C++ matcher is optional and **not assumed faster without measurements**.

```bash
# Linux/macOS
bash cpp/build_hungarian.sh
# Windows PowerShell with g++ in PATH
powershell -ExecutionPolicy Bypass -File cpp/build_hungarian.ps1
```

Windows: `cpp/build/hungarian.dll`; Linux: `cpp/build/libhungarian.so`; macOS: `cpp/build/libhungarian.dylib`. The loader finds these at startup. `PVTE_FORCE_SCIPY=1` bypasses native code.

## Tests

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

The basic tests do **not** download YOLO weights. They cover assignment, track lifecycle, CLI validation and an end-to-end frame I/O smoke test with a **fake detector**. They are not proof of actual YOLO accuracy. CI also compiles the Linux C++ backend and checks matching parity.

## Repository layout

- `src/detection/`: YOLO wrapper
- `src/tracking/`: Kalman filter, assignment and track management
- `src/visualization/`: rendering
- `src/io/`: video reading/writing
- `cpp/`: optional native matcher
- `tests/`: deterministic regression suite
- `tools/`: synthetic test video generator
- `docs/`: roadmap, benchmark methodology and program application notes

## Evaluation and limitations

- Matching is based on **Euclidean centre distance**, not object appearance or IoU. Identity switches remain possible during crossings and occlusions.
- Only confirmed tracks are drawn. Confidence, overlap handling and camera motion can affect outcomes.
- Metrics must be collected on labeled data. See [benchmark methodology](docs/BENCHMARKS.md).
- Uploads do not include model weights or third-party footage; respect model, dataset and package licenses independently of this repository's MIT-licensed original source code. **Ultralytics may impose AGPL-3.0 or commercial licensing obligations**, so check the current terms for the versions and use cases you choose: https://www.ultralytics.com/license

## Open source collaboration

Please read [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md) and [CHANGELOG.md](CHANGELOG.md). Follow the [roadmap](docs/ROADMAP.md). Maintainers should publish verified releases and evidence of actual adoption instead of implying that GitHub stars or usage exist.

## License

Original code in this repository: [MIT License](LICENSE). Dependencies, pretrained model weights and third-party media carry **their own licenses** and are not relicensed by this repository.

Maintainer: Ali Eray Kalaycı
