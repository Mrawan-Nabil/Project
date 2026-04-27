# Assets Directory

This directory contains image assets for the isometric rendering engine.

## Required Assets

### floor_tile.png
- **Dimensions**: 128x64 pixels
- **Format**: PNG with transparency (alpha channel)
- **Purpose**: Isometric floor tile sprite
- **Placement**: Place your floor tile sprite here as `floor_tile.png`

### entity.png
- **Dimensions**: Recommended 128x128 pixels (or appropriate for your entity)
- **Format**: PNG with transparency (alpha channel)
- **Purpose**: Entity/character sprite
- **Placement**: Place your entity sprite here as `entity.png`

## Creating Placeholder Assets

If you don't have assets yet, you can create simple placeholder images:

1. Use any image editor (GIMP, Photoshop, Paint.NET, etc.)
2. Create a 128x64 PNG for the floor tile with a simple pattern
3. Create a 128x128 PNG for the entity with a simple shape
4. Ensure both have transparency enabled (alpha channel)

## Notes

- The rendering engine will look for these files at the paths specified in `src/settings.py`
- If assets are missing, the ResourceManager will raise an error with the file path
- Future versions may include fallback to colored rectangles for missing assets
