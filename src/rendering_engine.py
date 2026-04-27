"""Rendering engine for isometric graphics.

This module provides the RenderingEngine class which orchestrates the complete
rendering pipeline for isometric graphics, including depth sorting, coordinate
transformation, asset loading, and sprite blitting with proper anchoring.
"""

from typing import List
try:
    import pygame
except ImportError:
    import pygame_ce as pygame

from src.entity import Entity
from src.resource_manager import ResourceManager
from src.camera import Camera
from src.y_sorter import YSorter
from src.isometric_converter import IsometricConverter


class RenderingEngine:
    """Core rendering system that draws isometric graphics.
    
    The RenderingEngine is the central component that orchestrates the complete
    rendering pipeline for isometric graphics. It manages a collection of entities,
    coordinates with other components (ResourceManager, Camera, Y-Sorter,
    IsometricConverter), and executes the rendering process each frame.
    
    The rendering pipeline follows these steps:
    1. Sort entities by depth using Y-Sorter (painter's algorithm)
    2. For each entity in back-to-front order:
       a. Get camera offset from Camera
       b. Calculate screen position via IsometricConverter or entity's render position
       c. Load sprite from ResourceManager or use entity's sprite
       d. Blit sprite to screen at calculated position
    
    This ensures correct visual layering where objects further back are drawn
    first and objects closer to the viewer are drawn on top.
    
    Attributes:
        screen: Pygame Surface representing the display
        resource_manager: ResourceManager for loading sprite assets
        camera: Camera for viewport offset management
        entities: List of Entity objects to render
    """
    
    def __init__(self, screen: pygame.Surface, resource_manager: ResourceManager, 
                 camera: Camera):
        """Initialize the RenderingEngine with required components.
        
        Creates a new rendering engine with references to the display surface,
        resource manager for asset loading, and camera for viewport offsets.
        The entity list is initialized as empty and entities must be added
        via add_entity() before rendering.
        
        Args:
            screen: Pygame Surface representing the display where graphics
                   will be drawn. This is typically created via
                   pygame.display.set_mode().
            resource_manager: ResourceManager instance for loading and caching
                            sprite assets. Must be initialized before passing
                            to the rendering engine.
            camera: Camera instance for managing viewport offsets. The camera's
                   offset values are applied during coordinate transformation
                   to enable map panning.
        """
        self.screen: pygame.Surface = screen
        self.resource_manager: ResourceManager = resource_manager
        self.camera: Camera = camera
        self.entities: List[Entity] = []
    
    def add_entity(self, entity: Entity) -> None:
        """Add an entity to the render list.
        
        Adds the specified entity to the internal list of entities that will
        be rendered during the next render() call. Entities can be added at
        any time and will be included in the next frame.
        
        The entity is not validated or processed during addition - validation
        and rendering occur during the render() method execution.
        
        Args:
            entity: Entity object to add to the render list. The entity must
                   have valid row, col, sprite_path, and depth attributes.
        """
        self.entities.append(entity)
    
    def add_entities(self, entities: List[Entity]) -> None:
        """Add multiple entities to the render list.
        
        Args:
            entities: List of Entity objects to add
        """
        self.entities.extend(entities)
    
    def clear_entities(self) -> None:
        """Clear all entities from the render list."""
        self.entities.clear()
    
    def render(self, zoom: float = 1.0) -> None:
        """Render all entities in depth-sorted order with optional zoom.

        The zoom factor scales both the isometric grid spacing AND each
        sprite's pixel dimensions, so the scene expands/contracts uniformly.
        Bottom-center anchoring is recalculated from the zoomed sprite size
        so entities never float above the floor at any zoom level.

        Args:
            zoom: Uniform scale multiplier (e.g. 1.0 = normal, 2.0 = 2× zoom).
                  Clamping to a safe range is the caller's responsibility.
        """
        # Step 1 — depth-sort (Y-sort / painter's algorithm — untouched)
        sorted_entities = YSorter.sort_by_depth(self.entities)

        # Step 2 — camera offset (panning — untouched)
        camera_x, camera_y = self.camera.get_offset()

        # Tile half-dimensions used for anchor math, scaled by zoom
        half_tile_w = IsometricConverter.TILE_WIDTH  * zoom / 2   # 64 * zoom
        half_tile_h = IsometricConverter.TILE_HEIGHT * zoom / 2   # 32 * zoom

        # Step 3 — draw each entity back-to-front
        for entity in sorted_entities:

            # --- Get the pre-loaded sprite --------------------------------
            sprite = (entity.sprite
                      if hasattr(entity, 'sprite')
                      else self.resource_manager.load_image(entity.sprite_path))

            # --- Scale the sprite by zoom (fast integer scale) -----------
            orig_w, orig_h = sprite.get_size()
            zoomed_w = max(1, int(orig_w * zoom))
            zoomed_h = max(1, int(orig_h * zoom))
            if zoom != 1.0:
                zoomed_sprite = pygame.transform.scale(sprite, (zoomed_w, zoomed_h))
            else:
                zoomed_sprite = sprite   # no copy needed at 1× zoom

            # --- Isometric grid position (math untouched) ----------------
            # Multiply the raw grid coords by zoom so tile spacing scales
            # with the images.  camera offset is added after.
            raw_x, raw_y = IsometricConverter.grid_to_screen(
                entity.row, entity.col, 0, 0
            )
            iso_x = int(raw_x * zoom) + camera_x
            iso_y = int(raw_y * zoom) + camera_y

            # --- Bottom-center anchor (recalculated from zoomed size) ----
            if hasattr(entity, 'is_floor_tile') and entity.is_floor_tile:
                # Floor tiles: top-left of sprite sits at the grid point
                blit_x = iso_x
                blit_y = iso_y
            else:
                # Entities: anchor bottom-center of zoomed sprite to grid point
                # blit_x centres the sprite horizontally over the tile diamond
                blit_x = iso_x + int(half_tile_w) - zoomed_w // 2
                # blit_y places the bottom of the sprite at the tile surface
                blit_y = iso_y - zoomed_h + int(half_tile_h * 2)

            # --- Blit -------------------------------------------------------
            self.screen.blit(zoomed_sprite, (blit_x, blit_y))
