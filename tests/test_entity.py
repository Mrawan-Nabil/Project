"""Unit tests for Entity."""

import pytest
from src.entity import Entity


class TestEntityUnit:
    """Example-based unit tests for Entity."""
    
    def test_entity_initialization(self):
        """Test that entity initializes with correct attributes."""
        entity = Entity(2, 3, "assets/sprite.png")
        assert entity.row == 2, f"Expected row=2, got {entity.row}"
        assert entity.col == 3, f"Expected col=3, got {entity.col}"
        assert entity.sprite_path == "assets/sprite.png", \
            f"Expected sprite_path='assets/sprite.png', got {entity.sprite_path}"
    
    def test_depth_calculated_on_init(self):
        """Test that depth is calculated as row + col on initialization."""
        entity = Entity(2, 3, "assets/sprite.png")
        expected_depth = 2 + 3
        assert entity.depth == expected_depth, \
            f"Expected depth={expected_depth}, got {entity.depth}"
    
    def test_depth_calculation_at_origin(self):
        """Test depth calculation for entity at origin (0, 0)."""
        entity = Entity(0, 0, "assets/sprite.png")
        assert entity.depth == 0, f"Expected depth=0, got {entity.depth}"
    
    def test_depth_calculation_various_positions(self):
        """Test depth calculation for various grid positions."""
        test_cases = [
            (0, 0, 0),
            (1, 0, 1),
            (0, 1, 1),
            (2, 2, 4),
            (5, 3, 8),
            (10, 15, 25)
        ]
        
        for row, col, expected_depth in test_cases:
            entity = Entity(row, col, "assets/sprite.png")
            assert entity.depth == expected_depth, \
                f"For position ({row}, {col}), expected depth={expected_depth}, got {entity.depth}"
    
    def test_update_position_changes_row_and_col(self):
        """Test that update_position changes row and col attributes."""
        entity = Entity(2, 3, "assets/sprite.png")
        entity.update_position(5, 7)
        assert entity.row == 5, f"Expected row=5, got {entity.row}"
        assert entity.col == 7, f"Expected col=7, got {entity.col}"
    
    def test_update_position_recalculates_depth(self):
        """Test that update_position recalculates depth value."""
        entity = Entity(2, 3, "assets/sprite.png")
        initial_depth = entity.depth
        entity.update_position(5, 7)
        expected_depth = 5 + 7
        assert entity.depth == expected_depth, \
            f"Expected depth={expected_depth}, got {entity.depth}"
        assert entity.depth != initial_depth, \
            "Depth should change after position update"
    
    def test_update_position_maintains_depth_invariant(self):
        """Test that depth always equals row + col after update_position."""
        entity = Entity(1, 1, "assets/sprite.png")
        
        positions = [(0, 0), (3, 4), (10, 5), (2, 8)]
        for row, col in positions:
            entity.update_position(row, col)
            expected_depth = row + col
            assert entity.depth == expected_depth, \
                f"After update to ({row}, {col}), expected depth={expected_depth}, got {entity.depth}"
    
    def test_sprite_path_unchanged_after_update(self):
        """Test that sprite_path remains unchanged after position update."""
        sprite_path = "assets/entity.png"
        entity = Entity(2, 3, sprite_path)
        entity.update_position(5, 7)
        assert entity.sprite_path == sprite_path, \
            f"Expected sprite_path='{sprite_path}', got '{entity.sprite_path}'"
    
    def test_multiple_position_updates(self):
        """Test that multiple position updates work correctly."""
        entity = Entity(0, 0, "assets/sprite.png")
        
        # First update
        entity.update_position(1, 2)
        assert entity.row == 1 and entity.col == 2 and entity.depth == 3
        
        # Second update
        entity.update_position(3, 4)
        assert entity.row == 3 and entity.col == 4 and entity.depth == 7
        
        # Third update
        entity.update_position(0, 0)
        assert entity.row == 0 and entity.col == 0 and entity.depth == 0
    
    def test_entity_with_different_sprite_paths(self):
        """Test that entities can have different sprite paths."""
        entity1 = Entity(1, 1, "assets/floor.png")
        entity2 = Entity(1, 1, "assets/wall.png")
        entity3 = Entity(1, 1, "assets/character.png")
        
        assert entity1.sprite_path == "assets/floor.png"
        assert entity2.sprite_path == "assets/wall.png"
        assert entity3.sprite_path == "assets/character.png"
    
    def test_entities_at_same_position_have_same_depth(self):
        """Test that entities at the same position have equal depth."""
        entity1 = Entity(2, 3, "assets/sprite1.png")
        entity2 = Entity(2, 3, "assets/sprite2.png")
        
        assert entity1.depth == entity2.depth, \
            f"Entities at same position should have same depth, got {entity1.depth} and {entity2.depth}"
