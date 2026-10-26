# Changelog

## Unreleased — proposed v1.1.1

- Gate track association by known detection class to reduce cross-class ID switches in `--all-classes` mode.
- Add regression tests for crossed classes and missing class metadata.

## v1.1.0 — 2026-10-23

- Added CLI for input/output, headless mode, tracking configuration and short smoke runs.
- Added Windows one-click launcher and original synthetic test-clip generator.
- Fixed gated assignment behavior, with parity tests for optional native C++ backend.
- Retained last detected bounding-box dimensions instead of drawing arbitrary 60x60 boxes.
- Added deterministic Python tests and an optional native-backend CI job.
- Added contributor, security, benchmark, and application preparation documentation.
- Removed unverified claims of FPS, ID stability, and native acceleration speedups.

