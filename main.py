"""Root main module - exposes backend app for deployment."""
import sys
import os

# Ensure the project root is on the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from backend.main import app
except ImportError as e:
    print(f"Error importing backend.main: {e}")
    print(f"Python path: {sys.path}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Project root: {project_root}")
    raise

# For Railway/other platforms that expect main:app
__all__ = ["app"]

def main():
    print("Hello from llm-council!")


if __name__ == "__main__":
    main()
