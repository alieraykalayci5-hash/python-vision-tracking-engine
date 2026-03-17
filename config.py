from pathlib import Path

PROJECT_NAME = "Python Vision Tracking Engine"

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"
LOG_DIR = OUTPUT_DIR / "logs"
FRAMES_DIR = OUTPUT_DIR / "frames"

VIDEO_SOURCE = str(INPUT_DIR / "sample_video.mp4")
OUTPUT_VIDEO_PATH = str(OUTPUT_DIR / "tracked_video.mp4")

DISPLAY_WINDOW_NAME = "Python Vision Tracking Engine"
EXIT_KEY = ord("q")

SAVE_OUTPUT = True
SHOW_VIDEO = True