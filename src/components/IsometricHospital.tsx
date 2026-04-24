"use client";

import { useEffect, useRef } from "react";
import { Application, Graphics, Container, Text, TextStyle } from "pixi.js";
import { Patient } from "@/lib/algorithms";

const TILE_W = 72;
const TILE_H = 36;

function isoX(col: number, row: number) { return (col - row) * (TILE_W / 2); }
function isoY(col: number, row: number) { return (col + row) * (TILE_H / 2); }

function darken(color: number, amount: number): number {
  const r = Math.max(0, ((color >> 16) & 0xff) * (1 - amount));
  const g = Math.max(0, ((color >> 8) & 0xff) * (1 - amount));
  const b = Math.max(0, (color & 0xff) * (1 - amount));
  return (Math.round(r) << 16) | (Math.round(g) << 8) | Math.round(b);
}
function lighten(color: number, amount: number): number {
  const r = Math.min(255, ((color >> 16) & 0xff) + 255 * amount);
  const g = Math.min(255, ((color >> 8) & 0xff) + 255 * amount);
  const b = Math.min(255, (color & 0xff) + 255 * amount);
  return (Math.round(r) << 16) | (Math.round(g) << 8) | Math.round(b);
}

// ─── Tile drawing ────────────────────────────────────────────────────────────
function drawTile(gfx: Graphics, col: number, row: number, floorColor: number, wallColor: number, wallHeight = 14) {
  const x = isoX(col, row);
  const y = isoY(col, row);
  const hw = TILE_W / 2, hh = TILE_H / 2;

  // Left face
  gfx.beginPath();
  gfx.moveTo(x, y + hh); gfx.lineTo(x, y + hh + wallHeight);
  gfx.lineTo(x + hw, y + TILE_H + wallHeight); gfx.lineTo(x + hw, y + TILE_H);
  gfx.closePath(); gfx.fill({ color: darken(wallColor, 0.18) });

  // Right face
  gfx.beginPath();
  gfx.moveTo(x + hw, y + TILE_H); gfx.lineTo(x + hw, y + TILE_H + wallHeight);
  gfx.lineTo(x + TILE_W, y + hh + wallHeight); gfx.lineTo(x + TILE_W, y + hh);
  gfx.closePath(); gfx.fill({ color: darken(wallColor, 0.32) });

  // Top face
  gfx.beginPath();
  gfx.moveTo(x, y + hh); gfx.lineTo(x + hw, y);
  gfx.lineTo(x + TILE_W, y + hh); gfx.lineTo(x + hw, y + TILE_H);
  gfx.closePath(); gfx.fill({ color: floorColor });
  gfx.stroke({ color: 0x334155, width: 0.4, alpha: 0.25 });
}

// ─── Isometric box (furniture base) ─────────────────────────────────────────
function drawIsoBox(
  gfx: Graphics,
  col: number, row: number,
  w: number, d: number, h: number,   // width, depth, height in pixels
  topColor: number,
  offsetX = 0, offsetY = 0
) {
  const bx = isoX(col, row) + TILE_W / 2 + offsetX;
  const by = isoY(col, row) + TILE_H / 2 + offsetY;
  const hw = w / 2, hd = d / 4;

  // Left face
  gfx.beginPath();
  gfx.moveTo(bx - hw, by + hd);
  gfx.lineTo(bx - hw, by + hd + h);
  gfx.lineTo(bx, by + hd * 2 + h);
  gfx.lineTo(bx, by + hd * 2);
  gfx.closePath(); gfx.fill({ color: darken(topColor, 0.25) });

  // Right face
  gfx.beginPath();
  gfx.moveTo(bx, by + hd * 2);
  gfx.lineTo(bx, by + hd * 2 + h);
  gfx.lineTo(bx + hw, by + hd + h);
  gfx.lineTo(bx + hw, by + hd);
  gfx.closePath(); gfx.fill({ color: darken(topColor, 0.4) });

  // Top face
  gfx.beginPath();
  gfx.moveTo(bx - hw, by + hd);
  gfx.lineTo(bx, by);
  gfx.lineTo(bx + hw, by + hd);
  gfx.lineTo(bx, by + hd * 2);
  gfx.closePath(); gfx.fill({ color: topColor });
  gfx.stroke({ color: 0x1e293b, width: 0.8, alpha: 0.4 });
}

// ─── Furniture drawers ───────────────────────────────────────────────────────

