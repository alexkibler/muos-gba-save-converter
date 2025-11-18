FROM python:3.11-slim-bookworm

# Install whiptail and basic utils to mimic MuOS environment
RUN apt-get update && apt-get install -y whiptail coreutils && rm -rf /var/lib/apt/lists/*

# Create the MuOS directory structure mock
RUN mkdir -p /mnt/mmc/MUOS/application/GBA_Fixer \
    && mkdir -p /mnt/sdcard/ROMS/GBA

# Set working directory
WORKDIR /mnt/mmc/MUOS/application/GBA_Fixer

# Copy the application files into the container
COPY GBA_Fixer/launch.sh ./
COPY GBA_Fixer/convert.py ./
COPY GBA_Fixer/assets ./assets

# Make scripts executable
RUN chmod +x launch.sh convert.py

# Default command
CMD ["/bin/bash"]
