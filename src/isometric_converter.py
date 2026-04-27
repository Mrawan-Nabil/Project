"""
Isometric coordinate transformation module.

This module provides conversion between 2D grid coordinates and isometric screen coordinates.
"""

from typing import Tuple, Optional


class IsometricConverter:
    """Converts 2D grid coordinates to isometric screen coordinates.
    
    The isometric projection creates a diamond-shaped visual grid from a logical
    rectangular grid. This class handles the mathematical transformation between
    these two coordinate systems.
    
    Tile dimensions are now dynamic and set at runtime based on the actual
    floor tile assets loaded by the ResourceManager.
    """
    
    # Dynamic tile dimensions (set by ResourceManager after loading floor tiles)
    # These start with default values but will be updated at runtime
    TILE_WIDTH = 128
    TILE_HEIGHT = 64
    
    @classmethod
    def set_tile_dimensions(cls, width: int, height: int) -> None:
        """Set the tile dimensions dynamically based on loaded assets.
        
        This should be called by ResourceManager after loading the first floor tile
        to ensure all isometric calculations use the correct dimensions.
        
        Args:
            width: The width of floor tiles in pixels
            height: The height of floor tiles in pixels
        """
        cls.TILE_WIDTH = width
        cls.TILE_HEIGHT = height
        print(f"IsometricConverter: Tile dimensions set to {width}x{height}")
    
    @staticmethod
    def grid_to_screen(row: int, col: int, camera_x: int = 0, camera_y: int = 0) -> Tuple[int, int]:
        """
        Transform grid coordinates to screen coordinates with camera offset.
        
        Isometric projection formula:
        - x = (col - row) * (TILE_WIDTH / 2) + camera_x
        - y = (col + row) * (TILE_HEIGHT / 2) + camera_y
        
        Mathematical explanation:
        The isometric projection maps a 2D grid onto a rotated diamond grid.
        - (col - row) creates the horizontal axis: moving right in the grid (col+1) 
          shifts right on screen, while moving down (row+1) shifts left on screen
        - (col + row) creates the depth axis: both col and row increases move down on screen
        - Multiplying by half the tile dimensions (TILE_WIDTH/2, TILE_HEIGHT/2) scales 
          the unit grid to pixel space, with the halving accounting for the diamond shape
          where each grid step moves half a tile width/height
        - Camera offsets are added to enable viewport panning
        
        Args:
            row: Grid row position (increases downward in logical grid)
            col: Grid column position (increases rightward in logical grid)
            camera_x: Camera horizontal offset in pixels (default: 0)
            camera_y: Camera vertical offset in pixels (default: 0)
            
        Returns:
            Tuple of (screen_x, screen_y) in pixels representing the isometric position
        """
        # Calculate base isometric coordinates using the projection formula
        # The (col - row) term creates the horizontal diamond axis
        x = (col - row) * (IsometricConverter.TILE_WIDTH / 2)
        
        # The (col + row) term creates the vertical depth axis
        y = (col + row) * (IsometricConverter.TILE_HEIGHT / 2)
        
        # Apply camera offsets to enable viewport panning
        x += camera_x
        y += camera_y
        
        # Return as integer pixel coordinates
        return (int(x), int(y))
