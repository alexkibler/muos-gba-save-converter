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
        echo "$counter"
        echo "$filename ($size)"
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
        --menu "Choose a .sav file to convert from mGBA to VBA format:" \
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

    # Show confirmation dialog with file details
    FILENAME=$(basename "$FILEPATH")
    FILESIZE=$(ls -lh "$FILEPATH" | awk '{print $5}')

    if whiptail --title "Confirm Conversion" \
        --yesno "Convert this file?\n\nFile: $FILENAME\nSize: $FILESIZE\n\nA backup (.bak) will be created automatically." \
        $MENU_HEIGHT $MENU_WIDTH; then

        # Execute the Python conversion script
        RESULT=$(python3 "$SCRIPT_DIR/convert.py" "$FILEPATH" 2>&1)
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
