#!/usr/bin/env python3
"""
GBA Save Converter - Bidirectional mGBA <-> VBA Format Converter
Converts between mGBA (with RTC footer) and VBA (standard) save formats
"""

import os
import sys
import platform
import shutil
import struct
import time

# Constants
MGBA_SIZE = 131088  # 128KB + 16-byte RTC footer
VBA_SIZE = 131072   # Standard 128KB
RTC_FOOTER_SIZE = 16
MIN_SAFE_DISK_SPACE = 1048576  # 1MB minimum free space


def check_file_permissions(filepath):
    """
    Check if we have read/write permissions for the file and directory.

    Args:
        filepath: Path to check

    Returns:
        tuple: (success: bool, error_message: str or None)
    """
    if not os.access(filepath, os.R_OK):
        return False, f"No read permission for file: {filepath}"

    if not os.access(filepath, os.W_OK):
        return False, f"No write permission for file: {filepath}"

    dir_path = os.path.dirname(filepath) or '.'
    if not os.access(dir_path, os.W_OK):
        return False, f"No write permission for directory: {dir_path}"

    return True, None


def check_disk_space(filepath):
    """
    Check if there's enough disk space for the operation.

    Args:
        filepath: Path to the file

    Returns:
        tuple: (success: bool, error_message: str or None)
    """
    try:
        stat = os.statvfs(os.path.dirname(filepath) or '.')
        free_space = stat.f_bavail * stat.f_frsize

        if free_space < MIN_SAFE_DISK_SPACE:
            return False, f"Insufficient disk space: {free_space} bytes available, need at least {MIN_SAFE_DISK_SPACE}"

        return True, None
    except Exception as e:
        # If we can't check disk space, warn but continue
        return True, None


def validate_save_file(filepath, expected_size=None):
    """
    Validate that the file appears to be a valid save file.

    Args:
        filepath: Path to the file
        expected_size: Expected size in bytes, or None to accept VBA_SIZE or MGBA_SIZE

    Returns:
        tuple: (success: bool, error_message: str or None)
    """
    file_size = os.path.getsize(filepath)

    if expected_size is not None:
        if file_size != expected_size:
            return False, f"Invalid file size: {file_size} bytes, expected {expected_size} bytes"
    else:
        if file_size not in [VBA_SIZE, MGBA_SIZE]:
            return False, f"Invalid file size: {file_size} bytes (expected {VBA_SIZE} or {MGBA_SIZE})"

    return True, None


def create_rtc_footer():
    """
    Create a 16-byte RTC footer for mGBA saves.

    The footer contains:
    - 4 bytes: seconds since epoch (uint32)
    - 12 bytes: padding/additional RTC data

    Returns:
        bytes: 16-byte RTC footer
    """
    timestamp = int(time.time())
    # Pack timestamp as little-endian uint32, followed by 12 zero bytes
    footer = struct.pack('<I', timestamp) + b'\x00' * 12
    return footer


def convert_mgba_to_vba(filepath):
    """
    Convert mGBA save file to VBA format by removing RTC footer.

    Args:
        filepath: Path to the .sav file

    Returns:
        tuple: (success: bool, message: str)
    """
    # Validate file size
    success, error = validate_save_file(filepath, MGBA_SIZE)
    if not success:
        return False, f"ERROR: {error}"

    # Check permissions
    success, error = check_file_permissions(filepath)
    if not success:
        return False, f"ERROR: {error}"

    # Check disk space
    success, error = check_disk_space(filepath)
    if not success:
        return False, f"ERROR: {error}"

    try:
        # Create backup
        backup_path = filepath + ".bak"
        try:
            shutil.copy2(filepath, backup_path)
        except IOError as e:
            return False, f"ERROR: Failed to create backup: {e}"

        # Read the file
        try:
            with open(filepath, 'rb') as f:
                data = f.read()
        except IOError as e:
            return False, f"ERROR: Failed to read file: {e}"

        # Verify we read the correct amount
        if len(data) != MGBA_SIZE:
            return False, f"ERROR: File size mismatch after read: {len(data)} bytes"

        # Trim the last 16 bytes (RTC footer)
        trimmed_data = data[:VBA_SIZE]

        # Write back atomically with fsync
        temp_path = filepath + ".tmp"
        try:
            with open(temp_path, 'wb') as f:
                f.write(trimmed_data)
                f.flush()
                os.fsync(f.fileno())
        except IOError as e:
            # Clean up temp file if it exists
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return False, f"ERROR: Failed to write converted file: {e}"

        # Atomic rename
        try:
            os.replace(temp_path, filepath)
        except OSError as e:
            return False, f"ERROR: Failed to replace original file: {e}"

        # Verify the conversion
        new_size = os.path.getsize(filepath)
        if new_size != VBA_SIZE:
            return False, f"ERROR: Conversion verification failed: file is {new_size} bytes, expected {VBA_SIZE}"

        return True, f"SUCCESS: Converted mGBA to VBA format\nOriginal: {MGBA_SIZE} bytes -> New: {VBA_SIZE} bytes\nBackup: {backup_path}"

    except Exception as e:
        return False, f"ERROR: Unexpected error during conversion: {e}"


