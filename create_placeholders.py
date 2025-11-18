#!/usr/bin/env python3
"""
Create placeholder PNG images for GBA Save Fixer
Uses pypng library (pure Python, no dependencies)
"""

import struct

def create_png(width, height, filename, bg_color=(44, 62, 80)):
    """
    Create a simple PNG file with a solid color background.

    Args:
        width: Image width in pixels
        height: Image height in pixels
        filename: Output filename
        bg_color: RGB tuple for background color
    """
    # PNG signature
    png_signature = b'\x89PNG\r\n\x1a\n'

    # Create IHDR chunk (image header)
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    ihdr_chunk = create_chunk(b'IHDR', ihdr_data)

    # Create image data (all pixels same color)
    # Each row starts with filter type 0 (no filter)
    row = bytes([0] + list(bg_color) * width)
    image_data = row * height

    # Compress the image data (simple zlib compression)
    import zlib
    compressed_data = zlib.compress(image_data, 9)

    # Create IDAT chunk (image data)
    idat_chunk = create_chunk(b'IDAT', compressed_data)

    # Create IEND chunk (end of file)
    iend_chunk = create_chunk(b'IEND', b'')

    # Write PNG file
    with open(filename, 'wb') as f:
        f.write(png_signature)
        f.write(ihdr_chunk)
        f.write(idat_chunk)
        f.write(iend_chunk)


def create_chunk(chunk_type, data):
    """Create a PNG chunk with length, type, data, and CRC."""
    import zlib
    length = struct.pack('>I', len(data))
    crc = struct.pack('>I', zlib.crc32(chunk_type + data) & 0xffffffff)
    return length + chunk_type + data + crc


if __name__ == '__main__':
    import os

    assets_dir = '/home/user/muos-gba-save-converter/GBA_Fixer/assets'

    # Create icon.png (320x320) - dark blue-gray
    print('Creating icon.png (320x320)...')
    create_png(320, 320, os.path.join(assets_dir, 'icon.png'), bg_color=(52, 73, 94))

    # Create preview.png (640x480) - darker blue-gray
    print('Creating preview.png (640x480)...')
    create_png(640, 480, os.path.join(assets_dir, 'preview.png'), bg_color=(26, 37, 47))

    print('Placeholder images created successfully!')
