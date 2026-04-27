"""Unit tests for IsometricConverter."""

import pytest
from src.isometric_converter import IsometricConverter


class TestIsometricConverterUnit:
    """Example-based unit tests for IsometricConverter."""
    
    def test_tile_width_constant(self):
        """Test that TILE_WIDTH = 128."""
        assert IsometricConverter.TILE_WIDTH == 128
    
    def test_tile_height_constant(self):
        """Test that TILE_HEIGHT = 64."""
        assert IsometricConverter.TILE_HEIGHT == 64
    
    def test_origin_point_maps_to_origin(self):
        """Test origin point (0, 0) maps to (0, 0)."""
        x, y = IsometricConverter.grid_to_screen(0, 0)
        assert x == 0, f"Expected x=0 for origin, got {x}"
        assert y == 0, f"Expected y=0 for origin, got {y}"
    
    def test_coordinate_1_0_maps_correctly(self):
        """Test specific known coordinate: (1, 0) → (64, 32).
        
        Formula: x = (col - row) * 64, y = (col + row) * 32
        For (row=1, col=0): x = (0 - 1) * 64 = -64, y = (0 + 1) * 32 = 32
        """
        x, y = IsometricConverter.grid_to_screen(1, 0)
        assert x == -64, f"Expected x=-64 for (1, 0), got {x}"
        assert y == 32, f"Expected y=32 for (1, 0), got {y}"
    
    def test_coordinate_0_1_maps_correctly(self):
        """Test specific known coordinate: (0, 1) → (64, 32).
        
        Formula: x = (col - row) * 64, y = (col + row) * 32
        For (row=0, col=1): x = (1 - 0) * 64 = 64, y = (1 + 0) * 32 = 32
        """
        x, y = IsometricConverter.grid_to_screen(0, 1)
        assert x == 64, f"Expected x=64 for (0, 1), got {x}"
        assert y == 32, f"Expected y=32 for (0, 1), got {y}"
    
    def test_coordinate_2_2_maps_correctly(self):
        """Test specific known coordinate: (2, 2) → (0, 128).
        
        Formula: x = (col - row) * 64, y = (col + row) * 32
        For (row=2, col=2): x = (2 - 2) * 64 = 0, y = (2 + 2) * 32 = 128
        """
        x, y = IsometricConverter.grid_to_screen(2, 2)
        assert x == 0, f"Expected x=0 for (2, 2), got {x}"
        assert y == 128, f"Expected y=128 for (2, 2), got {y}"
    
    def test_camera_offset_applied_to_x(self):
        """Test that camera_x offset is added to the calculated x coordinate."""
        # Without camera offset
        x_no_offset, _ = IsometricConverter.grid_to_screen(1, 1, camera_x=0)
        
        # With camera offset
        camera_x = 100
        x_with_offset, _ = IsometricConverter.grid_to_screen(1, 1, camera_x=camera_x)
        
        assert x_with_offset == x_no_offset + camera_x, \
            f"Expected x to increase by {camera_x}, got {x_with_offset - x_no_offset}"
    
    def test_camera_offset_applied_to_y(self):
        """Test that camera_y offset is added to the calculated y coordinate."""
        # Without camera offset
        _, y_no_offset = IsometricConverter.grid_to_screen(1, 1, camera_y=0)
        
        # With camera offset
        camera_y = 50
        _, y_with_offset = IsometricConverter.grid_to_screen(1, 1, camera_y=camera_y)
        
        assert y_with_offset == y_no_offset + camera_y, \
            f"Expected y to increase by {camera_y}, got {y_with_offset - y_no_offset}"
    
    def test_camera_offset_both_axes(self):
        """Test that both camera offsets are applied simultaneously."""
        camera_x = 200
        camera_y = 150
        
        # Calculate expected values
        # For (row=1, col=2): x = (2-1)*64 = 64, y = (2+1)*32 = 96
        expected_x = 64 + camera_x
        expected_y = 96 + camera_y
        
        x, y = IsometricConverter.grid_to_screen(1, 2, camera_x=camera_x, camera_y=camera_y)
        
        assert x == expected_x, f"Expected x={expected_x}, got {x}"
        assert y == expected_y, f"Expected y={expected_y}, got {y}"
    
    def test_negative_grid_coordinates(self):
        """Test that negative grid coordinates work correctly.
        
        Formula: x = (col - row) * 64, y = (col + row) * 32
        For (row=-1, col=-1): x = (-1 - (-1)) * 64 = 0, y = (-1 + (-1)) * 32 = -64
        """
        x, y = IsometricConverter.grid_to_screen(-1, -1)
        assert x == 0, f"Expected x=0 for (-1, -1), got {x}"
        assert y == -64, f"Expected y=-64 for (-1, -1), got {y}"
    
    def test_returns_integer_coordinates(self):
        """Test that returned coordinates are integers."""
        x, y = IsometricConverter.grid_to_screen(1, 1)
        assert isinstance(x, int), f"Expected x to be int, got {type(x)}"
        assert isinstance(y, int), f"Expected y to be int, got {type(y)}"
    
    def test_large_grid_coordinates(self):
        """Test that large grid coordinates are handled correctly.
        
        Formula: x = (col - row) * 64, y = (col + row) * 32
        For (row=100, col=100): x = (100 - 100) * 64 = 0, y = (100 + 100) * 32 = 6400
        """
        x, y = IsometricConverter.grid_to_screen(100, 100)
        assert x == 0, f"Expected x=0 for (100, 100), got {x}"
        assert y == 6400, f"Expected y=6400 for (100, 100), got {y}"
