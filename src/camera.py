"""Camera module for viewport offset management.

This module provides the Camera class which manages viewport offsets
for map panning functionality.
"""

from typing import Tuple


class Camera:
    """Manages viewport offset for map panning.
    
    The Camera class maintains x and y offset values that are applied to
    all rendered objects, enabling viewport panning functionality. In the
    current implementation, the camera serves as a simple data holder for
    offset values that are used by the IsometricConverter during coordinate
    transformation.
    
    Future enhancements may include:
    - Smooth scrolling interpolation
    - Bounds checking to prevent panning outside the map
    - Follow target functionality to track entities
    - Zoom level management
    """
    
    def __init__(self):
        """Initialize the Camera with zero offsets.
        
        The camera starts at position (0, 0), meaning no offset is applied
        to rendered objects. This represents the default viewport position.
        """
        self.camera_x: int = 0
        self.camera_y: int = 0
    
    def set_offset(self, x: int, y: int) -> None:
        """Set camera offset values.
        
        Updates both the horizontal and vertical camera offsets. These offsets
        are added to all screen coordinates during rendering, effectively moving
        the viewport. Positive x values shift the view right, positive y values
        shift the view down.
        
        Args:
            x: Horizontal camera offset in pixels
            y: Vertical camera offset in pixels
        """
        self.camera_x = x
        self.camera_y = y
    
    def get_offset(self) -> Tuple[int, int]:
        """Get current camera offset.
        
        Returns the current camera offset values as a tuple. This is used
        by the rendering system to apply offsets during coordinate transformation.
        
        Returns:
            Tuple of (camera_x, camera_y) representing the current viewport offset
        """
        return (self.camera_x, self.camera_y)
