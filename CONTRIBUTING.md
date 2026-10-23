# Contributing

We welcome useful, reproducible improvements to Python Vision Tracking Engine.

1. Search existing issues before creating a new one. Discuss large architectural changes first.
2. Create a focused branch and send a pull request with the underlying problem, tests, and expected behavior.
3. For core tracking changes run `python -m pytest -q` after `pip install -r requirements-dev.txt`.
4. For native backend changes, build `cpp/build_hungarian.sh` (Linux/macOS) or `cpp/build_hungarian.ps1` (Windows), then rerun tests.
5. Keep benchmarks honest: publish hardware, model, input, commands, measured values, and commit SHA. Do not invent tracking metrics.
6. Never include private videos, personally identifying footage, model weights without redistribution rights, credentials, or generated output.

## Reporting issues
Include your Python version, OS, exact command, traceback, minimal reproduction, and whether `PVTE_FORCE_SCIPY=1` changes the behavior.

## Maintainer process
Contributions are reviewed when available. No fixed response SLA is promised.
Please be respectful and discuss changes constructively.
