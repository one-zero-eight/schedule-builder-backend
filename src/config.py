import os
from pathlib import Path

from dotenv import load_dotenv

from src.config_schema import Settings


load_dotenv()
settings_path = os.getenv("SETTINGS_PATH", "settings.yaml")
settings: Settings = Settings.from_yaml(Path(settings_path))
DEBUG = os.getenv("DEBUG") == "1"
