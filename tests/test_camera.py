"""Unit tests for Camera."""

import pytest
from src.camera import Camera


class TestCameraUnit:
    """Example-based unit tests for Camera."""
    
    def test_initial_state_is_zero(self):
        """Test that camera initializes with (0, 0) offset."""
        camera = Camera()
        assert camera.camera_x == 0, f"Expected camera_x=0, got {camera.camera_x}"
        assert camera.camera_y == 0, f"Expected camera_y=0, got {camera.camera_y}"
    
    def test_get_offset_returns_initial_zero(self):
        """Test that get_offset returns (0, 0) for new camera."""
        camera = Camera()
        offset = camera.get_offset()
        assert offset == (0, 0), f"Expected (0, 0), got {offset}"
    
    def test_set_offset_updates_x(self):
        """Test that set_offset updates camera_x."""
        camera = Camera()
        camera.set_offset(100, 0)
        assert camera.camera_x == 100, f"Expected camera_x=100, got {camera.camera_x}"
    
    def test_set_offset_updates_y(self):
        """Test that set_offset updates camera_y."""
        camera = Camera()
        camera.set_offset(0, 50)
        assert camera.camera_y == 50, f"Expected camera_y=50, got {camera.camera_y}"
    
    def test_set_offset_updates_both_axes(self):
        """Test that set_offset updates both x and y."""
        camera = Camera()
        camera.set_offset(200, 150)
        assert camera.camera_x == 200, f"Expected camera_x=200, got {camera.camera_x}"
        assert camera.camera_y == 150, f"Expected camera_y=150, got {camera.camera_y}"
    
    def test_get_offset_returns_set_values(self):
        """Test that get_offset returns values set by set_offset."""
        camera = Camera()
        camera.set_offset(300, 250)
        offset = camera.get_offset()
        assert offset == (300, 250), f"Expected (300, 250), got {offset}"
    
    def test_set_offset_overwrites_previous_values(self):
        """Test that set_offset overwrites previous offset values."""
        camera = Camera()
        camera.set_offset(100, 100)
        camera.set_offset(200, 300)
        offset = camera.get_offset()
        assert offset == (200, 300), f"Expected (200, 300), got {offset}"
    
    def test_set_offset_with_negative_values(self):
        """Test that set_offset works with negative values."""
        camera = Camera()
        camera.set_offset(-50, -75)
        assert camera.camera_x == -50, f"Expected camera_x=-50, got {camera.camera_x}"
        assert camera.camera_y == -75, f"Expected camera_y=-75, got {camera.camera_y}"
    
    def test_get_offset_returns_tuple(self):
        """Test that get_offset returns a tuple."""
        camera = Camera()
        camera.set_offset(10, 20)
        offset = camera.get_offset()
        assert isinstance(offset, tuple), f"Expected tuple, got {type(offset)}"
        assert len(offset) == 2, f"Expected tuple of length 2, got {len(offset)}"
    
    def test_offset_round_trip(self):
        """Test that setting and getting offset preserves values (round-trip)."""
        camera = Camera()
        test_values = [(0, 0), (100, 200), (-50, 75), (1000, -500)]
        
        for x, y in test_values:
            camera.set_offset(x, y)
            offset = camera.get_offset()
            assert offset == (x, y), f"Round-trip failed for ({x}, {y}), got {offset}"
