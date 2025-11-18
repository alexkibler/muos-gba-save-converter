#!/usr/bin/env python3
"""
GBA Save Converter - mGBA to VBA Format
Removes the 16-byte RTC footer from mGBA save files for VBA compatibility
"""

import os
import sys
import platform
import shutil

# Constants
MGBA_SIZE = 131088  # 128KB + 16-byte RTC footer
VBA_SIZE = 131072   # Standard 128KB
RTC_FOOTER_SIZE = 16

def convert_save(filepath):
    """
    Convert mGBA save file to VBA format by removing RTC footer.

    Args:
        filepath: Path to the .sav file

    Returns:
        str: Status message
    """
    # Check if file exists
    if not os.path.isfile(filepath):
        return f"ERROR: File not found: {filepath}"

    # Get file size
    file_size = os.path.getsize(filepath)

    # Check if already in VBA format
    if file_size == VBA_SIZE:
        return "SUCCESS: File is already in VBA format (131,072 bytes)"

    # Check if it's an mGBA save file
    if file_size == MGBA_SIZE:
        try:
            # Create backup
            backup_path = filepath + ".bak"
            shutil.copy2(filepath, backup_path)

            # Read the file
            with open(filepath, 'rb') as f:
                data = f.read()

            # Trim the last 16 bytes (RTC footer)
            trimmed_data = data[:VBA_SIZE]

            # Write back atomically with fsync
            temp_path = filepath + ".tmp"
            with open(temp_path, 'wb') as f:
                f.write(trimmed_data)
                f.flush()
                os.fsync(f.fileno())

            # Atomic rename
            os.replace(temp_path, filepath)

            return f"SUCCESS: Converted mGBA save to VBA format\nOriginal: {MGBA_SIZE} bytes -> New: {VBA_SIZE} bytes\nBackup saved as: {backup_path}"

        except Exception as e:
            return f"ERROR: Conversion failed: {str(e)}"

    # Unknown file size
    return f"ERROR: Unknown format (file size: {file_size} bytes)\nExpected {MGBA_SIZE} bytes (mGBA) or {VBA_SIZE} bytes (VBA)"


def main():
    """Main entry point"""
    if len(sys.argv) != 2:
        print("Usage: convert.py <save_file.sav>")
        sys.exit(1)

    filepath = sys.argv[1]
    result = convert_save(filepath)
    print(result)

    # Exit with appropriate code
    if result.startswith("SUCCESS"):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
