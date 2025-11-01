#!/usr/bin/env python3

import subprocess
import sys
from pathlib import Path


def main():
    # Get paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    requirements_file = project_root / "app" / "vendor" / "requirements.txt"
    vendor_dir = project_root / "app" / "vendor"

    # Validate requirements.txt exists
    if not requirements_file.exists():
        print(f"Error: requirements.txt not found at {requirements_file}", file=sys.stderr)
        sys.exit(1)

    # Create vendor directory if it doesn't exist
    vendor_dir.mkdir(parents=True, exist_ok=True)

    print(f"Installing dependencies from {requirements_file} to {vendor_dir}...")

    # Install dependencies
    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "-r",
                str(requirements_file),
                "--target",
                str(vendor_dir),
                "--upgrade"
            ],
            check=True,
            capture_output=False
        )

        print("\n✅ Dependencies installed successfully!")
        return 0

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Failed to install dependencies. Exit code: {e.returncode}", file=sys.stderr)
        return e.returncode
    except Exception as e:
        print(f"\n❌ An error occurred: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