def convert_vba_to_mgba(filepath):
    """
    Convert VBA save file to mGBA format by adding RTC footer.

    Args:
        filepath: Path to the .sav file

    Returns:
        tuple: (success: bool, message: str)
    """
    # Validate file size
    success, error = validate_save_file(filepath, VBA_SIZE)
    if not success:
        return False, f"ERROR: {error}"

    # Check permissions
    success, error = check_file_permissions(filepath)
    if not success:
        return False, f"ERROR: {error}"

    # Check disk space
    success, error = check_disk_space(filepath)
    if not success:
        return False, f"ERROR: {error}"

    try:
        # Create backup
        backup_path = filepath + ".bak"
        try:
            shutil.copy2(filepath, backup_path)
        except IOError as e:
            return False, f"ERROR: Failed to create backup: {e}"

        # Read the file
        try:
            with open(filepath, 'rb') as f:
                data = f.read()
        except IOError as e:
            return False, f"ERROR: Failed to read file: {e}"

        # Verify we read the correct amount
        if len(data) != VBA_SIZE:
            return False, f"ERROR: File size mismatch after read: {len(data)} bytes"

        # Create RTC footer
        rtc_footer = create_rtc_footer()

        # Append the RTC footer
        mgba_data = data + rtc_footer

        # Write back atomically with fsync
        temp_path = filepath + ".tmp"
        try:
            with open(temp_path, 'wb') as f:
                f.write(mgba_data)
                f.flush()
                os.fsync(f.fileno())
        except IOError as e:
            # Clean up temp file if it exists
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return False, f"ERROR: Failed to write converted file: {e}"

        # Atomic rename
        try:
            os.replace(temp_path, filepath)
        except OSError as e:
            return False, f"ERROR: Failed to replace original file: {e}"

        # Verify the conversion
        new_size = os.path.getsize(filepath)
        if new_size != MGBA_SIZE:
            return False, f"ERROR: Conversion verification failed: file is {new_size} bytes, expected {MGBA_SIZE}"

        return True, f"SUCCESS: Converted VBA to mGBA format\nOriginal: {VBA_SIZE} bytes -> New: {MGBA_SIZE} bytes\nBackup: {backup_path}"

    except Exception as e:
        return False, f"ERROR: Unexpected error during conversion: {e}"


def convert_save(filepath, direction="auto"):
    """
    Convert save file between mGBA and VBA formats.

    Args:
        filepath: Path to the .sav file
        direction: "auto", "to-vba", or "to-mgba"

    Returns:
        str: Status message
    """
    # Check if file exists
    if not os.path.exists(filepath):
        return f"ERROR: File not found: {filepath}"

    if not os.path.isfile(filepath):
        return f"ERROR: Not a file: {filepath}"

    # Get file size
    try:
        file_size = os.path.getsize(filepath)
    except OSError as e:
        return f"ERROR: Cannot access file: {e}"

    # Auto-detect conversion direction
    if direction == "auto":
        if file_size == MGBA_SIZE:
            direction = "to-vba"
        elif file_size == VBA_SIZE:
            direction = "to-mgba"
        else:
            return f"ERROR: Unknown format (file size: {file_size} bytes)\nExpected {MGBA_SIZE} bytes (mGBA) or {VBA_SIZE} bytes (VBA)"

    # Perform conversion based on direction
    if direction == "to-vba":
        if file_size == VBA_SIZE:
            return "INFO: File is already in VBA format (131,072 bytes)"
        success, message = convert_mgba_to_vba(filepath)
        return message

    elif direction == "to-mgba":
        if file_size == MGBA_SIZE:
            return "INFO: File is already in mGBA format (131,088 bytes)"
        success, message = convert_vba_to_mgba(filepath)
        return message

    else:
        return f"ERROR: Invalid direction: {direction} (use 'auto', 'to-vba', or 'to-mgba')"


def main():
    """Main entry point"""
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: convert.py <save_file.sav> [direction]")
        print("  direction: auto (default), to-vba, or to-mgba")
        sys.exit(1)

    filepath = sys.argv[1]
    direction = sys.argv[2] if len(sys.argv) == 3 else "auto"

    result = convert_save(filepath, direction)
    print(result)

    # Exit with appropriate code
    if result.startswith("SUCCESS") or result.startswith("INFO"):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
