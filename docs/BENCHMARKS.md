# Benchmarks and evaluation

No general-purpose FPS / IDF1 / HOTA / MOTA / ID-switching numbers have yet been verified or published for this project.

## Assignment-only microbenchmark (reproducible)

Use this command from the repository root after installing the development dependencies:

```bash
python -m tools.benchmark_assignment --sizes 10 30 60 --iterations 30 --warmups 5 --seed 2026 --json-output data/output/assignment_benchmark.json
```

- The input is a **fixed-seed synthetic square cost matrix** of the requested size; values are sampled up to 1.5 times the matching threshold so some pairs are forbidden.
- Warmup runs are excluded from reported samples. Median and p95 are per-call assignment solver latency in milliseconds.
- Both backends (when available) receive identical inputs; the script checks matched-pair count and total matching cost rather than requiring identical tie-breaking.
- JSON records operating system, Python/NumPy/SciPy versions, random seed, matrix sizes, thresholds, samples and latencies. Save real reports with your hardware details before citing a result.
- Native results are null if C++ is not compiled. No performance advantage is asserted by default.
- **These are NOT detector inference FPS, video processing FPS, MOT accuracy, IDF1, or HOTA.** For full-pipeline validation use real authorized footage and labeled benchmarks separately.

Do not publish timings from CI/shared virtual runners as a representative hardware performance claim.

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
