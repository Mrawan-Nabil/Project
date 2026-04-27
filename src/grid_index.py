"""GridIndex — spatial index of the FLOOR_MAP.

Provides two services:
  1. Zone tile pools  — lists of (row, col) for every floor zone value.
  2. Occupancy tracking — marks tiles as taken/free so two patients
     never share the same cell.

No Pygame, no rendering.  Pure data structure.

Treatment → zone mapping
------------------------
Patients spawn in the Entrance (2) / Triage (3) waiting area.
When allocated to a room, they move to a tile inside that room's zone:

    'Ward'    → zone 4  (mint green)
    'ICU'     → zone 5  (pink)
    'MRI'     → zone 7  (lavender)
    'Surgery' → zone 8  (white — rows 0-3 and 10-13)
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple

# Zone IDs that correspond to each treatment type
TREATMENT_ZONE: Dict[str, int] = {
    'Ward':    4,
    'ICU':     5,
    'MRI':     7,
    'Surgery': 8,
}

# Zones used as the initial waiting / spawn area
SPAWN_ZONES = {2, 3}   # Entrance (yellow) + Triage (light blue)


class GridIndex:
    """Builds and maintains a spatial index over the FLOOR_MAP.

    Parameters
    ----------
    floor_map : list[list[int]]
        The FLOOR_MAP from map_data.py.
    entity_map : list[list]
        The ENTITY_MAP from map_data.py — used to avoid spawning patients
        on top of static furniture / staff.

    Usage
    -----
    idx = GridIndex(FLOOR_MAP, ENTITY_MAP)
    pos = idx.claim_spawn_tile()          # get a free waiting-area tile
    pos = idx.claim_zone_tile('Surgery')  # get a free surgery tile
    idx.release_tile(pos)                 # free a tile when patient leaves
    """

    def __init__(self, floor_map: List[List], entity_map: List[List]) -> None:
        self._floor_map  = floor_map
        self._entity_map = entity_map

        # occupied: set of (row, col) currently claimed by a live patient
        self._occupied: set[Tuple[int, int]] = set()

        # Pre-build zone pools: zone_id → list of (row, col)
        # Only include cells that are empty in the ENTITY_MAP (no furniture)
        self._zone_pools: Dict[int, List[Tuple[int, int]]] = {}
        self._build_pools()

    # ── Setup ─────────────────────────────────────────────────────────────────

    def _build_pools(self) -> None:
        """Scan FLOOR_MAP and collect free tiles per zone."""
        rows = len(self._floor_map)
        cols = len(self._floor_map[0]) if rows else 0

        for r in range(rows):
            for c in range(cols):
                zone = self._floor_map[r][c]
                if zone == 0:
                    continue   # void — skip

                # Only include tiles that have no static entity on them
                entity_cell = self._entity_map[r][c]
                if entity_cell != 0 and entity_cell != ' ':
                    continue   # occupied by furniture / staff

                if zone not in self._zone_pools:
                    self._zone_pools[zone] = []
                self._zone_pools[zone].append((r, c))

    # ── Public API ────────────────────────────────────────────────────────────

    def claim_spawn_tile(self) -> Optional[Tuple[int, int]]:
        """Return and claim a free tile in the spawn zones (Entrance/Triage).

        Tries zone 2 (Entrance) first, then zone 3 (Triage).
        Returns None if both zones are full.
        """
        for zone_id in (2, 3):
            tile = self._claim_from_zone(zone_id)
            if tile is not None:
                return tile
        return None

    def claim_zone_tile(self, treatment: str) -> Optional[Tuple[int, int]]:
        """Return and claim a free tile in the zone for *treatment*.

        Returns None if the zone is full or unknown.
        """
        zone_id = TREATMENT_ZONE.get(treatment)
        if zone_id is None:
            return None
        return self._claim_from_zone(zone_id)

    def release_tile(self, pos: Optional[Tuple[int, int]]) -> None:
        """Free a previously claimed tile."""
        if pos is not None:
            self._occupied.discard(pos)

    def is_occupied(self, pos: Tuple[int, int]) -> bool:
        return pos in self._occupied

    # ── Private helpers ───────────────────────────────────────────────────────

    def _claim_from_zone(self, zone_id: int) -> Optional[Tuple[int, int]]:
        """Find the first unoccupied tile in *zone_id* and claim it."""
        pool = self._zone_pools.get(zone_id, [])
        for tile in pool:
            if tile not in self._occupied:
                self._occupied.add(tile)
                return tile
        return None

    def reset(self) -> None:
        """Release all claimed tiles (call on sim reset)."""
        self._occupied.clear()

    def __repr__(self) -> str:
        return (f"GridIndex(zones={list(self._zone_pools.keys())}, "
                f"occupied={len(self._occupied)})")