function drawBed(gfx: Graphics, col: number, row: number, color = 0x93c5fd) {
  // Frame
  drawIsoBox(gfx, col, row, 38, 22, 10, 0xd4a574, -2, -4);
  // Mattress
  drawIsoBox(gfx, col, row, 32, 18, 8, lighten(color, 0.2), -2, -10);
  // Pillow
  drawIsoBox(gfx, col, row, 14, 10, 5, 0xffffff, -12, -16);
  // Blanket fold
  drawIsoBox(gfx, col, row, 20, 12, 4, color, 4, -12);
}

function drawDesk(gfx: Graphics, col: number, row: number, color = 0xd4a574) {
  // Desk surface
  drawIsoBox(gfx, col, row, 40, 22, 8, color, 0, -2);
  // Monitor base
  drawIsoBox(gfx, col, row, 6, 4, 10, 0x475569, -8, -14);
  // Monitor screen
  drawIsoBox(gfx, col, row, 20, 3, 16, 0x1e293b, -8, -22);
  // Screen glow
  drawIsoBox(gfx, col, row, 16, 2, 12, 0x38bdf8, -8, -22);
  // Keyboard
  drawIsoBox(gfx, col, row, 22, 10, 3, 0x64748b, 4, -10);
}

function drawMRIMachine(gfx: Graphics, col: number, row: number) {
  // Main body
  drawIsoBox(gfx, col, row, 52, 30, 28, 0xe2e8f0, 0, -8);
  // Tunnel opening
  const bx = isoX(col, row) + TILE_W / 2;
  const by = isoY(col, row) + TILE_H / 2 - 20;
  gfx.ellipse(bx, by, 12, 8);
  gfx.fill({ color: 0x0f172a });
  gfx.ellipse(bx, by, 9, 6);
  gfx.fill({ color: 0x1e3a5f });
  // Control panel
  drawIsoBox(gfx, col, row, 18, 12, 10, 0x475569, 20, -4);
  drawIsoBox(gfx, col, row, 14, 8, 4, 0x38bdf8, 20, -12);
  // Patient table
  drawIsoBox(gfx, col, row, 44, 12, 6, 0xf1f5f9, 0, 4);
}

function drawOperatingTable(gfx: Graphics, col: number, row: number) {
  // Table legs
  drawIsoBox(gfx, col, row, 6, 4, 18, 0x94a3b8, -16, 2);
  drawIsoBox(gfx, col, row, 6, 4, 18, 0x94a3b8, 10, 2);
  // Table surface
  drawIsoBox(gfx, col, row, 44, 20, 6, 0xe2e8f0, 0, -14);
  // Green sheet
  drawIsoBox(gfx, col, row, 38, 16, 4, 0x6ee7b7, 0, -18);
  // Overhead lamp arm
  drawIsoBox(gfx, col, row, 4, 4, 30, 0x64748b, 0, -40);
  // Lamp head
  drawIsoBox(gfx, col, row, 20, 12, 6, 0xfef08a, 0, -46);
  gfx.circle(isoX(col, row) + TILE_W / 2, isoY(col, row) + TILE_H / 2 - 50, 5);
  gfx.fill({ color: 0xffffff, alpha: 0.9 });
}

function drawPharmacyShelf(gfx: Graphics, col: number, row: number) {
  // Shelf unit
  drawIsoBox(gfx, col, row, 44, 14, 32, 0xd4a574, 0, -8);
  // Shelf dividers
  drawIsoBox(gfx, col, row, 42, 12, 2, 0xb8864e, 0, -18);
  drawIsoBox(gfx, col, row, 42, 12, 2, 0xb8864e, 0, -28);
  // Medicine bottles (row 1)
  const colors = [0xef4444, 0x3b82f6, 0x22c55e, 0xf59e0b, 0xa855f7];
  for (let i = 0; i < 5; i++) {
    drawIsoBox(gfx, col, row, 6, 5, 8, colors[i], -16 + i * 8, -24);
  }
  // Medicine bottles (row 2)
  for (let i = 0; i < 4; i++) {
    drawIsoBox(gfx, col, row, 6, 5, 10, colors[(i + 2) % 5], -12 + i * 8, -36);
  }
}

