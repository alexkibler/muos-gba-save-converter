# GBA Save Fixer for MuOS

A utility for converting Game Boy Advance save files between mGBA and VBA formats on the Anbernic RG34XXSP running MuOS.

## Overview

This tool solves the binary incompatibility between mGBA (default emulator on MuOS) and VBA (standard on PC/Mac) save files. It provides **bidirectional conversion** between the two formats.

### Save File Formats

- **mGBA Format**: 131,088 bytes (128KB + 16-byte RTC footer)
- **VBA/Standard Format**: 131,072 bytes (128KB)

The converter can:
- **mGBA → VBA**: Remove the 16-byte RTC footer for compatibility with PC/Mac emulators and flashcarts
- **VBA → mGBA**: Add an RTC footer to standard saves for use with mGBA on MuOS

## Features

- **Bidirectional Conversion**: Convert between mGBA and VBA formats in both directions
- **Interactive TUI**: whiptail-based menu system optimized for 720x480 display
- **Format Detection**: Automatically identifies save file format (mGBA/VBA) and displays it
- **Flexible Conversion Modes**:
  - Auto-detect: Automatically determines conversion direction
  - Manual selection: Choose specific conversion direction (to-vba or to-mgba)
- **Enhanced Error Handling**:
  - File permission validation
  - Disk space checking
  - File integrity verification
  - Detailed error messages
- **Safe Conversion**: Creates .bak backup before modifying files
- **Atomic Operations**: Uses fsync() to prevent corruption if device sleeps mid-write
- **Dual-Path Search**: Scans both SD card slots for .sav files

## Installation

### Method 1: Manual Installation

1. Copy the `GBA_Fixer` folder to your MuOS device:
   ```
   /mnt/mmc/MUOS/application/GBA_Fixer/
   ```

2. Ensure the directory structure looks like this:
   ```
   /mnt/mmc/MUOS/application/GBA_Fixer/
   ├── launch.sh
   ├── convert.py
   └── assets/
       ├── icon.png
       └── preview.png
   ```

3. Make sure scripts are executable:
   ```bash
   chmod +x /mnt/mmc/MUOS/application/GBA_Fixer/launch.sh
   chmod +x /mnt/mmc/MUOS/application/GBA_Fixer/convert.py
   ```

### Method 2: MuOS Archive Manager

1. Create a zip file containing the GBA_Fixer folder
2. Place the zip in the Archive folder on your SD card
3. Use the MuOS Archive Manager to install

## Usage

### Interactive Mode (On Device)

1. Launch "GBA Save Fixer" from the MuOS Applications menu
2. **Select a save file** from the list (files show format: mGBA/VBA)
3. **Choose conversion direction**:
   - **Auto** (recommended): Automatically converts based on current format
   - **to-vba**: Force conversion to VBA format (removes RTC footer)
   - **to-mgba**: Force conversion to mGBA format (adds RTC footer)
4. **Confirm** the conversion details
5. The tool will:
   - Create a backup (.bak file)
   - Perform the conversion
   - Verify the result
   - Display conversion results

### Command Line Mode

You can also use the converter directly from the command line:

```bash
# Auto-detect and convert
python3 convert.py /path/to/savefile.sav

# Force conversion to VBA format
python3 convert.py /path/to/savefile.sav to-vba

# Force conversion to mGBA format
python3 convert.py /path/to/savefile.sav to-mgba
```

## Development & Testing

### Docker Testing (Recommended for macOS)

Test the application in a Linux environment that mimics MuOS:

```bash
# Build the Docker image
docker build -t muos-test .

# Run the container with your project mounted
docker run -it --rm -v $(pwd)/GBA_Fixer:/mnt/mmc/MUOS/application/GBA_Fixer muos-test /bin/bash

# Inside the container, test the UI
./launch.sh
```

### Local Testing (macOS with Homebrew)

```bash
# Install whiptail
brew install newt

# Test the Python converter directly
python3 GBA_Fixer/convert.py /path/to/savefile.sav
```

## Technical Details

### Hardware Target
- **Device**: Anbernic RG34XXSP
- **OS**: MuOS (Linux)
- **Display**: 720x480 (3:2 aspect ratio)
- **Python**: 3.x (pre-installed on MuOS)

### Conversion Algorithms

#### mGBA → VBA (Remove RTC Footer)

1. **Detection**: Check file size (131,088 bytes = mGBA format)
2. **Validation**: Verify file exists, permissions, and disk space
3. **Backup**: Create .bak copy of original
4. **Conversion**: Truncate last 16 bytes (RTC footer)
5. **Verification**: Confirm result is exactly 131,072 bytes
6. **Result**: Standard VBA-compatible file

#### VBA → mGBA (Add RTC Footer)

1. **Detection**: Check file size (131,072 bytes = VBA format)
2. **Validation**: Verify file exists, permissions, and disk space
3. **Backup**: Create .bak copy of original
4. **RTC Generation**: Create 16-byte footer with current timestamp
5. **Conversion**: Append RTC footer to save data
6. **Verification**: Confirm result is exactly 131,088 bytes
7. **Result**: mGBA-compatible file with RTC support

### File Locations

The tool searches for .sav files in:
- `/mnt/sdcard/ROMS/GBA` (SD Slot 2)
- `/mnt/mmc/ROMS/GBA` (SD Slot 1)

## Safety Features

- **Automatic Backups**: Original file saved as `.bak` before conversion
- **Atomic Writes**: Uses temporary files and fsync() to ensure data integrity
- **Sleep Protection**: File operations complete atomically to prevent corruption if device sleeps
- **Comprehensive Validation**:
  - File existence and type checking
  - File size validation (must be exactly 131,072 or 131,088 bytes)
  - Read/write permission verification
  - Directory write access validation
  - Minimum disk space checking (1MB required)
  - Post-conversion verification
- **Error Recovery**:
  - Automatic cleanup of temporary files on failure
  - Detailed error messages for troubleshooting
  - Graceful handling of edge cases

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## Acknowledgments

Built for the MuOS community and Anbernic RG34XXSP users.
