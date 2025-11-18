# GBA Save Fixer for MuOS

A utility for converting Game Boy Advance save files between mGBA and VBA formats on the Anbernic RG34XXSP running MuOS.

## Overview

This tool solves the binary incompatibility between mGBA (default emulator on MuOS) and VBA (standard on PC/Mac) by removing the 16-byte RTC footer that mGBA appends to save files.

### Save File Formats

- **mGBA Format**: 131,088 bytes (128KB + 16-byte RTC footer)
- **VBA/Standard Format**: 131,072 bytes (128KB)

The converter detects mGBA saves and converts them to the standard VBA format, making them compatible with PC/Mac emulators and flashcarts.

## Features

- **Interactive TUI**: whiptail-based menu system optimized for 720x480 display
- **Automatic Detection**: Identifies save file format by size
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

1. Launch "GBA Save Fixer" from the MuOS Applications menu
2. Select a .sav file from the list
3. Confirm the conversion
4. The tool will:
   - Create a backup (.bak file)
   - Remove the 16-byte RTC footer
   - Display conversion results

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

### Conversion Algorithm

1. **Detection**: Check file size (131,088 bytes = mGBA format)
2. **Validation**: Verify file exists and size is valid
3. **Backup**: Create .bak copy of original
4. **Sanitization**: Truncate last 16 bytes (RTC footer)
5. **Result**: Standard 131,072 byte VBA-compatible file

### File Locations

The tool searches for .sav files in:
- `/mnt/sdcard/ROMS/GBA` (SD Slot 2)
- `/mnt/mmc/ROMS/GBA` (SD Slot 1)

## Safety Features

- **Automatic Backups**: Original file saved as `.bak` before conversion
- **Atomic Writes**: Uses temporary files and fsync() to ensure data integrity
- **Sleep Protection**: File operations complete atomically to prevent corruption if device sleeps
- **Validation**: Checks file size and format before conversion

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## Acknowledgments

Built for the MuOS community and Anbernic RG34XXSP users.
