#!/usr/bin/env python3
"""
Setup Gemini API Key

Saves the Gemini API key to the project's .env file.

Usage:
    python setup_api_key.py --key "your-api-key"
"""

import argparse
import sys
from pathlib import Path


def setup_api_key(api_key: str) -> bool:
    """
    Save API key to .env file.

    Args:
        api_key: The Gemini API key to save

    Returns:
        True if successful, False otherwise
    """
    env_file = Path.cwd() / '.env'

    # Read existing content if file exists
    existing_lines = []
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                # Skip existing GEMINI_API_KEY lines
                if not line.strip().startswith('GEMINI_API_KEY='):
                    existing_lines.append(line)

    # Ensure file ends with newline before adding new key
    if existing_lines and not existing_lines[-1].endswith('\n'):
        existing_lines[-1] += '\n'

    # Add new API key
    existing_lines.append(f'GEMINI_API_KEY="{api_key}"\n')

    # Write back
    try:
        with open(env_file, 'w') as f:
            f.writelines(existing_lines)

        print(f"✅ API key saved to {env_file}")
        print("")
        print("You can now use the Gemini code review feature.")
        print("The key will be automatically loaded from .env file.")
        return True
    except PermissionError:
        print(f"❌ Permission denied: Cannot write to {env_file}")
        return False
    except Exception as e:
        print(f"❌ Failed to save API key: {e}")
        return False


def validate_key_format(key: str) -> bool:
    """Basic validation of API key format."""
    if not key:
        return False
    if len(key) < 20:
        return False
    if ' ' in key:
        return False
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Setup Gemini API Key for code review",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Get your API key at: https://aistudio.google.com/apikey

Examples:
  python setup_api_key.py --key "AIzaSy..."
        """
    )
    parser.add_argument(
        "--key",
        required=True,
        help="Your Gemini API key"
    )

    args = parser.parse_args()

    # Validate key format
    if not validate_key_format(args.key):
        print("❌ Invalid API key format")
        print("   Key should be at least 20 characters with no spaces")
        sys.exit(1)

    # Setup the key
    if setup_api_key(args.key):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
