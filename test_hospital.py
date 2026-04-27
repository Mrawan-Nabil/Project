#!/usr/bin/env python3
"""Test script for the hospital management game.

This script tests the asset loading, map parsing, and rendering system
to ensure everything works correctly before running the main game.
"""

import sys
import os

# Add src to path so we can import modules
sys.path.insert(0, 'src')

try:
    import pygame
except ImportError:
    import pygame_ce as pygame

from src.resource_manager import ResourceManager
from src.map_data import MAP_LEGEND, get_legend_info, validate_maps
from src.map_parser import MapParser, create_hospital_entities


def test_asset_loading():
    """Test loading assets from the assets directory."""
    print("=== Testing Asset Loading ===")
    
    resource_manager = ResourceManager()
    
    try:
        resource_manager.load_assets_from_directory("assets")
        loaded_assets = resource_manager.get_loaded_assets()
        
        print(f"✓ Successfully loaded {len(loaded_assets)} assets")
        print("Available assets:")
        for asset_key in sorted(loaded_assets.keys()):
            sprite = loaded_assets[asset_key]
            print(f"  - {asset_key}: {sprite.get_width()}x{sprite.get_height()}")
        
        return resource_manager
        
    except Exception as e:
        print(f"✗ Failed to load assets: {e}")
        return None


def test_map_validation():
    """Test map data validation."""
    print("\n=== Testing Map Validation ===")
    
    try:
        validate_maps()
        print("✓ Maps are valid")
        
        legend_info = get_legend_info()
        print(f"✓ Legend has {legend_info['total_symbols']} symbols")
        print(f"✓ Legend references {legend_info['unique_assets']} unique assets")
        
        return True
        
    except Exception as e:
        print(f"✗ Map validation failed: {e}")
        return False


def test_map_parsing(resource_manager):
    """Test parsing maps and creating entities."""
    print("\n=== Testing Map Parsing ===")
    
    if not resource_manager:
        print("✗ Cannot test map parsing without loaded assets")
        return None
    
    try:
        parser = MapParser(resource_manager)
        
        # Check for missing assets
        missing = parser.get_missing_assets()
        if missing:
            print(f"⚠ Missing assets: {missing}")
        else:
            print("✓ All required assets are available")
        
        # Create entities
        entities = parser.parse_maps()
        print(f"✓ Created {len(entities)} entities")
        
        # Count entity types
        floor_count = sum(1 for e in entities if e.is_floor_tile)
        entity_count = len(entities) - floor_count
        
        print(f"  - Floor tiles: {floor_count}")
        print(f"  - Objects/Characters: {entity_count}")
        
        return entities
        
    except Exception as e:
        print(f"✗ Map parsing failed: {e}")
        return None


def test_sprite_anchoring(entities):
    """Test sprite anchoring calculations."""
    print("\n=== Testing Sprite Anchoring ===")
    
    if not entities:
        print("✗ Cannot test anchoring without entities")
        return False
    
    try:
        # Test a few entities
        test_entities = entities[:5]
        
        for entity in test_entities:
            pos = entity.get_render_position(0, 0)
            print(f"  {entity.asset_key} at ({entity.row},{entity.col}) -> screen {pos}")
            
            if entity.is_floor_tile:
                # Floor tiles should have no anchor offset
                assert entity.anchor_offset_x == 0
                assert entity.anchor_offset_y == 0
            else:
                # Non-floor entities should have anchor offsets
                print(f"    Anchor offset: ({entity.anchor_offset_x}, {entity.anchor_offset_y})")
        
        print("✓ Sprite anchoring working correctly")
        return True
        
    except Exception as e:
        print(f"✗ Sprite anchoring test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("Hospital Management Game - Test Suite")
    print("=" * 50)
    
    # Test 1: Asset Loading
    resource_manager = test_asset_loading()
    
    # Test 2: Map Validation
    maps_valid = test_map_validation()
    
    # Test 3: Map Parsing
    entities = test_map_parsing(resource_manager)
    
    # Test 4: Sprite Anchoring
    anchoring_ok = test_sprite_anchoring(entities)
    
    # Summary
    print("\n=== Test Summary ===")
    
    tests_passed = 0
    total_tests = 4
    
    if resource_manager:
        print("✓ Asset Loading: PASS")
        tests_passed += 1
    else:
        print("✗ Asset Loading: FAIL")
    
    if maps_valid:
        print("✓ Map Validation: PASS")
        tests_passed += 1
    else:
        print("✗ Map Validation: FAIL")
    
    if entities:
        print("✓ Map Parsing: PASS")
        tests_passed += 1
    else:
        print("✗ Map Parsing: FAIL")
    
    if anchoring_ok:
        print("✓ Sprite Anchoring: PASS")
        tests_passed += 1
    else:
        print("✗ Sprite Anchoring: FAIL")
    
    print(f"\nResult: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Ready to run the hospital game.")
        print("\nRun the game with: python src/main.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1
    
    return 0


if __name__ == "__main__":
    # Initialize pygame for testing (needed for image loading)
    pygame.init()
    pygame.display.set_mode((1, 1))  # Minimal display for testing
    
    try:
        exit_code = main()
        sys.exit(exit_code)
    finally:
        pygame.quit()