function drawMicroscope(gfx: Graphics, col: number, row: number) {
  // Lab bench
  drawIsoBox(gfx, col, row, 44, 22, 8, 0xd4a574, 0, -2);
  // Microscope base
  drawIsoBox(gfx, col, row, 14, 10, 4, 0x334155, -8, -10);
  // Arm
  drawIsoBox(gfx, col, row, 4, 4, 22, 0x475569, -8, -28);
  // Head
  drawIsoBox(gfx, col, row, 12, 8, 6, 0x334155, -8, -32);
  // Eyepiece
  drawIsoBox(gfx, col, row, 4, 4, 10, 0x1e293b, -8, -40);
  // Sample slide (glowing)
  drawIsoBox(gfx, col, row, 10, 6, 2, 0x7dd3fc, -8, -12);
  // Test tubes rack
  drawIsoBox(gfx, col, row, 20, 10, 6, 0x94a3b8, 10, -8);
  const tubeColors = [0xef4444, 0xfbbf24, 0x34d399];
  for (let i = 0; i < 3; i++) {
    drawIsoBox(gfx, col, row, 4, 4, 12, tubeColors[i], 12 + i * 6, -14);
  }
}

function drawWaitingChair(gfx: Graphics, col: number, row: number, color = 0xf97316) {
  // Seat
  drawIsoBox(gfx, col, row, 18, 14, 6, color, 0, 0);
  // Back
  drawIsoBox(gfx, col, row, 18, 4, 14, darken(color, 0.15), 0, -14);
  // Legs
  drawIsoBox(gfx, col, row, 3, 3, 8, 0x64748b, -6, 4);
  drawIsoBox(gfx, col, row, 3, 3, 8, 0x64748b, 4, 4);
}

function drawPlant(gfx: Graphics, col: number, row: number) {
  // Pot
  drawIsoBox(gfx, col, row, 14, 10, 12, 0xb45309, 0, 0);
  // Soil
  drawIsoBox(gfx, col, row, 12, 8, 2, 0x78350f, 0, -10);
  // Leaves
  const bx = isoX(col, row) + TILE_W / 2;
  const by = isoY(col, row) + TILE_H / 2 - 18;
  gfx.circle(bx, by - 8, 12); gfx.fill({ color: 0x16a34a });
  gfx.circle(bx - 8, by - 4, 9); gfx.fill({ color: 0x15803d });
  gfx.circle(bx + 8, by - 4, 9); gfx.fill({ color: 0x22c55e });
  gfx.circle(bx, by - 14, 8); gfx.fill({ color: 0x4ade80 });
}

function drawWaterCooler(gfx: Graphics, col: number, row: number) {
  // Base
  drawIsoBox(gfx, col, row, 14, 10, 20, 0xe2e8f0, 0, -4);
  // Water bottle (blue)
  drawIsoBox(gfx, col, row, 10, 8, 14, 0x7dd3fc, 0, -22);
  // Tap
  drawIsoBox(gfx, col, row, 6, 4, 4, 0x3b82f6, -2, -8);
}

function drawIVStand(gfx: Graphics, col: number, row: number) {
  // Pole
  drawIsoBox(gfx, col, row, 3, 3, 36, 0x94a3b8, 0, -10);
  // Bag
  drawIsoBox(gfx, col, row, 10, 6, 14, 0xbae6fd, 0, -44);
  // Tube
  const bx = isoX(col, row) + TILE_W / 2;
  const by = isoY(col, row) + TILE_H / 2 - 32;
  gfx.moveTo(bx, by); gfx.lineTo(bx + 6, by + 16);
  gfx.stroke({ color: 0x7dd3fc, width: 1.5 });
}

// ─── Room definitions ────────────────────────────────────────────────────────
const ROOMS = [
  { id: "Triage",     col: 1,  row: 1,  w: 6, h: 5, floor: 0xbfdbfe, wall: 0x93c5fd, label: "TRIAGE",     emoji: "📋" },
  { id: "MRI",        col: 9,  row: 1,  w: 6, h: 5, floor: 0xe9d5ff, wall: 0xc4b5fd, label: "MRI",         emoji: "🧲" },
  { id: "WARD",       col: 1,  row: 8,  w: 6, h: 5, floor: 0xa7f3d0, wall: 0x6ee7b7, label: "WARD",        emoji: "🛏️" },
  { id: "ICU",        col: 8,  row: 8,  w: 6, h: 5, floor: 0xfecdd3, wall: 0xfca5a5, label: "ICU",         emoji: "🩺" },
  { id: "OPS_ROOM",   col: 15, row: 8,  w: 6, h: 5, floor: 0xf0fdf4, wall: 0x86efac, label: "OPS ROOM",   emoji: "🔪" },
  { id: "Pharmacy",   col: 1,  row: 15, w: 6, h: 5, floor: 0xfef9c3, wall: 0xfcd34d, label: "PHARMACY",   emoji: "💊" },
  { id: "Laboratory", col: 9,  row: 15, w: 6, h: 5, floor: 0xc7d2fe, wall: 0xa5b4fc, label: "LABORATORY", emoji: "🔬" },
];

