"""Map parsing and entity instantiation for the hospital layout.

This module handles parsing the map blueprints and creating entities
with proper isometric positioning and sprite anchoring.
"""

from typing import List, Tuple, Optional
try:
    import pygame
except ImportError:
    import pygame_ce as pygame

from src.entity import Entity
from src.resource_manager import ResourceManager
from src.isometric_converter import IsometricConverter
from src.map_data import FLOOR_MAP, ENTITY_MAP, MAP_LEGEND, validate_maps


class AnchoredEntity(Entity):
    """Extended Entity class with sprite anchoring support.
    
    This class extends the base Entity to support proper sprite anchoring
    for tall objects in isometric view. Tall sprites (walls, equipment, characters)
    need to be anchored by their bottom-center to the grid point.
    """
    
    def __init__(self, row: int, col: int, asset_key: str, sprite: pygame.Surface, 
                 is_floor_tile: bool = False):
        """Initialize an anchored entity.
        
        Args:
            row: Grid row position
            col: Grid column position  
            asset_key: Key identifying the asset
            sprite: The pygame Surface for this entity
            is_floor_tile: True if this is a floor tile (no anchoring needed)
        """
        # Use asset_key as sprite_path for compatibility
        super().__init__(row, col, asset_key)
        self.asset_key = asset_key
        self.sprite = sprite
        self.is_floor_tile = is_floor_tile
        
        # Calculate anchor offset for tall sprites
        self.anchor_offset_x = 0
        self.anchor_offset_y = 0
        
        if not is_floor_tile:
            # For non-floor entities, anchor by bottom-center
            sprite_width = sprite.get_width()
            sprite_height = sprite.get_height()
            
            # Horizontal centering: offset by half width minus half tile width
            self.anchor_offset_x = -(sprite_width // 2) + (IsometricConverter.TILE_WIDTH // 2)
            
            # Vertical anchoring: offset by sprite height minus tile height
            # This makes the bottom of the sprite align with the tile
            self.anchor_offset_y = -(sprite_height - IsometricConverter.TILE_HEIGHT)
    
    def get_render_position(self, camera_x: int = 0, camera_y: int = 0) -> Tuple[int, int]:
        """Get the final render position with anchoring applied.
        
        Args:
            camera_x: Camera horizontal offset
            camera_y: Camera vertical offset
            
        Returns:
            Tuple of (x, y) screen coordinates for rendering
        """
        # Get base isometric position
        base_x, base_y = IsometricConverter.grid_to_screen(
            self.row, self.col, camera_x, camera_y
        )
        
        # Apply anchor offset
        final_x = base_x + self.anchor_offset_x
        final_y = base_y + self.anchor_offset_y
        
        return (final_x, final_y)


class MapParser:
    """Parses hospital map blueprints and creates entities."""
    
    def __init__(self, resource_manager: ResourceManager):
        """Initialize the map parser.
        
        Args:
            resource_manager: ResourceManager with loaded assets
        """
        self.resource_manager = resource_manager
        validate_maps()  # Ensure maps are valid
    
    def parse_maps(self) -> List[AnchoredEntity]:
        """Parse the floor and entity maps to create a list of entities.
        
        Returns:
            List of AnchoredEntity objects ready for rendering
            
        Raises:
            KeyError: If a symbol in the map doesn't exist in MAP_LEGEND
            KeyError: If an asset key doesn't exist in ResourceManager
        """
        entities = []
        rows, cols = len(FLOOR_MAP), len(FLOOR_MAP[0])
        
        print(f"Parsing {rows}x{cols} hospital map...")
        
        # First pass: Create floor tiles
        for row in range(rows):
            for col in range(cols):
                floor_symbol = FLOOR_MAP[row][col]
                
                if floor_symbol in MAP_LEGEND:
                    asset_key = MAP_LEGEND[floor_symbol]
                    
                    if asset_key is not None:
                        # Verify asset exists
                        if not self.resource_manager.has_asset(asset_key):
                            raise KeyError(f"Floor asset '{asset_key}' not found in ResourceManager")
                        
                        sprite = self.resource_manager.get_asset(asset_key)
                        entity = AnchoredEntity(row, col, asset_key, sprite, is_floor_tile=True)
                        entities.append(entity)
                else:
                    raise KeyError(f"Floor symbol '{floor_symbol}' not found in MAP_LEGEND")
        
        # Second pass: Create entities (walls, equipment, characters)
        for row in range(rows):
            for col in range(cols):
                entity_symbol = ENTITY_MAP[row][col]
                
                if entity_symbol in (0, ' '):
                    # Empty cell — nothing to place
                    continue
                
                if entity_symbol in MAP_LEGEND:
                    asset_key = MAP_LEGEND[entity_symbol]
                    
                    if asset_key is not None:
                        # Verify asset exists
                        if not self.resource_manager.has_asset(asset_key):
                            raise KeyError(f"Entity asset '{asset_key}' not found in ResourceManager")
                        
                        sprite = self.resource_manager.get_asset(asset_key)
                        entity = AnchoredEntity(row, col, asset_key, sprite, is_floor_tile=False)
                        entities.append(entity)
                else:
                    raise KeyError(f"Entity symbol '{entity_symbol}' not found in MAP_LEGEND")
        
        print(f"Created {len(entities)} entities from map")
        return entities
    
    def get_missing_assets(self) -> List[str]:
        """Get list of asset keys referenced in maps but not loaded.
        
        Returns:
            List of missing asset keys
        """
        missing = []
        
        # Check all symbols in both maps
        all_symbols = set()
        
        for row in FLOOR_MAP:
            all_symbols.update(row)
        
        for row in ENTITY_MAP:
            all_symbols.update(row)
        
        # Remove empty-cell markers
        all_symbols.discard(' ')
        all_symbols.discard(0)
        
        # Check each symbol
        for symbol in all_symbols:
            if symbol in MAP_LEGEND:
                asset_key = MAP_LEGEND[symbol]
                if asset_key is not None and not self.resource_manager.has_asset(asset_key):
                    missing.append(asset_key)
        
        return missing
    
    def validate_map_assets(self) -> bool:
        """Validate that all required assets are loaded.
        
        Returns:
            True if all assets are available, False otherwise
        """
        missing = self.get_missing_assets()
        
        if missing:
            print(f"Missing assets: {missing}")
            return False
        
        return True


def create_hospital_entities(resource_manager: ResourceManager) -> List[AnchoredEntity]:
    """Convenience function to create all hospital entities from maps.
    
    Args:
        resource_manager: ResourceManager with loaded assets
        
    Returns:
        List of AnchoredEntity objects ready for rendering
    """
    parser = MapParser(resource_manager)
    
    if not parser.validate_map_assets():
        missing = parser.get_missing_assets()
        raise RuntimeError(f"Cannot create hospital entities. Missing assets: {missing}")
    
    return parser.parse_maps()