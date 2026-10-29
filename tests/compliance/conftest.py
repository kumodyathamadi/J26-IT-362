"""
Component 2 Test Configuration

Sets sys.path so that 'backend.app.*' imports work from any working directory.
"""
import sys
from pathlib import Path

# Repo root (two levels up from tests/compliance/)
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