function getRoomCenter(roomId: string): { col: number; row: number } {
  const room = ROOMS.find((r) => r.id === roomId);
  if (!room) return { col: 11, row: 7 };
  return { col: room.col + Math.floor(room.w / 2), row: room.row + Math.floor(room.h / 2) };
}

// ─── Main component ──────────────────────────────────────────────────────────
interface Props { patients: Patient[]; isDark: boolean; }

export default function IsometricHospital({ patients, isDark }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const appRef       = useRef<Application | null>(null);
  const patientRef   = useRef<Map<string, Container>>(new Map());

  useEffect(() => {
    if (!containerRef.current) return;
    const el = containerRef.current;
    const app = new Application();
    appRef.current = app;

    app.init({
      resizeTo: el,
      backgroundColor: isDark ? 0x0f172a : 0xf0fdf4,
      antialias: true,
      resolution: window.devicePixelRatio || 1,
      autoDensity: true,
    }).then(() => {
      if (!el.contains(app.canvas)) el.appendChild(app.canvas);

      const W = app.screen.width;
      const H = app.screen.height;

      const world = new Container();
      world.x = W / 2;
      world.y = H * 0.08;
      app.stage.addChild(world);

      const checkerA = isDark ? 0x1e293b : 0xdbeafe;
      const checkerB = isDark ? 0x263348 : 0xe0f2fe;
      const wallC    = isDark ? 0x334155 : 0x93c5fd;

      // ── Ground ──
      const ground = new Graphics();
      world.addChild(ground);
      for (let r = 0; r < 22; r++) {
        for (let c = 0; c < 23; c++) {
          drawTile(ground, c, r, (r + c) % 2 === 0 ? checkerA : checkerB, wallC, 5);
        }
      }

      // ── Rooms ──
      for (const room of ROOMS) {
        const rg = new Graphics();
        world.addChild(rg);
        for (let dr = 0; dr < room.h; dr++) {
          for (let dc = 0; dc < room.w; dc++) {
            const c = room.col + dc, r = room.row + dr;
            const isEdge = dr === 0 || dc === 0 || dr === room.h - 1 || dc === room.w - 1;
            drawTile(rg, c, r, room.floor, isEdge ? room.wall : lighten(room.floor, 0.04), isEdge ? 32 : 8);
          }
        }
      }

      // ── Furniture layer ──
      const furn = new Graphics();
      world.addChild(furn);

      // Triage: desk + chairs + plant + water cooler
      drawDesk(furn, 2, 2);
      drawWaitingChair(furn, 4, 2, 0xf97316);
      drawWaitingChair(furn, 4, 3, 0xf97316);
      drawWaitingChair(furn, 5, 3, 0xf97316);
      drawPlant(furn, 2, 4);
      drawWaterCooler(furn, 5, 2);

      // MRI: machine + control desk
      drawMRIMachine(furn, 11, 2);
      drawDesk(furn, 10, 4);

      // Ward: beds + IV stands
      drawBed(furn, 2, 9, 0x93c5fd);
      drawBed(furn, 3, 10, 0x93c5fd);
      drawIVStand(furn, 2, 10);
      drawIVStand(furn, 3, 11);
      drawPlant(furn, 5, 9);

      // ICU: beds + IV stands + monitor
      drawBed(furn, 9, 9, 0xfca5a5);
      drawBed(furn, 10, 10, 0xfca5a5);
      drawIVStand(furn, 9, 10);
      drawIVStand(furn, 10, 11);
      drawDesk(furn, 12, 9);

      // OPS Room: operating table + lamp
      drawOperatingTable(furn, 18, 10);
      drawDesk(furn, 16, 9);

      // Pharmacy: shelves + desk
      drawPharmacyShelf(furn, 2, 16);
      drawPharmacyShelf(furn, 3, 17);
      drawDesk(furn, 5, 16);
      drawWaterCooler(furn, 5, 17);

      // Laboratory: microscope + bench
      drawMicroscope(furn, 10, 16);
      drawMicroscope(furn, 11, 17);
      drawPlant(furn, 13, 16);

      // Corridor chairs + plants
      drawWaitingChair(furn, 7, 6, 0xf97316);
      drawWaitingChair(furn, 8, 6, 0xf97316);
      drawWaitingChair(furn, 13, 6, 0xf97316);
      drawWaitingChair(furn, 14, 6, 0xf97316);
      drawPlant(furn, 7, 13);
      drawPlant(furn, 15, 13);
      drawWaterCooler(furn, 11, 6);

      // ── Room labels ──
      for (const room of ROOMS) {
        const cx = room.col + room.w / 2;
        const cy = room.row + room.h / 2;
        const style = new TextStyle({
          fontFamily: "Arial Black, Arial",
          fontSize: 12,
          fontWeight: "900",
          fill: isDark ? 0xffffff : 0x1e293b,
          align: "center",
          dropShadow: { color: isDark ? 0x000000 : 0xffffff, blur: 4, distance: 1, alpha: 0.8 },
        });
        const lbl = new Text({ text: `${room.emoji} ${room.label}`, style });
        lbl.anchor.set(0.5, 0.5);
        lbl.x = isoX(cx, cy) + TILE_W / 2;
        lbl.y = isoY(cx, cy) - 2;
        world.addChild(lbl);
      }

      // ── Patient layer ──
      const patientLayer = new Container();
      world.addChild(patientLayer);
      patientRef.current = new Map();

      // smooth animation ticker
      app.ticker.add(() => {
        for (const [, sprite] of patientRef.current) {
          const tx = (sprite as Container & { _tx?: number })._tx ?? sprite.x;
          const ty = (sprite as Container & { _ty?: number })._ty ?? sprite.y;
          sprite.x += (tx - sprite.x) * 0.1;
          sprite.y += (ty - sprite.y) * 0.1;
        }
      });
    });

    return () => { app.destroy(true, { children: true }); appRef.current = null; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isDark]);

  // ── Update patients ──
  useEffect(() => {
    const app = appRef.current;
    if (!app?.stage) return;
    const world = app.stage.children[0] as Container;
    if (!world) return;
    const patientLayer = world.children[world.children.length - 1] as Container;
    if (!patientLayer) return;

    const existing = patientRef.current;
    const currentIds = new Set(patients.map((p) => p.id));

    for (const [id, sprite] of existing) {
      if (!currentIds.has(id)) { patientLayer.removeChild(sprite); existing.delete(id); }
    }

    for (const patient of patients) {
      const { col, row } = getRoomCenter(patient.currentZone);
      let hash = 0;
      for (let i = 0; i < patient.id.length; i++) hash = patient.id.charCodeAt(i) + ((hash << 5) - hash);
      const sc = col + ((hash % 5) - 2) * 0.5;
      const sr = row + (((hash >> 4) % 5) - 2) * 0.5;
      const tx = isoX(sc, sr) + TILE_W / 2;
      const ty = isoY(sc, sr) + TILE_H / 2 - 10;

      const color = patient.severity >= 8 ? 0xef4444 : patient.severity >= 4 ? 0xf97316 : 0x22c55e;

      if (!existing.has(patient.id)) {
        const c = new Container() as Container & { _tx?: number; _ty?: number };
        // Shadow
        const shadow = new Graphics();
        shadow.ellipse(0, 4, 9, 4); shadow.fill({ color: 0x000000, alpha: 0.25 });
        // Body circle
        const circle = new Graphics();
        circle.circle(0, 0, 10); circle.fill({ color });
        circle.circle(0, 0, 10); circle.stroke({ color: 0xffffff, width: 2 });
        // Inner highlight
        const shine = new Graphics();
        shine.circle(-3, -3, 4); shine.fill({ color: 0xffffff, alpha: 0.35 });
        // Severity number
        const num = new Text({ text: String(patient.severity), style: new TextStyle({ fontFamily: "Arial", fontSize: 10, fontWeight: "bold", fill: 0xffffff }) });
        num.anchor.set(0.5, 0.5);
        c.addChild(shadow); c.addChild(circle); c.addChild(shine); c.addChild(num);
        c._tx = tx; c._ty = ty;
        c.x = tx; c.y = ty;
        patientLayer.addChild(c);
        existing.set(patient.id, c);
      } else {
        const c = existing.get(patient.id) as Container & { _tx?: number; _ty?: number };
        c._tx = tx; c._ty = ty;
      }
    }
  }, [patients]);

  return <div ref={containerRef} className="w-full h-full" />;
}
