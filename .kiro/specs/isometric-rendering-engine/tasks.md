# Implementation Plan: Isometric Rendering Engine

## Overview

This implementation plan breaks down the isometric rendering engine into discrete, incremental coding tasks. The engine consists of 6 core components (ResourceManager, IsometricConverter, Camera, Entity, Y-Sorter, RenderingEngine) with a demonstration main loop. The implementation follows a bottom-up approach, building foundational components first, then integrating them into the rendering pipeline.

The design includes 10 correctness properties that will be validated through property-based tests using Hypothesis. Each property test is marked as optional to allow for faster MVP delivery while maintaining the option for comprehensive correctness validation.

## Tasks

- [x] 1. Set up project structure and configuration
  - Create directory structure: `src/`, `tests/`, `assets/`
  - Create `src/settings.py` with configuration constants (SCREEN_WIDTH=1024, SCREEN_HEIGHT=768, FPS=60, TILE_WIDTH=128, TILE_HEIGHT=64)
  - Create `requirements.txt` with dependencies: pygame, hypothesis, pytest, pytest-cov
  - Create placeholder PNG files in `assets/` directory (floor_tile.png, entity.png) or document where to place them
  - _Requirements: 1.2, 7.4_

- [ ] 2. Implement ResourceManager class
  - [x] 2.1 Create ResourceManager with image loading and caching
    - Create `src/resource_manager.py`
    - Implement `__init__` with empty cache dictionary
    - Implement `load_image(path: str)` method that checks cache, loads with pygame.image.load(), applies convert_alpha(), caches result, and returns Surface
    - Add error handling that wraps pygame.error and FileNotFoundError with descriptive messages including file path
    - Add docstrings for class and methods
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 8.4_

  - [ ]* 2.2 Write property test for image loading (Property 1)
    - **Property 1: Image Loading Succeeds for Valid Paths**
    - **Validates: Requirements 2.1**
    - Create `tests/test_properties.py`
    - Use Hypothesis to generate temporary PNG files with valid image data
    - Test that ResourceManager.load_image() returns a pygame.Surface for any valid PNG path
    - Add property tag comment: `# Feature: isometric-rendering-engine, Property 1`
    - _Requirements: 2.1_

  - [ ]* 2.3 Write property test for alpha channel (Property 2)
    - **Property 2: Loaded Images Have Alpha Channel**
    - **Validates: Requirements 2.2**
    - Use Hypothesis to generate temporary PNG files
    - Test that loaded Surface has SRCALPHA flag set
    - Add property tag comment: `# Feature: isometric-rendering-engine, Property 2`
    - _Requirements: 2.2_

  - [ ]* 2.4 Write property test for caching (Property 3)
    - **Property 3: Image Caching Returns Same Object**
    - **Validates: Requirements 2.3**
    - Use Hypothesis to generate file paths with actual temp files
    - Test that loading same path twice returns identical object (identity check with `is`)
    - Add property tag comment: `# Feature: isometric-rendering-engine, Property 3`
    - _Requirements: 2.3_

  - [ ]* 2.5 Write property test for error handling (Property 4)
    - **Property 4: Invalid Paths Raise Descriptive Errors**
    - **Validates: Requirements 2.4**
    - Use Hypothesis to generate random non-existent file paths
    - Test that loading invalid path raises exception containing the path in error message
    - Add property tag comment: `# Feature: isometric-rendering-engine, Property 4`
    - _Requirements: 2.4_

  - [x]* 2.6 Write unit tests for ResourceManager
    - Test loading a specific known PNG file
    - Test error message format for missing file
    - Test cache hit behavior with specific file
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [ ] 3. Implement IsometricConverter class
  - [x] 3.1 Create IsometricConverter with coordinate transformation
    - Create `src/isometric_converter.py`
    - Define class constants: TILE_WIDTH = 128, TILE_HEIGHT = 64
    - Implement static method `grid_to_screen(row: int, col: int, camera_x: int = 0, camera_y: int = 0) -> Tuple[int, int]`
    - Apply formula: x = (col - row) * (TILE_WIDTH / 2) + camera_x, y = (col + row) * (TILE_HEIGHT / 2) + camera_y
    - Add inline comments explaining the isometric projection math and why tile dimensions are used
    - Add docstrings with parameter descriptions
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 8.1, 8.2_

  - [ ]* 3.2 Write property test for coordinate transformation (Property 5)
    - **Property 5: Coordinate Transformation Formula Correctness**
    - **Validates: Requirements 3.1**
    - Use Hypothesis to generate random (row, col) pairs in range [-1000, 1000]
    - Test with camera offsets (0, 0) and verify: x = (col - row) * 64, y = (col + row) * 32
    - Add property tag comment: `# Feature: isometric-rendering-engine, Property 5`
    - _Requirements: 3.1_

  - [ ]* 3.3 Write property test for camera offset application (Property 6)
    - **Property 6: Camera Offset Application**
    - **Validates: Requirements 3.4**
    - Use Hypothesis to generate random (row, col) and (camera_x, camera_y) values
    - Test that screen coordinates correctly include camera offsets
    - Add property tag comment: `# Feature: isometric-rendering-engine, Property 6`
    - _Requirements: 3.4_

  - [x]* 3.4 Write unit tests for IsometricConverter
    - Test origin point (0, 0) maps to (0, 0)
    - Test specific known coordinates: (1, 0) → (64, 32), (0, 1) → (-64, 32), (2, 2) → (0, 128)
    - Test that TILE_WIDTH = 128 and TILE_HEIGHT = 64
    - _Requirements: 3.1, 3.2_

