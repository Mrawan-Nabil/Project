"""Main entry point for the isometric hospital management game.

This module initializes Pygame, creates all engine components, loads hospital
assets, sets up the hospital layout, and runs the main game loop at a fixed frame rate.
"""

try:
    import pygame
except ImportError:
    import pygame_ce as pygame
import sys

from src.settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS
)
from src.resource_manager import ResourceManager
from src.camera import Camera
from src.rendering_engine import RenderingEngine
from src.map_parser import create_hospital_entities
from src.simulation_state   import SimulationState
from src.dashboard_ui       import DashboardUI, ResourceHUD
from src.simulation_manager import SimulationManager
from src.grid_index         import GridIndex
from src.map_data           import FLOOR_MAP, ENTITY_MAP
from src.map_parser         import AnchoredEntity
from src.isometric_converter import IsometricConverter


def main() -> None:
    """Initialize and run the hospital management game.
    
    This function performs the following steps:
    1. Initialize Pygame with error checking
    2. Create display surface with configured dimensions
    3. Create clock for FPS management
    4. Initialize all engine components (ResourceManager, Camera, RenderingEngine)
    5. Load all PNG assets from the assets directory
    6. Parse hospital maps and create entities
    7. Set up camera to center the hospital layout
    8. Run the main loop:
       - Handle pygame.QUIT events
       - Clear screen with black fill
       - Call rendering_engine.render()
       - Flip display
       - Tick clock at configured FPS
    9. Clean up with pygame.quit() on exit
    """
    # Initialize Pygame with error checking
    init_result = pygame.init()
    if init_result[1] > 0:
        print(f"Warning: {init_result[1]} Pygame module(s) failed to initialize", 
              file=sys.stderr)
    
    # Create display surface with SCREEN_WIDTH x SCREEN_HEIGHT
    try:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Isometric Hospital Management Game")
    except pygame.error as e:
        print(f"Failed to create display ({SCREEN_WIDTH}x{SCREEN_HEIGHT}): {e}", 
              file=sys.stderr)
        pygame.quit()
        sys.exit(1)
    
    # Create clock for FPS management
    clock = pygame.time.Clock()
    
    # Initialize all components
    resource_manager = ResourceManager()
    camera = Camera()
    rendering_engine = RenderingEngine(screen, resource_manager, camera)
    
    # Load all PNG assets from assets directory
    try:
        print("Loading hospital assets...")
        resource_manager.load_assets_from_directory("assets")

        # Print loaded assets for debugging
        loaded_assets = resource_manager.get_loaded_assets()
        print(f"Available assets: {sorted(loaded_assets.keys())}")
        
    except (FileNotFoundError, pygame.error) as e:
        print(f"Failed to load assets: {e}", file=sys.stderr)
        pygame.quit()
        sys.exit(1)
    
    # Parse hospital maps and create entities
    try:
        print("Creating hospital layout...")
        hospital_entities = create_hospital_entities(resource_manager)
        rendering_engine.add_entities(hospital_entities)
        print(f"Hospital layout created with {len(hospital_entities)} entities")
        
    except (KeyError, RuntimeError) as e:
        print(f"Failed to create hospital layout: {e}", file=sys.stderr)
        pygame.quit()
        sys.exit(1)
    
    # ------------------------------------------------------------------ #
    # Camera + zoom state — initialised before the loop                  #
    # ------------------------------------------------------------------ #
    camera_x = SCREEN_WIDTH  // 2 - 320   # centre the 10×10 grid
    camera_y = SCREEN_HEIGHT // 2 - 240
    camera.set_offset(camera_x, camera_y)

    zoom_level     = 1.0    # 1.0 = normal size
    ZOOM_MIN       = 0.5    # scroll out limit
    ZOOM_MAX       = 2.5    # scroll in limit
    ZOOM_STEP      = 0.1    # change per wheel tick

    is_dragging    = False
    last_mouse_pos = (0, 0)

    # ------------------------------------------------------------------ #
    # HUD — state + UI renderers                                         #
    # ------------------------------------------------------------------ #
    state        = SimulationState()
    dashboard    = DashboardUI(SCREEN_WIDTH, SCREEN_HEIGHT)
    resource_hud = ResourceHUD(SCREEN_WIDTH)

    # ------------------------------------------------------------------ #
    # Simulation engine                                                   #
    # ------------------------------------------------------------------ #
    grid_index  = GridIndex(FLOOR_MAP, ENTITY_MAP)
    sim_manager = SimulationManager(state, grid_index)

    # Patch SimulationState.start_sim so the engine loads patients the
    # moment the user clicks START SIM — no other main.py changes needed.
    _original_start_sim = state.start_sim

    def _start_sim_with_engine() -> None:
        _original_start_sim()                          # generate patients + set flag
        sim_manager.reset(state)                       # rebuild rooms from state
        sim_manager.load_patients(state.patients)      # push patients into queue

    state.start_sim = _start_sim_with_engine           # type: ignore[method-assign]

    # Tick timer: fire one simulation tick every TICK_INTERVAL_MS ms
    TICK_INTERVAL_MS = 1000   # 1 tick per second
    TICK_EVENT       = pygame.USEREVENT + 1
    pygame.time.set_timer(TICK_EVENT, TICK_INTERVAL_MS)

    print("Starting hospital management game...")
    print("Left-drag to pan  |  Scroll wheel to zoom  |  ESC to quit")

    # ------------------------------------------------------------------ #
    # Main loop                                                           #
    # ------------------------------------------------------------------ #
    running = True
    while running:

        # --- Event handling ------------------------------------------- #
        for event in pygame.event.get():

            # Let the dashboard handle button clicks first
            dashboard.handle_event(event, state)

            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                else:
                    # Forward all other key events to the dashboard
                    # so the text input box can receive them.
                    dashboard.handle_event(event, state)

            # Simulation tick — fires every TICK_INTERVAL_MS
            elif event.type == TICK_EVENT:
                if state.sim_running:
                    sim_manager.tick()

            # Mouse wheel → zoom
            elif event.type == pygame.MOUSEWHEEL:
                zoom_level += event.y * ZOOM_STEP
                zoom_level  = max(ZOOM_MIN, min(ZOOM_MAX, zoom_level))

            # Left-button down → start drag (only if not clicking HUD elements)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    btn_hit   = (dashboard.start_button_rect is not None and
                                 dashboard.start_button_rect.collidepoint(event.pos))
                    input_hit = dashboard.input_rect.collidepoint(event.pos)
                    if not btn_hit and not input_hit:
                        is_dragging    = True
                        last_mouse_pos = event.pos

            # Left-button up → stop drag
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    is_dragging = False

            # Mouse motion → pan while dragging
            elif event.type == pygame.MOUSEMOTION:
                if is_dragging:
                    dx = event.pos[0] - last_mouse_pos[0]
                    dy = event.pos[1] - last_mouse_pos[1]
                    camera_x      += dx
                    camera_y      += dy
                    last_mouse_pos = event.pos
                    camera.set_offset(camera_x, camera_y)

        # --- Draw ----------------------------------------------------- #
        screen.fill((32, 32, 32))
        rendering_engine.render(zoom=zoom_level)   # static isometric scene

        # ── Dynamic patient sprites ───────────────────────────────────────
        # Blit a patient sprite for every live patient that has a grid_pos.
        # Uses the same zoom + camera + anchor math as the rendering engine.
        if state.sim_running:
            cam_x, cam_y = camera.get_offset()
            half_tw = IsometricConverter.TILE_WIDTH  * zoom_level / 2
            half_th = IsometricConverter.TILE_HEIGHT * zoom_level / 2
            patient_sprite = resource_manager.get_asset('char_male_patient_gown')
            orig_w, orig_h = patient_sprite.get_size()
            zoomed_w = max(1, int(orig_w * zoom_level))
            zoomed_h = max(1, int(orig_h * zoom_level))
            if zoom_level != 1.0:
                patient_sprite_z = pygame.transform.scale(
                    patient_sprite, (zoomed_w, zoomed_h))
            else:
                patient_sprite_z = patient_sprite

            for patient in sim_manager.get_visible_patients():
                row, col = patient.grid_pos
                raw_x, raw_y = IsometricConverter.grid_to_screen(row, col, 0, 0)
                iso_x = int(raw_x * zoom_level) + cam_x
                iso_y = int(raw_y * zoom_level) + cam_y
                blit_x = iso_x + int(half_tw) - zoomed_w // 2
                blit_y = iso_y - zoomed_h + int(half_th * 2)
                screen.blit(patient_sprite_z, (blit_x, blit_y))

        resource_hud.draw(screen, state)           # top-left static resources
        dashboard.draw(screen, state)              # bottom HUD floats on top
        pygame.display.flip()
        clock.tick(FPS)
    
    # Call pygame.quit() on exit
    print("Shutting down hospital management game...")
    pygame.quit()


if __name__ == "__main__":
    main()
