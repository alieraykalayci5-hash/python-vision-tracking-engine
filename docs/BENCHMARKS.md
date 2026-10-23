# Benchmarks and evaluation

No general-purpose FPS / IDF1 / HOTA / MOTA / ID-switching numbers have yet been verified or published for this project.

## Reproducible measurement procedure

1. Log the Git commit, OS, CPU, GPU, Python, PyTorch, OpenCV, YOLO and SciPy versions.
2. Obtain footage or datasets that permit use and redistribution; record video resolution, FPS, duration, and dataset provenance.
3. Warm the detector for several frames before reporting steady-state throughput; do **not** include first-run model downloads.
4. Capture frame latency distribution (mean, median, p95), alongside end-to-end FPS including video I/O and drawing.
5. Run the same inputs under `PVTE_FORCE_SCIPY=1` and the compiled native backend before claiming speedups.
6. Tracking metrics such as IDF1/HOTA require ground-truth labels and an evaluation protocol. Frame throughput does not measure tracking correctness.

For an initial **diagnostic only**, run:

```bash
python main.py --input path/to/authorized_video.mp4 --headless --max-frames 300
```

The command prints a rough end-to-end FPS including setup; it is NOT a standalone formal benchmark.

| Commit | Hardware | Input | Model | Backend | Frames | FPS | Notes |
|---|---|---|---|---:|---:|---:|---|
| (not yet measured) | — | — | — | — | — | — | Pending reproducible benchmark |
