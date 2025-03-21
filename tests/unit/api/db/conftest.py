"""Configuration for database unit tests.

This ensures that the 'src' directory is in the Python path for tests.
"""

import os
import sys
from pathlib import Path

# Get the repo root (4 levels up from this file)
repo_root = Path(__file__).parents[3].parent
src_dir = repo_root / "src"

# Add src to the Python path
if os.path.exists(src_dir) and str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))
    print(f"Added {src_dir} to Python path")
