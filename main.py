"""Root main module - exposes backend app for deployment."""
from backend.main import app

# For Railway/other platforms that expect main:app
__all__ = ["app"]

def main():
    print("Hello from llm-council!")


if __name__ == "__main__":
    main()
