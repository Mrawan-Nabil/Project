"""Unit tests for RenderingEngine."""

import pytest
from unittest.mock import Mock, MagicMock, call
try:
    import pygame
except ImportError:
    import pygame_ce as pygame

from src.rendering_engine import RenderingEngine
from src.resource_manager import ResourceManager
from src.camera import Camera
from src.entity import Entity


class TestRenderingEngineUnit:
    """Example-based unit tests for RenderingEngine."""
    
    def test_initialization_creates_empty_entity_list(self):
        """Test that RenderingEngine initializes with empty entity list."""
        screen = Mock(spec=pygame.Surface)
        resource_manager = Mock(spec=ResourceManager)
        camera = Mock(spec=Camera)
        
        engine = RenderingEngine(screen, resource_manager, camera)
        
        assert engine.entities == [], f"Expected empty list, got {engine.entities}"
        assert len(engine.entities) == 0, f"Expected 0 entities, got {len(engine.entities)}"
    
    def test_initialization_stores_screen_reference(self):
        """Test that RenderingEngine stores screen reference."""
        screen = Mock(spec=pygame.Surface)
        resource_manager = Mock(spec=ResourceManager)
        camera = Mock(spec=Camera)
        
        engine = RenderingEngine(screen, resource_manager, camera)
        
        assert engine.screen is screen, "Screen reference not stored correctly"
    
    def test_initialization_stores_resource_manager_reference(self):
        """Test that RenderingEngine stores resource_manager reference."""
        screen = Mock(spec=pygame.Surface)
        resource_manager = Mock(spec=ResourceManager)
        camera = Mock(spec=Camera)
        
        engine = RenderingEngine(screen, resource_manager, camera)
        
        assert engine.resource_manager is resource_manager, "ResourceManager reference not stored correctly"
    
    def test_initialization_stores_camera_reference(self):
        """Test that RenderingEngine stores camera reference."""
        screen = Mock(spec=pygame.Surface)
        resource_manager = Mock(spec=ResourceManager)
        camera = Mock(spec=Camera)
        
        engine = RenderingEngine(screen, resource_manager, camera)
        
        assert engine.camera is camera, "Camera reference not stored correctly"
    
    def test_add_entity_increases_entity_count(self):
        """Test that add_entity increases the entity count."""
        screen = Mock(spec=pygame.Surface)
        resource_manager = Mock(spec=ResourceManager)
        camera = Mock(spec=Camera)
        engine = RenderingEngine(screen, resource_manager, camera)
        
        entity = Entity(0, 0, "test.png")
        engine.add_entity(entity)
        
        assert len(engine.entities) == 1, f"Expected 1 entity, got {len(engine.entities)}"
    
    def test_add_entity_stores_entity_reference(self):
        """Test that add_entity stores the entity reference."""
        screen = Mock(spec=pygame.Surface)
        resource_manager = Mock(spec=ResourceManager)
        camera = Mock(spec=Camera)
        engine = RenderingEngine(screen, resource_manager, camera)
        
        entity = Entity(1, 2, "test.png")
        engine.add_entity(entity)
        
        assert entity in engine.entities, "Entity not found in entities list"
        assert engine.entities[0] is entity, "Entity reference not stored correctly"
    
    def test_add_multiple_entities(self):
        """Test that multiple entities can be added."""
        screen = Mock(spec=pygame.Surface)
        resource_manager = Mock(spec=ResourceManager)
        camera = Mock(spec=Camera)
        engine = RenderingEngine(screen, resource_manager, camera)
        
        entity1 = Entity(0, 0, "test1.png")
        entity2 = Entity(1, 1, "test2.png")
        entity3 = Entity(2, 2, "test3.png")
        
        engine.add_entity(entity1)
        engine.add_entity(entity2)
        engine.add_entity(entity3)
        
        assert len(engine.entities) == 3, f"Expected 3 entities, got {len(engine.entities)}"
        assert engine.entities[0] is entity1, "First entity not stored correctly"
        assert engine.entities[1] is entity2, "Second entity not stored correctly"
        assert engine.entities[2] is entity3, "Third entity not stored correctly"
    
    def test_render_with_no_entities(self):
        """Test that render completes successfully with no entities."""
        screen = Mock(spec=pygame.Surface)
        resource_manager = Mock(spec=ResourceManager)
        camera = Mock(spec=Camera)
        camera.get_offset.return_value = (0, 0)
        
        engine = RenderingEngine(screen, resource_manager, camera)
        
        # Should not raise any exceptions
        engine.render()
        
        # Verify camera was queried
        camera.get_offset.assert_called_once()
        
        # Verify no resources were loaded
        resource_manager.load_image.assert_not_called()
        
        # Verify no blits occurred
        screen.blit.assert_not_called()
    
    def test_render_calls_camera_get_offset(self):
        """Test that render calls camera.get_offset()."""
        screen = Mock(spec=pygame.Surface)
        resource_manager = Mock(spec=ResourceManager)
        camera = Mock(spec=Camera)
        camera.get_offset.return_value = (100, 50)
        
        engine = RenderingEngine(screen, resource_manager, camera)
        entity = Entity(0, 0, "test.png")
        engine.add_entity(entity)
        
        # Mock the sprite
        mock_sprite = Mock(spec=pygame.Surface)
        resource_manager.load_image.return_value = mock_sprite
        
        engine.render()
        
        camera.get_offset.assert_called_once()
    
    def test_render_loads_sprite_for_each_entity(self):
        """Test that render calls resource_manager.load_image for each entity."""
        screen = Mock(spec=pygame.Surface)
        resource_manager = Mock(spec=ResourceManager)
        camera = Mock(spec=Camera)
        camera.get_offset.return_value = (0, 0)
        
        engine = RenderingEngine(screen, resource_manager, camera)
        
        entity1 = Entity(0, 0, "sprite1.png")
        entity2 = Entity(1, 1, "sprite2.png")
        engine.add_entity(entity1)
        engine.add_entity(entity2)
        
        # Mock the sprites
        mock_sprite1 = Mock(spec=pygame.Surface)
        mock_sprite2 = Mock(spec=pygame.Surface)
        resource_manager.load_image.side_effect = [mock_sprite1, mock_sprite2]
        
        engine.render()
        
        # Verify load_image was called for each entity
        assert resource_manager.load_image.call_count == 2
        resource_manager.load_image.assert_any_call("sprite1.png")
        resource_manager.load_image.assert_any_call("sprite2.png")
    
    def test_render_blits_sprite_for_each_entity(self):
        """Test that render calls screen.blit for each entity."""
        screen = Mock(spec=pygame.Surface)
        resource_manager = Mock(spec=ResourceManager)
        camera = Mock(spec=Camera)
        camera.get_offset.return_value = (0, 0)
        
        engine = RenderingEngine(screen, resource_manager, camera)
        
        entity = Entity(0, 0, "test.png")
        engine.add_entity(entity)
        
        # Mock the sprite
        mock_sprite = Mock(spec=pygame.Surface)
        resource_manager.load_image.return_value = mock_sprite
        
        engine.render()
        
        # Verify blit was called
        screen.blit.assert_called_once()
        # Verify the sprite was passed to blit
        call_args = screen.blit.call_args
        assert call_args[0][0] is mock_sprite, "Sprite not passed to blit"
    
    def test_render_applies_isometric_transformation(self):
        """Test that render applies isometric coordinate transformation."""
        screen = Mock(spec=pygame.Surface)
        resource_manager = Mock(spec=ResourceManager)
        camera = Mock(spec=Camera)
        camera.get_offset.return_value = (0, 0)
        
        engine = RenderingEngine(screen, resource_manager, camera)
        
        # Entity at (1, 0) should map to screen coordinates
        # x = (0 - 1) * 64 = -64
        # y = (0 + 1) * 32 = 32
        entity = Entity(1, 0, "test.png")
        engine.add_entity(entity)
        
        # Mock the sprite
        mock_sprite = Mock(spec=pygame.Surface)
        resource_manager.load_image.return_value = mock_sprite
        
        engine.render()
        
        # Verify blit was called with correct screen coordinates
        call_args = screen.blit.call_args
        screen_pos = call_args[0][1]
        assert screen_pos == (-64, 32), f"Expected (-64, 32), got {screen_pos}"
    
    def test_render_applies_camera_offset(self):
        """Test that render applies camera offset to screen coordinates."""
        screen = Mock(spec=pygame.Surface)
        resource_manager = Mock(spec=ResourceManager)
        camera = Mock(spec=Camera)
        camera.get_offset.return_value = (100, 50)
        
        engine = RenderingEngine(screen, resource_manager, camera)
        
        # Entity at (0, 0) with camera offset (100, 50)
        # Base: x = 0, y = 0
        # With offset: x = 100, y = 50
        entity = Entity(0, 0, "test.png")
        engine.add_entity(entity)
        
        # Mock the sprite
        mock_sprite = Mock(spec=pygame.Surface)
        resource_manager.load_image.return_value = mock_sprite
        
        engine.render()
        
        # Verify blit was called with camera offset applied
        call_args = screen.blit.call_args
        screen_pos = call_args[0][1]
        assert screen_pos == (100, 50), f"Expected (100, 50), got {screen_pos}"
    
    def test_render_sorts_entities_by_depth(self):
        """Test that render draws entities in depth-sorted order."""
        screen = Mock(spec=pygame.Surface)
        resource_manager = Mock(spec=ResourceManager)
        camera = Mock(spec=Camera)
        camera.get_offset.return_value = (0, 0)
        
        engine = RenderingEngine(screen, resource_manager, camera)
        
        # Add entities in non-sorted order
        entity_high_depth = Entity(2, 2, "high.png")  # depth = 4
        entity_low_depth = Entity(0, 0, "low.png")    # depth = 0
        entity_mid_depth = Entity(1, 0, "mid.png")    # depth = 1
        
        engine.add_entity(entity_high_depth)
        engine.add_entity(entity_low_depth)
        engine.add_entity(entity_mid_depth)
        
        # Mock the sprites
        mock_sprite = Mock(spec=pygame.Surface)
        resource_manager.load_image.return_value = mock_sprite
        
        engine.render()
        
        # Verify load_image was called in depth order (low to high)
        calls = resource_manager.load_image.call_args_list
        assert len(calls) == 3
        assert calls[0][0][0] == "low.png", f"Expected low.png first, got {calls[0][0][0]}"
        assert calls[1][0][0] == "mid.png", f"Expected mid.png second, got {calls[1][0][0]}"
        assert calls[2][0][0] == "high.png", f"Expected high.png third, got {calls[2][0][0]}"
    
    def test_render_with_equal_depth_entities(self):
        """Test that render maintains stable order for equal depth entities."""
        screen = Mock(spec=pygame.Surface)
        resource_manager = Mock(spec=ResourceManager)
        camera = Mock(spec=Camera)
        camera.get_offset.return_value = (0, 0)
        
        engine = RenderingEngine(screen, resource_manager, camera)
        
        # Add entities with equal depth in specific order
        entity1 = Entity(0, 1, "first.png")   # depth = 1
        entity2 = Entity(1, 0, "second.png")  # depth = 1
        
        engine.add_entity(entity1)
        engine.add_entity(entity2)
        
        # Mock the sprites
        mock_sprite = Mock(spec=pygame.Surface)
        resource_manager.load_image.return_value = mock_sprite
        
        engine.render()
        
        # Verify load_image was called in original order (stable sort)
        calls = resource_manager.load_image.call_args_list
        assert len(calls) == 2
        assert calls[0][0][0] == "first.png", f"Expected first.png first, got {calls[0][0][0]}"
        assert calls[1][0][0] == "second.png", f"Expected second.png second, got {calls[1][0][0]}"
