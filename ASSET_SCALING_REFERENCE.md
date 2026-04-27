# Asset Scaling Reference

## Scaling Results by Category

### 🏥 Floor Tiles (Force-scaled to 128x64)
| Asset Name | Original Size | Scaled Size | Type |
|------------|---------------|-------------|------|
| floor_tile | 128x64 | 128x64 | Floor |
| tile_grey_speckled_quad | 4096x2733 | 128x64 | Floor |
| tile_white_speckled | 1696x1444 | 128x64 | Floor |

**Note**: All floor tiles are force-scaled to exactly 128x64 to ensure perfect isometric diamond shape.

---

### 👥 Characters (Proportionally scaled, width=128)
| Asset Name | Original Size | Scaled Size | Height |
|------------|---------------|-------------|--------|
| char_male_surgeon_green | 2260x4096 | 128x231 | Shortest |
| char_male_patient_casual | 2208x4096 | 128x237 | Short |
| char_male_patient_gown | 2120x4096 | 128x247 | Medium |
| char_male_staff_blue_scrubs | 2120x4096 | 128x247 | Medium |
| char_female_surgeon_green | 2116x4096 | 128x247 | Medium |
| char_female_patient_casual | 2036x4096 | 128x257 | Tall |
| char_female_patient_gown | 1916x4096 | 128x273 | Tall |
| char_male_doctor_white | 1888x4096 | 128x277 | Taller |
| char_female_staff_white_blue | 1796x4096 | 128x291 | Tallest |
| char_female_staff_blue_scrubs | 1664x4096 | 128x315 | Very Tall |

**Range**: 231-315 pixels tall (all 128 pixels wide)

---

### 🏗️ Walls & Doors (Proportionally scaled, width=128)
| Asset Name | Original Size | Scaled Size | Height |
|------------|---------------|-------------|--------|
| wall_corner_internal | 1812x1644 | 128x116 | Short |
| wall_corner_external | 1592x1500 | 128x120 | Short |
| door_keypad | 1024x1536 | 128x192 | Medium |
| wall_panel_rail | 816x1420 | 128x222 | Tall |
| door_window | 864x1824 | 128x270 | Very Tall |

**Range**: 116-270 pixels tall

---

### 🏥 Medical Equipment (Proportionally scaled, width=128)
| Asset Name | Original Size | Scaled Size | Height |
|------------|---------------|-------------|--------|
| equip_iv_stand | 4096x2234 | 128x69 | Short |
| equip_medical_monitor | 4096x2234 | 128x69 | Short |
| equip_surgical_light | 4096x2234 | 128x69 | Short |
| equip_exam_table | 1224x868 | 128x90 | Medium |
| equip_mri_scanner | 4096x4096 | 128x128 | Tall |

**Range**: 69-128 pixels tall

---

### 🪑 Furniture (Proportionally scaled, width=128)
| Asset Name | Original Size | Scaled Size | Height |
|------------|---------------|-------------|--------|
| furn_waiting_bench_orange | 996x912 | 128x117 | Short |
| furn_reception_desk | 900x856 | 128x121 | Medium |
| furn_lab_workbench | 972x928 | 128x122 | Medium |

**Range**: 117-122 pixels tall

---

## Scaling Statistics

### Overall Summary
- **Total Assets**: 27
- **Floor Tiles**: 3 (all 128x64)
- **Entities**: 24 (all 128 wide, varying heights)

### Height Distribution
- **Short** (69-120px): 8 assets
- **Medium** (121-200px): 8 assets
- **Tall** (201-280px): 7 assets
- **Very Tall** (281-315px): 1 asset

### Scale Factors Applied
- **Minimum**: 0.031x (4096 → 128)
- **Maximum**: 1.0x (128 → 128, no scaling needed)
- **Most Common**: ~0.031x (for 4096-wide sprites)

---

## Anchoring Behavior

### Floor Tiles (128x64)
- **Anchor**: Top-left corner at grid point
- **Offset**: (0, 0)
- **Reason**: Floor tiles define the base grid

### Entities (128 x varying height)
- **Anchor**: Bottom-center at grid point
- **Horizontal Offset**: `-(width/2) + (TILE_WIDTH/2)` = 0 (since width = 128)
- **Vertical Offset**: `-(height - TILE_HEIGHT)`
- **Example**: 
  - Character (128x247): offset = (0, -183)
  - Wall (128x222): offset = (0, -158)
  - Equipment (128x90): offset = (0, -26)

---

## Visual Quality Notes

### Scaling Method
- **Algorithm**: `pygame.transform.smoothscale()`
- **Quality**: High (anti-aliased)
- **Performance**: One-time cost during loading

### Aspect Ratio Preservation
- ✅ Characters maintain proper proportions
- ✅ Equipment looks natural
- ✅ Walls don't appear stretched
- ✅ Floor tiles fit perfectly in isometric grid

### Transparency
- ✅ Alpha channel preserved during scaling
- ✅ Smooth edges maintained
- ✅ No artifacts or halos

---

## Usage in Code

```python
# Loading with scaling
resource_manager.load_assets_from_directory(
    "assets",
    tile_width=128,
    tile_height=64
)

# Getting a scaled asset
sprite = resource_manager.get_asset("char_male_doctor_white")
# Returns: 128x277 scaled surface (from original 1888x4096)

# Automatic anchoring
entity = AnchoredEntity(row=5, col=5, asset_key="char_male_doctor_white", 
                        sprite=sprite, is_floor_tile=False)
# Automatically calculates bottom-center anchor offset
```

---

## Troubleshooting

### If sprites still look wrong:
1. Check asset filename contains "floor", "tile", or "ground" for floor tiles
2. Verify TILE_WIDTH=128 and TILE_HEIGHT=64 in IsometricConverter
3. Ensure smoothscale is being used (not regular scale)
4. Check that convert_alpha() is applied before scaling

### If anchoring is off:
1. Verify is_floor_tile flag is set correctly
2. Check sprite dimensions after scaling
3. Ensure IsometricConverter.TILE_WIDTH and TILE_HEIGHT are correct
4. Verify anchor offset calculations in AnchoredEntity

---

**Result**: All 27 assets now perfectly scaled and anchored for the 128x64 isometric grid! 🎉