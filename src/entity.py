"""Entity module for game object representation.

This module provides the Entity class which represents renderable game objects
with grid positions and sprite assets.
"""


class Entity:
    """Represents a renderable game object.
    
    The Entity class encapsulates the data needed to render a game object in
    the isometric view. Each entity has a grid position (row, col), a sprite
    asset path, and a cached depth value used for depth sorting in the
    painter's algorithm.
    
    The depth value is automatically calculated as (row + col) and is used
    by the Y-Sorter to determine rendering order. Objects with lower depth
    values are further back in the isometric view and are drawn first.
    
    Attributes:
        row: Grid row position (non-negative integer)
        col: Grid column position (non-negative integer)
        sprite_path: Path to the PNG sprite asset
        depth: Cached depth value equal to (row + col)
    """
    
    def __init__(self, row: int, col: int, sprite_path: str):
        """Initialize an Entity with grid position and sprite.
        
        Creates a new entity at the specified grid position with the given
        sprite asset. The depth value is automatically calculated as (row + col)
        for use in depth sorting during rendering.
        
        Args:
            row: Grid row position (non-negative integer)
            col: Grid column position (non-negative integer)
            sprite_path: Path to the PNG sprite asset file
        """
        self.row: int = row
        self.col: int = col
        self.sprite_path: str = sprite_path
        self.depth: int = row + col
    
    def update_position(self, row: int, col: int) -> None:
        """Update entity position and recalculate depth.
        
        Updates the entity's grid position to the new coordinates and
        recalculates the depth value. This ensures the depth invariant
        (depth = row + col) is maintained after position changes.
        
        This method is used when entities move on the grid, ensuring that
        the depth sorting remains correct for the new position.
        
        Args:
            row: New grid row position (non-negative integer)
            col: New grid column position (non-negative integer)
        """
        self.row = row
        self.col = col
        self.depth = row + col
