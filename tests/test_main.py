"""Unit tests for the main module."""

import pytest
try:
    import pygame
except ImportError:
    import pygame_ce as pygame
from unittest.mock import Mock, patch, MagicMock

from src.main import main
from src.rendering_engine import RenderingEngine


def setup_mock_pygame(mock_pygame):
    """Helper to setup common pygame mocks."""
    mock_pygame.init.return_value = (5, 0)
    mock_pygame.QUIT = 256
    mock_pygame.error = Exception  # Mock pygame.error as a real exception class
    mock_pygame.key.get_pressed.return_value = [False] * 512
    mock_pygame.K_ESCAPE = 27
    mock_pygame.KEYDOWN = 768
    return mock_pygame


def setup_mock_resource_manager(mock_rm_class):
    """Helper to setup ResourceManager mock."""
    mock_rm = Mock()
    mock_rm.tile_width = 128
    mock_rm.tile_height = 64
    mock_rm.get_loaded_assets.return_value = {}
    mock_rm_class.return_value = mock_rm
    return mock_rm


def setup_mock_camera(mock_camera_class):
    """Helper to setup Camera mock."""
    mock_camera = Mock()
    mock_camera.get_offset.return_value = (0, 0)
    mock_camera_class.return_value = mock_camera
    return mock_camera


