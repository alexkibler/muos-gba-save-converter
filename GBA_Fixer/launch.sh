#!/bin/sh
# NAME: GBA Save Fixer
# ICON: icon.png
# CATEGORY: Utility

# Whiptail dimensions optimized for 720x480 display (3:2 aspect ratio)
MENU_HEIGHT=20
MENU_WIDTH=85
LIST_HEIGHT=12

# Script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Search paths for .sav files
SEARCH_PATHS="/mnt/sdcard/ROMS/GBA /mnt/mmc/ROMS/GBA"

# Function to detect save format
get_save_format() {
    local filepath=$1
    local size=$(stat -c%s "$filepath" 2>/dev/null || stat -f%z "$filepath" 2>/dev/null)

    if [ "$size" = "131088" ]; then
        echo "mGBA"
    elif [ "$size" = "131072" ]; then
        echo "VBA"
    else
        echo "Unknown"
    fi
}

# Function to scan for .sav files
find_save_files() {
    find $SEARCH_PATHS -type f -name "*.sav" 2>/dev/null | sort
}

# Function to build menu items for whiptail
build_menu() {
    local counter=1
    find_save_files | while read -r filepath; do
        # Get just the filename for display
        filename=$(basename "$filepath")
        # Get file size
        size=$(ls -lh "$filepath" | awk '{print $5}')
        # Get format
        format=$(get_save_format "$filepath")
        echo "$counter"
        echo "$filename ($size - $format)"
        counter=$((counter + 1))
    done
}

# Function to get filepath by index
get_filepath_by_index() {
    local index=$1
    find_save_files | sed -n "${index}p"
}

# Main loop
while true; do
    # Build the menu dynamically
    MENU_ITEMS=$(build_menu)

    if [ -z "$MENU_ITEMS" ]; then
        whiptail --title "GBA Save Fixer" \
            --msgbox "No .sav files found in:\n\n/mnt/sdcard/ROMS/GBA\n/mnt/mmc/ROMS/GBA\n\nPlease check your ROM directories." \
            $MENU_HEIGHT $MENU_WIDTH
        exit 0
    fi

    # Display file selection menu
    SELECTION=$(echo "$MENU_ITEMS" | xargs whiptail --title "GBA Save Fixer - Select File" \
        --menu "Choose a .sav file to convert:\n(Formats: mGBA=131088 bytes, VBA=131072 bytes)" \
        $MENU_HEIGHT $MENU_WIDTH $LIST_HEIGHT \
        --cancel-button "Exit" \
        3>&1 1>&2 2>&3)

    # Check if user cancelled
    if [ $? -ne 0 ]; then
        exit 0
    fi

    # Get the selected filepath
    FILEPATH=$(get_filepath_by_index "$SELECTION")

    if [ -z "$FILEPATH" ]; then
        whiptail --title "Error" \
            --msgbox "Failed to locate selected file." \
            $MENU_HEIGHT $MENU_WIDTH
        continue
    fi

    # Get file details
    FILENAME=$(basename "$FILEPATH")
    FILESIZE=$(ls -lh "$FILEPATH" | awk '{print $5}')
    FORMAT=$(get_save_format "$FILEPATH")

    # Select conversion direction
    DIRECTION=$(whiptail --title "Select Conversion Direction" \
        --menu "Current format: $FORMAT\n\nChoose conversion direction:" \
        $MENU_HEIGHT $MENU_WIDTH 3 \
        "auto" "Auto-detect (recommended)" \
        "to-vba" "Convert to VBA format" \
        "to-mgba" "Convert to mGBA format" \
        --cancel-button "Back" \
        3>&1 1>&2 2>&3)

    # Check if user cancelled
    if [ $? -ne 0 ]; then
        continue
    fi

    # Determine conversion description for confirmation
    case "$DIRECTION" in
        "auto")
            if [ "$FORMAT" = "mGBA" ]; then
                CONV_DESC="mGBA → VBA (remove RTC footer)"
            elif [ "$FORMAT" = "VBA" ]; then
                CONV_DESC="VBA → mGBA (add RTC footer)"
            else
                CONV_DESC="Auto-detect format and convert"
            fi
            ;;
        "to-vba")
            CONV_DESC="Convert to VBA format (remove RTC footer)"
            ;;
        "to-mgba")
            CONV_DESC="Convert to mGBA format (add RTC footer)"
            ;;
    esac

    # Show confirmation dialog with file details
    if whiptail --title "Confirm Conversion" \
        --yesno "File: $FILENAME\nSize: $FILESIZE\nCurrent Format: $FORMAT\n\nConversion: $CONV_DESC\n\nA backup (.bak) will be created automatically.\n\nProceed?" \
        $MENU_HEIGHT $MENU_WIDTH; then

        # Execute the Python conversion script
        RESULT=$(python3 "$SCRIPT_DIR/convert.py" "$FILEPATH" "$DIRECTION" 2>&1)
        EXIT_CODE=$?

        # Display result
        if [ $EXIT_CODE -eq 0 ]; then
            whiptail --title "Conversion Complete" \
                --msgbox "$RESULT" \
                $MENU_HEIGHT $MENU_WIDTH
        else
            whiptail --title "Conversion Failed" \
                --msgbox "$RESULT" \
                $MENU_HEIGHT $MENU_WIDTH
        fi
    fi
done
