import os
import sys
from pathlib import Path

import uvicorn

# Change dir to project root (three levels up from this file)
os.chdir(Path(__file__).parents[2])
# Get arguments from command
args = sys.argv[1:]

uvicorn.main.main(
    [
        "src.presentation.app:app",
        "--reload",
        "--port=8000",
        "--host=0.0.0.0",
        *args,
    ]
)