- [ ] 4. Implement Camera class
  - [x] 4.1 Create Camera with offset management
    - Create `src/camera.py`
    - Implement `__init__` initializing camera_x = 0, camera_y = 0
    - Implement `set_offset(x: int, y: int)` method
    - Implement `get_offset() -> Tuple[int, int]` method
    - Add docstrings for class and methods
    - _Requirements: 5.1, 5.3, 5.4_

  - [ ]* 4.2 Write property test for camera offset round-trip (Property 10)
    - **Property 10: Camera Offset Round-Trip**
    - **Validates: Requirements 5.1, 5.4**
    - Use Hypothesis to generate random (x, y) offset values
    - Test that set_offset followed by get_offset returns the same values
    - Add property tag comment: `# Feature: isometric-rendering-engine, Property 10`
    - _Requirements: 5.1, 5.4_

  - [x]* 4.3 Write unit tests for Camera
    - Test initial state is (0, 0)
    - Test set_offset updates both x and y
    - Test get_offset returns tuple
    - _Requirements: 5.1, 5.3, 5.4_

- [x] 5. Checkpoint - Ensure foundational components work
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 6. Implement Entity class
  - [x] 6.1 Create Entity data class
    - Create `src/entity.py`
    - Implement Entity class with attributes: row, col, sprite_path, depth
    - Implement `__init__(row: int, col: int, sprite_path: str)` that calculates depth = row + col
    - Implement `update_position(row: int, col: int)` that updates position and recalculates depth
    - Add docstrings
    - _Requirements: 4.2_

  - [ ]* 6.2 Write property test for depth calculation (Property 7)
    - **Property 7: Depth Calculation Correctness**
    - **Validates: Requirements 4.2**
    - Use Hypothesis to generate random Entity objects with various (row, col) values
    - Test that entity.depth == entity.row + entity.col
    - Add property tag comment: `# Feature: isometric-rendering-engine, Property 7`
    - _Requirements: 4.2_

  - [x]* 6.3 Write unit tests for Entity
    - Test entity creation with specific coordinates
    - Test depth calculation for known values
    - Test update_position recalculates depth
    - _Requirements: 4.2_

- [ ] 7. Implement Y-Sorter class
  - [x] 7.1 Create Y-Sorter with depth sorting
    - Create `src/y_sorter.py`
    - Implement static method `sort_by_depth(entities: List[Entity]) -> List[Entity]`
    - Use Python's sorted() with key=lambda e: e.depth to ensure stable sort
    - Add comments explaining depth calculation (row + col) and back-to-front rendering rationale
    - Add docstrings
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 8.3_

  - [ ]* 7.2 Write property test for depth-based ordering (Property 8)
    - **Property 8: Depth-Based Ordering**
    - **Validates: Requirements 4.1, 4.3, 4.5**
    - Use Hypothesis to generate lists of entities with random positions
    - Test that after sorting, all pairs satisfy: if depth_A < depth_B, then A appears before B
    - Add property tag comment: `# Feature: isometric-rendering-engine, Property 8`
    - _Requirements: 4.1, 4.3, 4.5_

  - [ ]* 7.3 Write property test for stable sort (Property 9)
    - **Property 9: Stable Sort for Equal Depths**
    - **Validates: Requirements 4.4**
    - Use Hypothesis to generate lists with intentionally duplicated depth values
    - Test that relative order of equal-depth entities is preserved after sorting
    - Add property tag comment: `# Feature: isometric-rendering-engine, Property 9`
    - _Requirements: 4.4_

  - [x]* 7.4 Write unit tests for Y-Sorter
    - Test empty list returns empty list
    - Test single entity returns single entity
    - Test specific 3-entity example with known depths: [(2,2), (1,1), (3,0)] → [(1,1), (2,2), (3,0)]
    - _Requirements: 4.1, 4.2, 4.3_