class TestMainInitialization:
    """Tests for main function initialization."""
    
    @patch('src.main.pygame')
    @patch('src.main.ResourceManager')
    @patch('src.main.Camera')
    @patch('src.main.RenderingEngine')
    @patch('src.main.create_hospital_entities')
    def test_main_initializes_pygame(self, mock_create_entities, mock_engine_class, 
                                     mock_camera_class, mock_rm_class, mock_pygame):
        """Test that main initializes Pygame correctly."""
        setup_mock_pygame(mock_pygame)
        setup_mock_resource_manager(mock_rm_class)
        mock_pygame.display.set_mode.return_value = Mock()
        mock_pygame.time.Clock.return_value = Mock()
        mock_pygame.event.get.return_value = [Mock(type=256)]
        mock_create_entities.return_value = []
        
        main()
        
        mock_pygame.init.assert_called_once()
    
    @patch('src.main.pygame')
    @patch('src.main.ResourceManager')
    @patch('src.main.Camera')
    @patch('src.main.RenderingEngine')
    @patch('src.main.create_hospital_entities')
    def test_main_creates_display_surface(self, mock_create_entities, mock_engine_class,
                                         mock_camera_class, mock_rm_class, mock_pygame):
        """Test that main creates display surface with correct dimensions."""
        setup_mock_pygame(mock_pygame)
        setup_mock_resource_manager(mock_rm_class)
        mock_screen = Mock()
        mock_pygame.display.set_mode.return_value = mock_screen
        mock_pygame.time.Clock.return_value = Mock()
        mock_pygame.event.get.return_value = [Mock(type=256)]
        mock_create_entities.return_value = []
        
        main()
        
        from src.settings import SCREEN_WIDTH, SCREEN_HEIGHT
        mock_pygame.display.set_mode.assert_called_once_with((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    @patch('src.main.pygame')
    @patch('src.main.ResourceManager')
    @patch('src.main.Camera')
    @patch('src.main.RenderingEngine')
    @patch('src.main.create_hospital_entities')
    def test_main_creates_clock(self, mock_create_entities, mock_engine_class,
                               mock_camera_class, mock_rm_class, mock_pygame):
        """Test that main creates clock for FPS management."""
        setup_mock_pygame(mock_pygame)
        setup_mock_resource_manager(mock_rm_class)
        mock_pygame.display.set_mode.return_value = Mock()
        mock_clock = Mock()
        mock_pygame.time.Clock.return_value = mock_clock
        mock_pygame.event.get.return_value = [Mock(type=256)]
        mock_create_entities.return_value = []
        
        main()
        
        mock_pygame.time.Clock.assert_called_once()
    
    @patch('src.main.pygame')
    @patch('src.main.ResourceManager')
    @patch('src.main.Camera')
    @patch('src.main.RenderingEngine')
    @patch('src.main.create_hospital_entities')
    def test_main_initializes_all_components(self, mock_create_entities, mock_engine_class,
                                            mock_camera_class, mock_rm_class, mock_pygame):
        """Test that main initializes ResourceManager, Camera, and RenderingEngine."""
        setup_mock_pygame(mock_pygame)
        mock_rm = setup_mock_resource_manager(mock_rm_class)
        mock_screen = Mock()
        mock_pygame.display.set_mode.return_value = mock_screen
        mock_pygame.time.Clock.return_value = Mock()
        mock_pygame.event.get.return_value = [Mock(type=256)]
        
        mock_camera = Mock()
        mock_engine = Mock()
        mock_camera_class.return_value = mock_camera
        mock_engine_class.return_value = mock_engine
        mock_create_entities.return_value = []
        
        main()
        
        mock_rm_class.assert_called_once()
        mock_camera_class.assert_called_once()
        mock_engine_class.assert_called_once_with(mock_screen, mock_rm, mock_camera)


class TestMainLoop:
    """Tests for main loop execution."""
    
    @patch('src.main.pygame')
    @patch('src.main.ResourceManager')
    @patch('src.main.Camera')
    @patch('src.main.RenderingEngine')
    @patch('src.main.create_hospital_entities')
    def test_main_loop_handles_quit_event(self, mock_create_entities, mock_engine_class,
                                         mock_camera_class, mock_rm_class, mock_pygame):
        """Test that main loop terminates on QUIT event."""
        setup_mock_pygame(mock_pygame)
        setup_mock_resource_manager(mock_rm_class)
        mock_screen = Mock()
        mock_pygame.display.set_mode.return_value = mock_screen
        mock_pygame.time.Clock.return_value = Mock()
        mock_pygame.event.get.return_value = [Mock(type=256)]
        mock_create_entities.return_value = []
        
        main()
        
        mock_pygame.quit.assert_called_once()
    
    @patch('src.main.pygame')
    @patch('src.main.ResourceManager')
    @patch('src.main.Camera')
    @patch('src.main.RenderingEngine')
    @patch('src.main.create_hospital_entities')
    def test_main_loop_clears_screen(self, mock_create_entities, mock_engine_class,
                                    mock_camera_class, mock_rm_class, mock_pygame):
        """Test that main loop clears screen each frame."""
        setup_mock_pygame(mock_pygame)
        setup_mock_resource_manager(mock_rm_class)
        mock_screen = Mock()
        mock_pygame.display.set_mode.return_value = mock_screen
        mock_pygame.time.Clock.return_value = Mock()
        mock_pygame.event.get.return_value = [Mock(type=256)]
        mock_create_entities.return_value = []
        
        main()
        
        mock_screen.fill.assert_called_with((32, 32, 32))
    
    @patch('src.main.pygame')
    @patch('src.main.ResourceManager')
    @patch('src.main.Camera')
    @patch('src.main.RenderingEngine')
    @patch('src.main.create_hospital_entities')
    def test_main_loop_calls_render(self, mock_create_entities, mock_engine_class,
                                   mock_camera_class, mock_rm_class, mock_pygame):
        """Test that main loop calls rendering_engine.render()."""
        setup_mock_pygame(mock_pygame)
        setup_mock_resource_manager(mock_rm_class)
        mock_pygame.display.set_mode.return_value = Mock()
        mock_pygame.time.Clock.return_value = Mock()
        mock_pygame.event.get.return_value = [Mock(type=256)]
        
        mock_engine = Mock()
        mock_engine_class.return_value = mock_engine
        mock_create_entities.return_value = []
        
        main()
        
        mock_engine.render.assert_called()
    
    @patch('src.main.pygame')
    @patch('src.main.ResourceManager')
    @patch('src.main.Camera')
    @patch('src.main.RenderingEngine')
    @patch('src.main.create_hospital_entities')
    def test_main_loop_flips_display(self, mock_create_entities, mock_engine_class,
                                    mock_camera_class, mock_rm_class, mock_pygame):
        """Test that main loop flips display each frame."""
        setup_mock_pygame(mock_pygame)
        setup_mock_resource_manager(mock_rm_class)
        mock_pygame.display.set_mode.return_value = Mock()
        mock_pygame.time.Clock.return_value = Mock()
        mock_pygame.event.get.return_value = [Mock(type=256)]
        mock_create_entities.return_value = []
        
        main()
        
        mock_pygame.display.flip.assert_called()
    
    @patch('src.main.pygame')
    @patch('src.main.ResourceManager')
    @patch('src.main.Camera')
    @patch('src.main.RenderingEngine')
    @patch('src.main.create_hospital_entities')
    def test_main_loop_ticks_clock(self, mock_create_entities, mock_engine_class,
                                  mock_camera_class, mock_rm_class, mock_pygame):
        """Test that main loop ticks clock at FPS."""
        setup_mock_pygame(mock_pygame)
        setup_mock_resource_manager(mock_rm_class)
        mock_pygame.display.set_mode.return_value = Mock()
        mock_clock = Mock()
        mock_pygame.time.Clock.return_value = mock_clock
        mock_pygame.event.get.return_value = [Mock(type=256)]
        mock_create_entities.return_value = []
        
        main()
        
        from src.settings import FPS
        mock_clock.tick.assert_called_with(FPS)
