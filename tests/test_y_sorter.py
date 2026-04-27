"""Unit tests for Y-Sorter depth sorting functionality."""

import pytest
from src.y_sorter import YSorter
from src.entity import Entity


class TestYSorter:
    """Test suite for YSorter class."""
    
    def test_empty_list_returns_empty_list(self):
        """Test that sorting an empty list returns an empty list."""
        entities = []
        result = YSorter.sort_by_depth(entities)
        assert result == []
        assert isinstance(result, list)
    
    def test_single_entity_returns_single_entity(self):
        """Test that sorting a single entity returns a list with that entity."""
        entity = Entity(1, 1, "sprite.png")
        entities = [entity]
        result = YSorter.sort_by_depth(entities)
        assert len(result) == 1
        assert result[0] is entity
    
    def test_three_entity_sorting_with_known_depths(self):
        """Test sorting three entities with known depths.
        
        Test case: [(2,2), (1,1), (3,0)] should sort to [(3,0), (1,1), (2,2)]
        - Entity at (3, 0) has depth = 3
        - Entity at (1, 1) has depth = 2
        - Entity at (2, 2) has depth = 4
        
        Expected order after sorting: depth 2, 3, 4
        Which corresponds to: (1,1), (3,0), (2,2)
        """
        entity_a = Entity(2, 2, "sprite_a.png")  # depth = 4
        entity_b = Entity(1, 1, "sprite_b.png")  # depth = 2
        entity_c = Entity(3, 0, "sprite_c.png")  # depth = 3
        
        entities = [entity_a, entity_b, entity_c]
        result = YSorter.sort_by_depth(entities)
        
        # Verify correct order: entity_b (depth=2), entity_c (depth=3), entity_a (depth=4)
        assert len(result) == 3
        assert result[0] is entity_b
        assert result[1] is entity_c
        assert result[2] is entity_a
        
        # Verify depths are in ascending order
        assert result[0].depth == 2
        assert result[1].depth == 3
        assert result[2].depth == 4
    
    def test_stable_sort_preserves_order_for_equal_depths(self):
        """Test that entities with equal depths maintain their relative order."""
        # Create three entities with the same depth
        entity_a = Entity(1, 0, "sprite_a.png")  # depth = 1
        entity_b = Entity(0, 1, "sprite_b.png")  # depth = 1
        entity_c = Entity(1, 0, "sprite_c.png")  # depth = 1
        
        entities = [entity_a, entity_b, entity_c]
        result = YSorter.sort_by_depth(entities)
        
        # Verify stable sort: original order is preserved
        assert len(result) == 3
        assert result[0] is entity_a
        assert result[1] is entity_b
        assert result[2] is entity_c
    
    def test_sorting_does_not_modify_original_list(self):
        """Test that sorting returns a new list without modifying the original."""
        entity_a = Entity(2, 2, "sprite_a.png")  # depth = 4
        entity_b = Entity(1, 1, "sprite_b.png")  # depth = 2
        
        original = [entity_a, entity_b]
        result = YSorter.sort_by_depth(original)
        
        # Original list should be unchanged
        assert original[0] is entity_a
        assert original[1] is entity_b
        
        # Result should be a different list
        assert result is not original
        
        # Result should be sorted
        assert result[0] is entity_b
        assert result[1] is entity_a
    
    def test_sorting_with_zero_depth(self):
        """Test sorting entities including one at origin (depth = 0)."""
        entity_origin = Entity(0, 0, "origin.png")  # depth = 0
        entity_other = Entity(1, 1, "other.png")    # depth = 2
        
        entities = [entity_other, entity_origin]
        result = YSorter.sort_by_depth(entities)
        
        # Origin should come first
        assert result[0] is entity_origin
        assert result[1] is entity_other
    
    def test_sorting_large_depth_values(self):
        """Test sorting with large depth values."""
        entity_far = Entity(100, 100, "far.png")    # depth = 200
        entity_near = Entity(50, 50, "near.png")    # depth = 100
        entity_close = Entity(10, 10, "close.png")  # depth = 20
        
        entities = [entity_far, entity_close, entity_near]
        result = YSorter.sort_by_depth(entities)
        
        # Should be sorted by depth: 20, 100, 200
        assert result[0] is entity_close
        assert result[1] is entity_near
        assert result[2] is entity_far
