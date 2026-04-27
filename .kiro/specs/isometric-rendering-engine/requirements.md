# Requirements Document

## Introduction

This document specifies the requirements for a foundational 2.5D isometric rendering engine for a Pygame-based hospital management game. The engine provides core rendering capabilities including isometric coordinate transformation, depth-sorted rendering (painter's algorithm), asset management, and camera offset support. The system uses transparent PNG sprites with standard isometric tile dimensions (128x64 pixels) and follows object-oriented design principles for modularity and maintainability.

## Glossary

- **Rendering_Engine**: The core system responsible for drawing isometric graphics to the screen
- **Resource_Manager**: Component that loads and prepares PNG image assets for rendering
- **Isometric_Converter**: Component that transforms 2D Cartesian grid coordinates to 2.5D isometric screen coordinates
- **Y_Sorter**: Component that orders renderable objects by depth to ensure correct visual layering
- **Camera**: Virtual viewport that applies x and y offsets to all rendered objects
- **Entity**: Any game object that occupies a grid position and has a visual sprite representation
- **Grid_Coordinate**: A position on the logical 2D game grid expressed as (row, col)
- **Screen_Coordinate**: A pixel position on the display surface expressed as (x, y)
- **Tile**: The basic unit of the isometric grid with dimensions 128 pixels wide by 64 pixels tall
- **Painter_Algorithm**: Depth-sorting technique where objects are drawn back-to-front based on their position
- **Sprite**: A transparent PNG image representing a visual game element
- **Main_Loop**: The primary game loop that handles updates and rendering at a fixed frame rate

## Requirements

### Requirement 1: Project Structure and Architecture

**User Story:** As a developer, I want a clean modular OOP architecture, so that the codebase is maintainable and extensible.

#### Acceptance Criteria

1. THE Rendering_Engine SHALL be implemented as a separate class from the Main_Loop
2. THE system SHALL define configuration constants in a dedicated settings module
3. THE Resource_Manager SHALL be implemented as a separate class responsible for asset loading
4. THE Isometric_Converter SHALL be implemented as a separate class or module for coordinate transformation
5. THE Main_Loop SHALL initialize all components and orchestrate the game loop

### Requirement 2: Asset Loading and Management

**User Story:** As a developer, I want to load PNG sprites efficiently, so that they render correctly with transparency in Pygame.

#### Acceptance Criteria

1. WHEN a PNG image path is provided, THE Resource_Manager SHALL load the image using Pygame
2. WHEN an image is loaded, THE Resource_Manager SHALL convert it using convert_alpha() for transparency support
3. THE Resource_Manager SHALL cache loaded images to avoid redundant file I/O operations
4. IF an image file cannot be loaded, THEN THE Resource_Manager SHALL raise a descriptive error with the file path

### Requirement 3: Isometric Coordinate Transformation

**User Story:** As a developer, I want to convert grid coordinates to screen coordinates, so that objects appear in correct isometric perspective.

#### Acceptance Criteria

1. WHEN given a Grid_Coordinate (row, col), THE Isometric_Converter SHALL calculate the Screen_Coordinate using the formula: x = (col - row) * (TILE_WIDTH / 2), y = (col + row) * (TILE_HEIGHT / 2)
2. THE Isometric_Converter SHALL use TILE_WIDTH = 128 pixels and TILE_HEIGHT = 64 pixels
3. THE Isometric_Converter SHALL include inline documentation explaining the mathematical transformation
4. WHEN Camera offsets are provided, THE Isometric_Converter SHALL add camera_x to the calculated x coordinate and camera_y to the calculated y coordinate

### Requirement 4: Depth-Sorted Rendering Pipeline

**User Story:** As a developer, I want objects rendered in correct depth order, so that visual layering appears natural in the isometric view.

#### Acceptance Criteria

1. WHEN rendering multiple objects, THE Y_Sorter SHALL sort objects by their depth value before drawing
2. THE Y_Sorter SHALL calculate depth as (row + col) for each Entity
3. THE Rendering_Engine SHALL draw objects in ascending depth order (back-to-front)
4. WHEN two objects have equal depth values, THE Rendering_Engine SHALL maintain stable ordering
5. FOR ALL pairs of objects where object_A has depth less than object_B, object_A SHALL be drawn before object_B

### Requirement 5: Camera Offset System

**User Story:** As a developer, I want camera offset variables in the rendering system, so that map panning can be implemented in the future.

#### Acceptance Criteria

1. THE Camera SHALL maintain camera_x and camera_y offset values
2. WHEN rendering any object, THE Rendering_Engine SHALL apply Camera offsets to the calculated Screen_Coordinate
3. THE Camera SHALL initialize with camera_x = 0 and camera_y = 0
4. THE Camera SHALL provide methods to update camera_x and camera_y values

### Requirement 6: Main Game Loop

**User Story:** As a developer, I want a configurable main game loop, so that the engine runs at a consistent frame rate.

#### Acceptance Criteria

1. THE Main_Loop SHALL run continuously until a quit event is received
2. THE Main_Loop SHALL enforce a configurable FPS cap using Pygame clock
3. THE Main_Loop SHALL handle Pygame QUIT events to terminate gracefully
4. THE Main_Loop SHALL clear the screen before each render cycle
5. THE Main_Loop SHALL call the Rendering_Engine to draw all objects each frame

### Requirement 7: Demonstration Implementation

**User Story:** As a developer, I want a working demonstration, so that I can verify the rendering engine functions correctly.

#### Acceptance Criteria

1. THE system SHALL render a 5x5 grid of floor tiles
2. THE system SHALL render one Entity sprite at Grid_Coordinate (2, 2)
3. WHEN the application starts, THE Camera SHALL position the grid centered on the screen
4. THE demonstration SHALL use placeholder sprites or colored rectangles if actual PNG assets are not available
5. THE Main_Loop SHALL run at 60 FPS by default

### Requirement 8: Code Documentation

**User Story:** As a developer, I want clear documentation of the isometric math, so that I can understand and modify the coordinate system.

#### Acceptance Criteria

1. THE Isometric_Converter SHALL include inline comments explaining the coordinate transformation formula
2. THE Isometric_Converter SHALL include comments explaining why TILE_WIDTH and TILE_HEIGHT values are used
3. THE Y_Sorter SHALL include comments explaining the depth calculation and sorting rationale
4. THE Rendering_Engine SHALL include docstrings for all public methods describing parameters and return values
