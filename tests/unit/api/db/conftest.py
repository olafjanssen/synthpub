"""Configuration for database unit tests.

This ensures that the 'src' directory is in the Python path for tests.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path if not already there
src_dir = Path(__file__).parents[3].parent / "src"
if os.path.exists(src_dir) and str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))