- [ ] 8. Implement RenderingEngine class
  - [x] 8.1 Create RenderingEngine with rendering pipeline
    - Create `src/rendering_engine.py`
    - Implement `__init__(screen: pygame.Surface, resource_manager: ResourceManager, camera: Camera)`
    - Initialize empty entities list
    - Implement `add_entity(entity: Entity)` method
    - Implement `render()` method that:
      - Sorts entities using Y-Sorter
      - Gets camera offset from Camera
      - For each entity: calculates screen position via IsometricConverter, loads sprite from ResourceManager, blits to screen
    - Add docstrings for all public methods
    - _Requirements: 1.1, 4.1, 4.3, 5.2, 8.4_

  - [x]* 8.2 Write unit tests for RenderingEngine
    - Test add_entity increases entity count
    - Test render calls resource_manager.load_image for each entity (use mocks)
    - Test render calls screen.blit for each entity (use mocks)
    - Test render applies camera offset to coordinates
    - _Requirements: 4.1, 4.3, 5.2_

- [x] 9. Checkpoint - Ensure core rendering pipeline works
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 10. Implement main loop and demo scene
  - [x] 10.1 Create main loop with Pygame initialization
    - Create `src/main.py`
    - Implement pygame.init() with error checking
    - Create display surface with SCREEN_WIDTH x SCREEN_HEIGHT
    - Create clock for FPS management
    - Initialize all components (ResourceManager, Camera, RenderingEngine)
    - Implement main loop that:
      - Handles pygame.QUIT events
      - Clears screen with black fill
      - Calls rendering_engine.render()
      - Flips display
      - Ticks clock at FPS
    - Call pygame.quit() on exit
    - _Requirements: 1.5, 6.1, 6.2, 6.3, 6.4, 6.5, 7.5_

  - [x] 10.2 Create demo scene setup function
    - Implement `setup_demo_scene(rendering_engine: RenderingEngine)` function
    - Create 5x5 grid of floor tile entities (25 total) at positions (row, col) for row in [0,4], col in [0,4]
    - Create one entity sprite at grid position (2, 2)
    - Calculate camera offset to center the grid on screen: camera_x = SCREEN_WIDTH // 2, camera_y = SCREEN_HEIGHT // 4
    - Apply camera offset
    - _Requirements: 7.1, 7.2, 7.3_

  - [ ]* 10.3 Write unit tests for main loop components
    - Test initialization creates all components
    - Test QUIT event terminates loop (use mock event queue)
    - Test screen.fill is called each frame
    - Test rendering_engine.render is called each frame
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ] 11. Create integration tests
  - [ ]* 11.1 Write full rendering pipeline integration test
    - Create complete system with all components
    - Add multiple entities at various positions
    - Execute render cycle
    - Verify entities are drawn in correct depth order (use mock tracking)
    - _Requirements: 4.1, 4.3, 5.2_

  - [ ]* 11.2 Write demo scene integration test
    - Run setup_demo_scene()
    - Verify 25 floor tiles are added (5x5 grid)
    - Verify 1 entity at position (2, 2)
    - Verify camera offset is set
    - _Requirements: 7.1, 7.2, 7.3_

  - [ ]* 11.3 Write asset loading integration test
    - Test with actual PNG files in assets directory (if available)
    - Verify all demo assets load successfully
    - Test graceful error handling if assets missing
    - _Requirements: 2.1, 2.4_

- [x] 12. Final checkpoint and verification
  - Run full test suite with coverage report (pytest --cov=src tests/)
  - Verify all 10 correctness properties pass (if property tests were implemented)
  - Run the demo application and verify visual output
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP delivery
- Each task references specific requirements for traceability
- Property-based tests validate the 10 correctness properties from the design document
- Unit tests validate specific examples and edge cases
- Integration tests verify component interactions
- The implementation uses Python with Pygame as specified in the design document
- Checkpoints ensure incremental validation and provide opportunities for user feedback
- All code should include docstrings and inline comments as specified in Requirements 8.1-8.4
