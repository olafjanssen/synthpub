"""Test package initialization.

This module sets up the Python path for tests to use 'src' as the root folder.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
src_dir = Path(__file__).parent.parent / 'src'
if os.path.exists(src_dir) and src_dir not in sys.path:
    sys.path.insert(0, str(src_dir))
