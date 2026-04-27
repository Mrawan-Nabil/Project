"""Resource management for loading and caching image assets."""

from pathlib import Path
from typing import Dict, Tuple
try:
    import pygame
except ImportError:
    import pygame_ce as pygame


# =============================================================================
# CUSTOM SCALES — tune every entity's visual size here
# =============================================================================
#
# Each key is the asset filename stem (no extension, must match exactly what
# is in your assets/ folder).  The value is a float multiplier applied to the
# sprite's ORIGINAL pixel dimensions before it is stored.
#
#   1.0  → keep the sprite at its natural size after the base proportional
#           scale (width locked to TILE_WIDTH = 128 px).
#   > 1.0 → make the sprite LARGER  (e.g. 2.0 = double size)
#   < 1.0 → make the sprite SMALLER (e.g. 0.5 = half size)
#
# HOW TO TUNE:
#   1. Run the game and look at a sprite that is too big or too small.
#   2. Find its key below (it is the PNG filename without ".png").
#   3. Increase the number to make it bigger, decrease to make it smaller.
#   4. Save the file and re-run — no other code needs to change.
#
# ADDING A NEW SPRITE:
#   Just add a new line:  "your_new_asset": 1.0,
#   If a key is NOT listed here the sprite defaults to 1.0 (no extra scaling).
# =============================================================================
# =============================================================================
# CUSTOM SCALES — tune every entity's visual size here
# =============================================================================
CUSTOM_SCALES: Dict[str, float] = {
    # ── Characters ──────────────────────────────────────────────────────────
    # Bringing all humans down to 0.5 to match the tiny doctor.
    "char_male_doctor_white":          0.5,
    "char_female_staff_blue_scrubs":   0.5,
    "char_male_surgeon_green":         0.5,
    "char_female_surgeon_green":       0.5,
    "char_male_patient_gown":          0.5,
    "char_female_patient_gown":        0.5,
    "char_male_patient_casual":        0.5,
    "char_female_patient_casual":      0.5,
    "char_male_staff_blue_scrubs":     0.5,
    "char_female_staff_white_blue":    0.5,

    # ── Medical equipment ────────────────────────────────────────────────────
    # The MRI looks great at 1.0 next to the 0.5 doctor.
    "equip_mri_scanner":               1.0,
    # Shrinking the massive exam table.
    "equip_exam_table":                0.6,
    # The IV stand was towering; bringing it down to human height.
    "equip_iv_stand":                  0.2,
    # The monitor was the size of a car; scaling it down to a desktop size.
    "equip_medical_monitor":           0.25,
    # Overhead surgical light scaling down to fit a smaller room.
    "equip_surgical_light":            0.5,

    # ── Furniture ────────────────────────────────────────────────────────────
    # The desks and benches drop proportionally to match the 0.5 humans.
    "furn_reception_desk":             0.6,
    "furn_waiting_bench_orange":       0.5,
    "furn_lab_workbench":              0.6,

    # ── Doors ───────────────────────────────────────────────────────────────
    "door_window":                     0.6,
    "door_keypad":                     0.6,
}
# =============================================================================


class ResourceManager:
    """Manages loading and caching of image assets.

    Scaling pipeline (applied once at load time, stored in _assets):

    Floor tiles  → force-scaled to exactly (TILE_WIDTH × TILE_HEIGHT).
    Entities     → base scale locks width to TILE_WIDTH (aspect-ratio safe),
                   then the CUSTOM_SCALES multiplier is applied on top.
                   If the key is absent from CUSTOM_SCALES the multiplier is 1.0.
    """

    TILE_WIDTH:  int = 128
    TILE_HEIGHT: int = 64

    _FLOOR_KEYWORDS = ('floor', 'tile', 'ground')

    def __init__(self) -> None:
        self._assets: Dict[str, pygame.Surface] = {}
        self._cache:  Dict[str, pygame.Surface] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load_assets_from_directory(self, directory_path: str) -> None:
        """Scan *directory_path*, load every PNG, scale it, and cache it."""
        assets_dir = Path(directory_path)
        if not assets_dir.exists() or not assets_dir.is_dir():
            raise FileNotFoundError(f"Assets directory not found: {directory_path}")

        png_files = sorted(assets_dir.glob("*.png"))
        if not png_files:
            print(f"Warning: No PNG files found in {directory_path}")
            return

        print(f"Loading {len(png_files)} assets from '{directory_path}' …")

        for png_file in png_files:
            asset_key = png_file.stem
            try:
                raw    = pygame.image.load(str(png_file)).convert_alpha()
                scaled = self._scale(raw, asset_key)
                self._assets[asset_key] = scaled

                ow, oh = raw.get_size()
                nw, nh = scaled.get_size()
                kind   = "floor" if self._is_floor(asset_key) else "entity"
                mult   = CUSTOM_SCALES.get(asset_key, 1.0)
                print(f"  {asset_key}: {ow}×{oh} → {nw}×{nh}  [{kind}, ×{mult}]")

            except pygame.error as exc:
                raise pygame.error(f"Failed to load '{png_file.name}': {exc}") from exc

        print(f"Done — {len(self._assets)} assets ready.\n")

    def get_asset(self, asset_key: str) -> pygame.Surface:
        if asset_key not in self._assets:
            raise KeyError(
                f"Asset '{asset_key}' not found. Available: {sorted(self._assets)}"
            )
        return self._assets[asset_key]

    def has_asset(self, asset_key: str) -> bool:
        return asset_key in self._assets

    def get_loaded_assets(self) -> Dict[str, pygame.Surface]:
        return dict(self._assets)

    def load_image(self, path: str) -> pygame.Surface:
        """Load an arbitrary PNG by file path (legacy / test helper, no scaling)."""
        if path in self._cache:
            return self._cache[path]
        try:
            surface = pygame.image.load(path).convert_alpha()
            self._cache[path] = surface
            return surface
        except FileNotFoundError as exc:
            raise FileNotFoundError(f"Failed to load asset: {path} - File not found") from exc
        except pygame.error as exc:
            raise pygame.error(f"Failed to load asset: {path} - {exc}") from exc

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _is_floor(self, asset_key: str) -> bool:
        lower = asset_key.lower()
        return any(kw in lower for kw in self._FLOOR_KEYWORDS)

    def _scale(self, surface: pygame.Surface, asset_key: str) -> pygame.Surface:
        """Return a correctly scaled copy of *surface*.

        Floor tiles  → exact (TILE_WIDTH, TILE_HEIGHT).
        Entities     → proportional base scale (width = TILE_WIDTH) then
                       multiplied by CUSTOM_SCALES.get(asset_key, 1.0).
        """
        orig_w, orig_h = surface.get_size()

        if self._is_floor(asset_key):
            target: Tuple[int, int] = (self.TILE_WIDTH, self.TILE_HEIGHT)
        else:
            # Step 1 — base proportional scale: lock width to TILE_WIDTH
            base_scale = self.TILE_WIDTH / orig_w
            base_w = self.TILE_WIDTH
            base_h = orig_h * base_scale

            # Step 2 — apply the per-asset custom multiplier (default 1.0)
            mult  = CUSTOM_SCALES.get(asset_key, 1.0)
            new_w = max(1, int(base_w * mult))
            new_h = max(1, int(base_h * mult))
            target = (new_w, new_h)

        if surface.get_size() == target:
            return surface

        return pygame.transform.smoothscale(surface, target)
