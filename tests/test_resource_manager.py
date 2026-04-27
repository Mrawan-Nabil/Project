"""Unit and property-based tests for ResourceManager."""

import os
import tempfile
import pytest
try:
    import pygame
except ImportError:
    import pygame_ce as pygame
from hypothesis import given, strategies as st, settings
from PIL import Image
from src.resource_manager import ResourceManager


# Initialize pygame for testing
pygame.init()
# Set up a display mode for convert_alpha() to work
pygame.display.set_mode((1, 1))


class TestResourceManagerUnit:
    """Example-based unit tests for ResourceManager."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.resource_manager = ResourceManager()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        # Clean up temporary files
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def create_test_image(self, filename: str, width: int = 64, height: int = 64) -> str:
        """Create a test PNG image and return its path."""
        path = os.path.join(self.temp_dir, filename)
        # Create a simple RGBA image using PIL
        img = Image.new('RGBA', (width, height), color=(255, 0, 0, 128))
        img.save(path, 'PNG')
        return path
    
    def test_load_image_returns_surface(self):
        """Test that loading a valid PNG returns a pygame Surface."""
        path = self.create_test_image("test.png")
        surface = self.resource_manager.load_image(path)
        assert isinstance(surface, pygame.Surface)
    
    def test_load_image_has_alpha_channel(self):
        """Test that loaded images have alpha channel (convert_alpha applied)."""
        path = self.create_test_image("test_alpha.png")
        surface = self.resource_manager.load_image(path)
        # Check that the surface has the SRCALPHA flag
        assert surface.get_flags() & pygame.SRCALPHA
    
    def test_load_image_caches_result(self):
        """Test that loading the same image twice returns the same object."""
        path = self.create_test_image("test_cache.png")
        surface1 = self.resource_manager.load_image(path)
        surface2 = self.resource_manager.load_image(path)
        # Use identity check (is) not equality check (==)
        assert surface1 is surface2
    
    def test_load_nonexistent_file_raises_error(self):
        """Test that loading a non-existent file raises FileNotFoundError."""
        nonexistent_path = os.path.join(self.temp_dir, "does_not_exist.png")
        with pytest.raises(FileNotFoundError) as exc_info:
            self.resource_manager.load_image(nonexistent_path)
        # Verify the path is in the error message
        assert nonexistent_path in str(exc_info.value)
    
    def test_load_invalid_file_raises_pygame_error(self):
        """Test that loading an invalid image file raises pygame.error."""
        # Create a text file with .png extension
        invalid_path = os.path.join(self.temp_dir, "invalid.png")
        with open(invalid_path, 'w') as f:
            f.write("This is not a valid PNG file")
        
        with pytest.raises(pygame.error) as exc_info:
            self.resource_manager.load_image(invalid_path)
        # Verify the path is in the error message
        assert invalid_path in str(exc_info.value)
    
    def test_multiple_different_images_cached_separately(self):
        """Test that different images are cached separately."""
        path1 = self.create_test_image("image1.png", 32, 32)
        path2 = self.create_test_image("image2.png", 64, 64)
        
        surface1 = self.resource_manager.load_image(path1)
        surface2 = self.resource_manager.load_image(path2)
        
        # Different images should be different objects
        assert surface1 is not surface2
        # Verify dimensions are different
        assert surface1.get_size() != surface2.get_size()
    
    def test_load_specific_floor_tile_asset(self):
        """Test loading the specific known floor_tile.png asset.
        
        This test verifies that the actual project asset can be loaded
        successfully and has the expected properties.
        """
        floor_tile_path = "assets/floor_tile.png"
        
        # Verify the file exists
        assert os.path.exists(floor_tile_path), \
            f"Expected asset file {floor_tile_path} to exist"
        
        # Load the floor tile
        surface = self.resource_manager.load_image(floor_tile_path)
        
        # Verify it's a valid Surface
        assert isinstance(surface, pygame.Surface)
        
        # Verify it has alpha channel
        assert surface.get_flags() & pygame.SRCALPHA
        
        # Verify expected dimensions (128x64 for isometric tile)
        width, height = surface.get_size()
        assert width == 128, f"Expected floor tile width 128, got {width}"
        assert height == 64, f"Expected floor tile height 64, got {height}"
    
    def test_load_specific_entity_asset(self):
        """Test loading the specific known entity.png asset.
        
        This test verifies that the actual project asset can be loaded
        successfully and has the expected properties.
        """
        entity_path = "assets/entity.png"
        
        # Verify the file exists
        assert os.path.exists(entity_path), \
            f"Expected asset file {entity_path} to exist"
        
        # Load the entity sprite
        surface = self.resource_manager.load_image(entity_path)
        
        # Verify it's a valid Surface
        assert isinstance(surface, pygame.Surface)
        
        # Verify it has alpha channel
        assert surface.get_flags() & pygame.SRCALPHA
    
    def test_missing_file_error_message_format(self):
        """Test that error message for missing file includes the path and is descriptive.
        
        This test verifies the specific error message format required by the spec:
        'Failed to load asset: {path} - File not found'
        """
        missing_path = "assets/nonexistent_file.png"
        
        with pytest.raises(FileNotFoundError) as exc_info:
            self.resource_manager.load_image(missing_path)
        
        error_message = str(exc_info.value)
        
        # Verify the error message contains the path
        assert missing_path in error_message, \
            f"Error message should contain the file path. Got: {error_message}"
        
        # Verify the error message has the expected format
        assert "Failed to load asset:" in error_message, \
            f"Error message should start with 'Failed to load asset:'. Got: {error_message}"
        assert "File not found" in error_message, \
            f"Error message should contain 'File not found'. Got: {error_message}"
    
    def test_cache_hit_with_specific_file(self):
        """Test cache hit behavior with a specific known file.
        
        This test verifies that loading the same specific asset file multiple
        times returns the exact same cached Surface object (identity check).
        """
        floor_tile_path = "assets/floor_tile.png"
        
        # Load the same file three times
        surface1 = self.resource_manager.load_image(floor_tile_path)
        surface2 = self.resource_manager.load_image(floor_tile_path)
        surface3 = self.resource_manager.load_image(floor_tile_path)
        
        # All three should be the exact same object (identity check)
        assert surface1 is surface2, \
            "Second load should return cached object"
        assert surface2 is surface3, \
            "Third load should return cached object"
        assert surface1 is surface3, \
            "All loads should return the same cached object"


class TestResourceManagerProperties:
    """Property-based tests for ResourceManager."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.resource_manager = ResourceManager()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def create_test_image(self, filename: str, width: int = 64, height: int = 64) -> str:
        """Create a test PNG image and return its path."""
        path = os.path.join(self.temp_dir, filename)
        img = Image.new('RGBA', (width, height), color=(255, 0, 0, 128))
        img.save(path, 'PNG')
        return path
    
    @given(
        width=st.integers(min_value=1, max_value=256),
        height=st.integers(min_value=1, max_value=256)
    )
    @settings(max_examples=100)
    def test_property_1_image_loading_succeeds(self, width, height):
        """Property 1: For any valid PNG file path, the ResourceManager SHALL 
        successfully load the image and return a Pygame Surface.
        
        **Validates: Requirements 2.1**
        """
        # Create a valid PNG file with random dimensions
        path = self.create_test_image(f"prop1_{width}x{height}.png", width, height)
        
        # Load the image
        surface = self.resource_manager.load_image(path)
        
        # Verify a Surface is returned
        assert isinstance(surface, pygame.Surface)
        assert surface.get_width() == width
        assert surface.get_height() == height
    
    @given(
        width=st.integers(min_value=1, max_value=256),
        height=st.integers(min_value=1, max_value=256)
    )
    @settings(max_examples=100)
    def test_property_2_loaded_images_have_alpha(self, width, height):
        """Property 2: For any image loaded by the ResourceManager, the returned 
        Surface SHALL have an alpha channel (indicating convert_alpha() was applied).
        
        **Validates: Requirements 2.2**
        """
        # Create a valid PNG file
        path = self.create_test_image(f"prop2_{width}x{height}.png", width, height)
        
        # Load the image
        surface = self.resource_manager.load_image(path)
        
        # Verify the surface has alpha channel
        assert surface.get_flags() & pygame.SRCALPHA, \
            "Surface should have SRCALPHA flag after convert_alpha()"
    
    @given(
        filename=st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')),
            min_size=1,
            max_size=20
        ).map(lambda s: s + ".png")
    )
    @settings(max_examples=100)
    def test_property_3_caching_returns_same_object(self, filename):
        """Property 3: For any image path, loading it multiple times through the 
        ResourceManager SHALL return the same cached Surface object (identity 
        equality, not just value equality).
        
        **Validates: Requirements 2.3**
        """
        # Create a valid PNG file
        path = self.create_test_image(filename)
        
        # Load the image twice
        surface1 = self.resource_manager.load_image(path)
        surface2 = self.resource_manager.load_image(path)
        
        # Verify identity equality (same object in memory)
        assert surface1 is surface2, \
            "Loading the same path twice should return the same cached object"
    
    @given(
        invalid_filename=st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')),
            min_size=1,
            max_size=20
        ).map(lambda s: s + "_nonexistent.png")
    )
    @settings(max_examples=100)
    def test_property_4_invalid_paths_raise_descriptive_errors(self, invalid_filename):
        """Property 4: For any invalid or non-existent file path, the ResourceManager 
        SHALL raise an error that includes the problematic path in the error message.
        
        **Validates: Requirements 2.4**
        """
        # Create a path that doesn't exist
        nonexistent_path = os.path.join(self.temp_dir, invalid_filename)
        
        # Attempt to load and verify error is raised
        with pytest.raises((FileNotFoundError, pygame.error)) as exc_info:
            self.resource_manager.load_image(nonexistent_path)
        
        # Verify the path appears in the error message
        error_message = str(exc_info.value)
        assert nonexistent_path in error_message or invalid_filename in error_message, \
            f"Error message should include the problematic path. Got: {error_message}"
