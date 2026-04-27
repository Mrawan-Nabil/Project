"""HUD overlay — two independent panels.

ResourceHUD   — small top-left panel showing static hospital resources.
DashboardUI   — glass-morphism bottom panel with input + live metrics.

Public API (main.py calls both):
    resource_hud = ResourceHUD(screen_width)
    dashboard    = DashboardUI(screen_width, screen_height)

    # inside event loop:
    dashboard.handle_event(event, state)

    # after rendering_engine.render():
    resource_hud.draw(screen, state)
    dashboard.draw(screen, state)
"""

from __future__ import annotations
from typing import TYPE_CHECKING

try:
    import pygame
except ImportError:
    import pygame_ce as pygame

if TYPE_CHECKING:
    from src.simulation_state import SimulationState

# ── Shared palette ────────────────────────────────────────────────────────────
_PANEL_BG      = (12,  22,  40,  215)
_BORDER_TOP    = (100, 140, 200,  180)
_DIVIDER       = (40,   58,  90,  160)
_HEADER        = (176, 196, 222)          # Light Steel Blue
_LABEL         = (255, 255, 255)
_VALUE         = (255, 255, 255)
_BTN_IDLE      = ( 34, 160,  74)
_BTN_HOVER     = ( 52, 199,  97)
_BTN_ACTIVE    = ( 20, 110,  50)
_BTN_TEXT      = (255, 255, 255)
_TRAFFIC_GREEN = (100, 220, 130)
_TRAFFIC_AMBER = (230, 175,  50)
_TRAFFIC_RED   = (220,  70,  70)


# =============================================================================
# ResourceHUD — top-left static resource panel
# =============================================================================

class ResourceHUD:
    """Small semi-transparent panel in the top-left corner.

    Displays the four static hospital resources that never change
    during a simulation run.
    """

    PAD   = 12
    ROW_H = 20
    W     = 190    # fixed panel width

    def __init__(self, screen_width: int) -> None:  # noqa: ARG002
        self._f_header = pygame.font.SysFont("Arial", 11, bold=True)
        self._f_label  = pygame.font.SysFont("Arial", 12, bold=False)
        self._f_value  = pygame.font.SysFont("Arial", 12, bold=True)

        # 5 rows: header + 5 resource lines (added Operating Rooms)
        rows   = 5
        height = self.PAD * 2 + self.ROW_H + rows * self.ROW_H + 4

        self._bg = pygame.Surface((self.W, height), pygame.SRCALPHA)
        self._bg.fill(_PANEL_BG)
        self._rect = pygame.Rect(10, 10, self.W, height)

    def draw(self, screen: pygame.Surface,
             state: "SimulationState") -> None:
        """Blit the resource panel onto *screen*."""
        screen.blit(self._bg, self._rect.topleft)

        # Border
        pygame.draw.rect(screen, _BORDER_TOP, self._rect, 1, border_radius=4)

        lx = self._rect.x + self.PAD
        rx = self._rect.right - self.PAD
        y  = self._rect.y + self.PAD

        # Header
        h_surf = self._f_header.render("HOSPITAL RESOURCES", True, _HEADER)
        screen.blit(h_surf, (lx, y))
        y += self.ROW_H + 4

        # Divider line under header
        pygame.draw.line(screen, _DIVIDER,
                         (lx, y - 2), (rx, y - 2), 1)

        rows = [
            ("Beds",             str(state.beds)),
            ("MRI Machines",     str(state.mris)),
            ("Doctors",          str(state.doctors)),
            ("ICU Bays",         str(state.icus)),
            ("Operating Rooms",  str(state.operating_rooms)),
        ]
        for label, value in rows:
            lbl = self._f_label.render(label, True, _LABEL)
            val = self._f_value.render(value, True, _VALUE)
            screen.blit(lbl, (lx, y))
            screen.blit(val, (rx - val.get_width(), y))
            y += self.ROW_H


# =============================================================================
# DashboardUI — bottom glass-morphism panel
# =============================================================================

