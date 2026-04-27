"""Y-Sorter module for depth-based entity sorting.

This module provides the YSorter class which implements the painter's algorithm
for isometric rendering. The painter's algorithm ensures correct visual layering
by drawing objects from back to front based on their depth in the scene.
"""

from typing import List
from src.entity import Entity


class YSorter:
    """Handles depth sorting for painter's algorithm rendering.
    
    The YSorter class provides depth-based sorting functionality for entities
    in an isometric rendering system. It implements the painter's algorithm,
    which ensures correct visual layering by rendering objects in back-to-front
    order based on their position in the isometric grid.
    
    Depth Calculation:
    ------------------
    In an isometric view, an object's depth is determined by its position on
    the 2D grid. The depth value is calculated as (row + col):
    
    - Objects at (0, 0) have depth 0 (furthest back, top of diamond)
    - Objects at (1, 0) or (0, 1) have depth 1
    - Objects at (2, 2) have depth 4
    - Higher depth values indicate objects closer to the viewer
    
    This formula works because in isometric projection:
    - Moving right (col+1) moves the object toward the viewer
    - Moving down (row+1) also moves the object toward the viewer
    - Therefore, the sum (row + col) represents the object's distance from
      the origin along the diagonal axis of the isometric view
    
    Back-to-Front Rendering Rationale:
    ----------------------------------
    The painter's algorithm draws objects in ascending depth order (low to high):
    
    1. Objects with lower depth values are further back in the scene
    2. These are drawn first, establishing the background
    3. Objects with higher depth values are closer to the viewer
    4. These are drawn later, overlapping the background objects
    5. This creates the correct visual layering without complex occlusion logic
    
    For example, in a 3x3 grid:
    - (0,0) depth=0 drawn first  (back)
    - (1,0) depth=1 drawn second
    - (0,1) depth=1 drawn third
    - (1,1) depth=2 drawn fourth
    - (2,2) depth=4 drawn last   (front)
    
    Stable Sorting:
    ---------------
    Python's sorted() function provides stable sorting, meaning that when two
    entities have equal depth values, their relative order from the input list
    is preserved. This ensures deterministic rendering behavior and prevents
    visual flickering when entities occupy the same depth layer.
    """
    
    @staticmethod
    def sort_by_depth(entities: List[Entity]) -> List[Entity]:
        """Sort entities by depth value in ascending order for back-to-front rendering.
        
        This method implements the core sorting operation for the painter's
        algorithm. It takes a list of entities and returns a new list sorted
        by depth value (row + col) in ascending order. The sorted list can be
        directly used for rendering, with each entity drawn in sequence to
        achieve correct visual layering.
        
        The sorting is stable, meaning entities with equal depth values maintain
        their relative order from the input list. This prevents non-deterministic
        rendering behavior when multiple entities occupy the same grid diagonal.
        
        Args:
            entities: List of Entity objects to sort. Each entity must have a
                     valid depth attribute (typically calculated as row + col).
                     The input list is not modified.
        
        Returns:
            A new list containing the same Entity objects sorted in ascending
            depth order (back-to-front). Objects with lower depth values appear
            first in the list and should be drawn first during rendering.
        
        Example:
            >>> entity_a = Entity(0, 0, "sprite.png")  # depth = 0
            >>> entity_b = Entity(1, 1, "sprite.png")  # depth = 2
            >>> entity_c = Entity(0, 1, "sprite.png")  # depth = 1
            >>> entities = [entity_b, entity_a, entity_c]
            >>> sorted_entities = YSorter.sort_by_depth(entities)
            >>> [e.depth for e in sorted_entities]
            [0, 1, 2]
        
        Note:
            The depth value is expected to be pre-calculated and stored in each
            Entity object. This method does not recalculate depth values; it
            simply sorts based on the existing depth attribute.
        """
        # Use Python's sorted() with a lambda key function to sort by depth.
        # sorted() provides stable sorting (O(n log n) time complexity) which
        # preserves the relative order of entities with equal depth values.
        # The lambda extracts the depth attribute from each entity for comparison.
        return sorted(entities, key=lambda e: e.depth)
