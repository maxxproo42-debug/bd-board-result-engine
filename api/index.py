import os
import sys

# Ensure parent directory is in path so it can import app and dinajpur_engine
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from app import app
