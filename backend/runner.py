# runner.py
import json
import argparse

from agent2 import create_spec  # <-- this is your existing Wayflow logic

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=str, required=False)
    parser.add_argument("--audio", type=str, required=False)
    args = parser.parse_args()

    # Call your existing sync function that uses Wayflow
    # e.g. create_spec(image_path, audio_path) -> dict with overview, etc.
    result = create_spec(args.image)

    # Make sure result is JSON-serializable dict
    # Example:
    # result = {
    #   "overview": "...",
    #   "requirements": "...",
    #   "architecture": "...",
    #   "code": "...",
    #   "docs": "..."
    # }

    print(json.dumps(result))


if __name__ == "__main__":
    main()