class DashboardUI:
    """Renders the glass-morphism bottom HUD panel.

    Column layout (3 equal panes):
      Col 1 — PATIENT INPUT   : incoming_patients control only
      Col 2 — PATIENT BREAKDOWN: surgery / MRI / ICU / ward counts
      Col 3 — LIVE METRICS    : wait time, mortality, resource util
    """

    PANEL_HEIGHT_RATIO = 0.22
    PAD                = 20
    ROW_H              = 25
    BTN_W              = 200
    BTN_H              = 40

    def __init__(self, screen_width: int, screen_height: int) -> None:
        self.sw = screen_width
        self.sh = screen_height

        self.panel_h = int(screen_height * self.PANEL_HEIGHT_RATIO)
        self.panel_y = screen_height - self.panel_h

        self.col_w  = screen_width // 3
        self.col1_x = 0
        self.col2_x = self.col_w
        self.col3_x = self.col_w * 2

        self._bg = pygame.Surface((screen_width, self.panel_h), pygame.SRCALPHA)
        self._bg.fill(_PANEL_BG)

        self._f_header = pygame.font.SysFont("Arial", 12, bold=True)
        self._f_label  = pygame.font.SysFont("Arial", 13, bold=False)
        self._f_value  = pygame.font.SysFont("Arial", 13, bold=True)
        self._f_btn    = pygame.font.SysFont("Arial", 15, bold=True)

        self.start_button_rect: pygame.Rect | None = None

        # ── Text input state ──────────────────────────────────────────────
        # The input box sits to the right of the "Incoming Patients" label
        # inside column 1.  Its rect is calculated once here and reused
        # every frame so hit-testing is always accurate.
        self.input_text:   str          = "30"
        self.input_active: bool         = False
        self.input_rect:   pygame.Rect  = pygame.Rect(0, 0, 60, 22)
        # (x/y are set properly on first draw — see _draw_input_box)

    # ── Public API ────────────────────────────────────────────────────────

    def handle_event(self, event: pygame.event.Event,
                     state: "SimulationState") -> None:
        """Forward events here from the main event loop."""

        # ── Mouse click ───────────────────────────────────────────────────
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            # Focus / unfocus the input box
            self.input_active = self.input_rect.collidepoint(event.pos)

            # START / STOP button
            if (self.start_button_rect and
                    self.start_button_rect.collidepoint(event.pos)):
                if state.sim_running:
                    state.stop_sim()
                else:
                    # Sync input_text → state before generating patients
                    try:
                        state.set_incoming_patients(int(self.input_text or "0"))
                    except ValueError:
                        state.set_incoming_patients(0)
                    state.start_sim()

        # ── Keyboard input (only when the box is focused) ─────────────────
        elif event.type == pygame.KEYDOWN and self.input_active:
            if event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            elif event.unicode.isnumeric() and len(self.input_text) < 3:
                self.input_text += event.unicode

    def draw(self, screen: pygame.Surface,
             state: "SimulationState") -> None:
        """Blit the complete bottom HUD onto *screen*."""

        # ── Background + border ───────────────────────────────────────────
        screen.blit(self._bg, (0, self.panel_y))
        pygame.draw.line(screen, _BORDER_TOP,
                         (0, self.panel_y), (self.sw, self.panel_y), 2)

        for div_x in (self.col_w, self.col_w * 2):
            pygame.draw.line(screen, _DIVIDER,
                             (div_x, self.panel_y + 6),
                             (div_x, self.sh - 6), 1)

        content_y = self.panel_y + self.PAD

        # ── Col 1 — PATIENT INPUT ─────────────────────────────────────────
        self._header(screen, "PATIENT INPUT",
                     self.col1_x + self.PAD, content_y)

        self._draw_input_row(screen, content_y + self.ROW_H)

        # ── Col 2 — PATIENT BREAKDOWN ─────────────────────────────────────
        self._header(screen, "PATIENT BREAKDOWN",
                     self.col2_x + self.PAD, content_y)

        breakdown = [
            ("Total Generated",  str(state.total_patients),  _VALUE),
            ("Surgery Cases",    str(state.n_surgery),        _TRAFFIC_RED),
            ("MRI Needs",        str(state.n_mri),            _TRAFFIC_AMBER),
            ("ICU Cases",        str(state.n_icu),            _TRAFFIC_AMBER),
            ("Ward Admissions",  str(state.n_ward),           _TRAFFIC_GREEN),
        ]
        self._kv_coloured(screen, breakdown,
                          lx = self.col2_x + self.PAD,
                          rx = self.col3_x - self.PAD,
                          y  = content_y + self.ROW_H)

        # ── Col 3 — LIVE METRICS ──────────────────────────────────────────
        self._header(screen, "LIVE METRICS",
                     self.col3_x + self.PAD, content_y)

        wt_col   = self._tl(state.avg_wait_time,  lo=15, hi=45)
        mort_col = self._tl(state.mortality_risk, lo=5,  hi=20)
        util_col = self._tl(state.resource_util,  lo=60, hi=90, invert=True)

        metrics = [
            ("Avg Wait Time",   f"{state.avg_wait_time:.1f} min",  wt_col),
            ("Mortality Risk",  f"{state.mortality_risk:.1f} %",   mort_col),
            ("Resource Util",   f"{state.resource_util:.1f} %",    util_col),
            ("Surgeries Done",  str(state.surgeries_today),        _VALUE),
            ("MRI Scans Done",  str(state.mri_scans),              _VALUE),
        ]
        self._kv_coloured(screen, metrics,
                          lx = self.col3_x + self.PAD,
                          rx = self.sw - self.PAD,
                          y  = content_y + self.ROW_H)

        # ── Floating START / STOP button ──────────────────────────────────
        btn_rect = pygame.Rect(0, 0, self.BTN_W, self.BTN_H)
        btn_rect.center = (self.sw // 2,
                           self.panel_y - 20 - self.BTN_H // 2)
        self.start_button_rect = btn_rect

        mouse_pos = pygame.mouse.get_pos()
        if state.sim_running:
            btn_col, btn_label = _BTN_ACTIVE, "■  STOP SIM"
        elif btn_rect.collidepoint(mouse_pos):
            btn_col, btn_label = _BTN_HOVER,  "▶  START SIM"
        else:
            btn_col, btn_label = _BTN_IDLE,   "▶  START SIM"

        pygame.draw.rect(screen, btn_col, btn_rect, border_radius=10)
        btn_surf = self._f_btn.render(btn_label, True, _BTN_TEXT)
        screen.blit(btn_surf, btn_surf.get_rect(center=btn_rect.center))

        # ── Sim-running indicator dot ─────────────────────────────────────
        if state.sim_running:
            dot_x = self.sw - self.PAD
            dot_y = self.panel_y + self.PAD // 2 + 4
            pygame.draw.circle(screen, _TRAFFIC_GREEN, (dot_x, dot_y), 5)
            lbl = self._f_header.render("SIM RUNNING", True, _TRAFFIC_GREEN)
            screen.blit(lbl, (dot_x - lbl.get_width() - 10,
                               dot_y - lbl.get_height() // 2))

    # ── Private helpers ───────────────────────────────────────────────────

    def _draw_input_row(self, screen: pygame.Surface, y: int) -> None:
        """Draw the 'Incoming Patients' label + interactive text input box.

        Layout inside col 1:
          [Incoming Patients]  [  30 |]
          label left-aligned   box right-aligned to col boundary
        """
        lx = self.col1_x + self.PAD
        rx = self.col2_x - self.PAD

        # Label
        screen.blit(self._f_label.render("Incoming Patients", True, _LABEL),
                    (lx, y + 3))   # +3 to vertically centre with box

        # Position the input box flush-right inside col 1
        box_w = 60
        box_h = 22
        self.input_rect = pygame.Rect(rx - box_w, y, box_w, box_h)

        # Box fill — slightly lighter than panel when active
        box_bg = (30, 50, 80, 200) if self.input_active else (20, 35, 60, 180)
        box_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        box_surf.fill(box_bg)
        screen.blit(box_surf, self.input_rect.topleft)

        # Border — white when focused, grey when idle
        border_col = (255, 255, 255) if self.input_active else (100, 120, 150)
        pygame.draw.rect(screen, border_col, self.input_rect, 1, border_radius=3)

        # Text + blinking cursor when active
        display_text = self.input_text
        if self.input_active:
            # Simple cursor: always visible (blink can be added later)
            display_text += "|"
        txt_surf = self._f_value.render(display_text, True, _VALUE)
        # Clip text to box width with a small inner pad
        txt_x = self.input_rect.right - txt_surf.get_width() - 5
        txt_y = self.input_rect.y + (box_h - txt_surf.get_height()) // 2
        screen.blit(txt_surf, (txt_x, txt_y))

    def _header(self, screen: pygame.Surface,
                text: str, x: int, y: int) -> None:
        screen.blit(self._f_header.render(text, True, _HEADER), (x, y))

    def _kv(self, screen: pygame.Surface,
            label: str, value: str,
            lx: int, rx: int, y: int) -> None:
        """Single label-left / value-right row."""
        screen.blit(self._f_label.render(label, True, _LABEL), (lx, y))
        val_surf = self._f_value.render(value, True, _VALUE)
        screen.blit(val_surf, (rx - val_surf.get_width(), y))

    def _kv_coloured(self, screen: pygame.Surface,
                     rows: list,
                     lx: int, rx: int, y: int) -> None:
        """Multiple rows, each with its own value colour."""
        for label, value, vc in rows:
            screen.blit(self._f_label.render(label, True, _LABEL), (lx, y))
            val_surf = self._f_value.render(value, True, vc)
            screen.blit(val_surf, (rx - val_surf.get_width(), y))
            y += self.ROW_H

    @staticmethod
    def _tl(value: float, lo: float, hi: float,
            invert: bool = False) -> tuple:
        above_hi = value > hi
        above_lo = value > lo
        if not invert:
            if not above_lo: return _TRAFFIC_GREEN
            if not above_hi: return _TRAFFIC_AMBER
            return _TRAFFIC_RED
        else:
            if not above_lo: return _TRAFFIC_GREEN
            if not above_hi: return _TRAFFIC_AMBER
            return _TRAFFIC_RED
