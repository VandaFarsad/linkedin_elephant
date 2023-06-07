from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
SUB_BASE_DIR = Path(__file__).resolve().parent.parent
FEED_EXPORT_PATH = SUB_BASE_DIR / "feed_export"
LOGS_PATH = SUB_BASE_DIR / "logs"
