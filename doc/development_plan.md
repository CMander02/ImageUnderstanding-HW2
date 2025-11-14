# Cylindrical Panorama - Development Plan

## Project Overview

**Deadline:** November 15, 2025
**Objective:** Implement a cylindrical panorama stitching system using SIFT features and RANSAC alignment.

---

## Project Pipeline (8 Steps)

### 1. Image Acquisition
- **Status:** TBD
- **Options:**
  - Use pre-captured images from course website
  - Use custom images (self-captured)
- **Questions:**
  - Which image set should we use?
  - Do we need to support multiple image sets for testing?

### 2. Cylindrical Warping
- **Status:** Not Started
- **Key Tasks:**
  - Implement backward warping algorithm
  - Handle focal length estimation
  - Apply transformation: (x,y) → (θ, h) → (x̂, ŷ, ẑ) → (x', y')
- **Questions:**
  - Should focal length be configurable or auto-estimated?
  - Do we need to support both cylindrical and spherical projections?
  - How to handle edge cases (image boundaries)?

### 3. Feature Extraction
- **Status:** Not Started
- **Algorithm:** SIFT (Scale-Invariant Feature Transform)
- **Key Tasks:**
  - Extract SIFT keypoints and descriptors from warped images
  - Visualize detected features (optional, for debugging)
- **Questions:**
  - How many features should we extract per image? (default: adaptive or fixed number?)
  - Do we need feature visualization for the report?

### 4. Feature Matching & RANSAC Alignment
- **Status:** Not Started
- **Key Tasks:**
  - Match features between neighboring image pairs
  - Apply RANSAC to find robust translation parameters
  - Filter out outliers
- **Questions:**
  - What RANSAC parameters should we use? (iterations, threshold, inlier ratio?)
  - Should we only match adjacent pairs or try all pairs?
  - Do we need to save matching visualizations for the report?

### 5. Translation List Generation
- **Status:** Not Started
- **Key Tasks:**
  - Compute and store pairwise translations
  - Save translation list to file (format TBD)
- **Questions:**
  - What file format for translations? (JSON, CSV, pickle?)
  - Should translations be cumulative or pairwise?

### 6. Drift Correction
- **Status:** Not Started
- **Key Tasks:**
  - Match first and last images
  - Compute gap angle θ_g
  - Distribute correction evenly across sequence
  - Update focal length: f' = f(1 - θ_g/2π)
- **Questions:**
  - Is drift correction required for all datasets or only 360° panoramas?
  - How to handle cases where first and last images don't overlap?

### 7. Image Blending
- **Status:** Not Started
- **Key Tasks:**
  - Read warped images
  - Composite images using computed translations
  - Implement blending algorithm (options: average, linear blend, multi-band blending)
- **Questions:**
  - Which blending method? (simple averaging vs. advanced multi-band?)
  - Do we need to handle exposure differences?
  - Canvas size calculation strategy?

### 8. Cropping & Output
- **Status:** Not Started
- **Key Tasks:**
  - Crop black borders from final panorama
  - Export result as high-quality image
  - (Optional) Generate interactive viewer
- **Questions:**
  - Output format? (PNG, JPG, TIFF?)
  - Do we need an interactive viewer or just static output?
  - Should we support different aspect ratios?

---

## Codebase Structure (Proposed)

```
ImageUnderstanding-HW2/
├── .env                      # Environment configuration
├── pyproject.toml            # UV project dependencies
├── main.py                   # Main entry point
│
├── src/                      # Source code
│   ├── __init__.py
│   ├── config.py             # Load .env and configuration
│   ├── utils/                # Utility functions
│   │   ├── __init__.py
│   │   ├── image_io.py       # Image loading/saving
│   │   └── visualization.py  # Plotting and visualization
│   │
│   ├── warping/              # Step 2: Cylindrical warping
│   │   ├── __init__.py
│   │   └── cylindrical.py    # Warping transformations
│   │
│   ├── features/             # Step 3: Feature extraction
│   │   ├── __init__.py
│   │   └── sift.py           # SIFT feature detection
│   │
│   ├── alignment/            # Step 4: Matching & RANSAC
│   │   ├── __init__.py
│   │   ├── matcher.py        # Feature matching
│   │   └── ransac.py         # RANSAC alignment
│   │
│   ├── stitching/            # Steps 5-8: Stitching pipeline
│   │   ├── __init__.py
│   │   ├── drift.py          # Drift correction
│   │   ├── blending.py       # Image blending
│   │   └── crop.py           # Cropping utilities
│   │
│   └── pipeline.py           # Orchestrate full pipeline
│
├── data/                     # Data directory
│   └── official/             # Official course images
│
├── output/                   # Output results
│   ├── warped/               # Warped images
│   ├── features/             # Feature visualizations
│   ├── matches/              # Matching visualizations
│   └── final/                # Final panoramas
│
├── doc/                      # Documentation
│   ├── development_plan.md   # This file
│   └── todo.md               # Task tracking
│
└── tests/                    # Unit tests (optional)
    └── __init__.py
```

---

## Technical Stack

- **Language:** Python 3.13
- **Package Manager:** uv
- **Core Libraries:**
  - OpenCV (cv2) - Image processing, SIFT, RANSAC
  - NumPy - Numerical operations
  - Matplotlib - Visualization
  - python-dotenv - Configuration management

---

## Key Design Decisions (CONFIRMED)

> **详细设计规格请参考:** `doc/design_specification.md`

### 1. **Focal Length Handling** ✅
- **Decision:** **Option B** - Auto-read from EXIF data
- **Implementation:**
  - Priority: CLI args > EXIF data > .env default
  - Fallback to `DEFAULT_FOCAL_LENGTH` in .env if EXIF missing
  - Support manual override via `--focal-length` parameter

### 2. **Pipeline Mode** ✅
- **Decision:** **Option C** - Hybrid Mode
- **Implementation:**
  - Default: Fully automated (run all 8 steps)
  - Support selective step execution via config
  - Save all intermediate results for debugging

### 3. **Intermediate Outputs** ✅
- **Decision:** **Option A** - Save all intermediate results
- **Implementation:**
  - Use timestamp-based directory structure: `output/{timestamp}/`
  - Save: warped images, features, matches, translations, blending, final
  - Each run creates isolated output directory
  - Create `latest/` symlink pointing to most recent run

### 4. **Translation List Format** ✅
- **Decision:** JSON format
- **Implementation:**
  - Save as `translations.json` with metadata
  - Include: pair indices, translation vectors, inlier counts
  - Human-readable and machine-parseable

### 5. **Blending Method** ✅
- **Decision:** Simple Averaging
- **Implementation:**
  - Arithmetic mean for overlapping regions
  - Fast and simple implementation
  - Suitable for consistent lighting conditions

### 6. **Drift Correction** ✅
- **Decision:** Full support as per PDF requirements
- **Implementation:**
  - Match first and last images
  - Compute gap angle θ_g
  - Update focal length: f' = f(1 - θ_g/2π)
  - Configurable: enable/disable via `.env`

### 7. **Configuration Management** ✅
- **Decision:** CLI + .env file
- **Implementation:**
  - Support command-line arguments
  - Load from `.env` when no CLI args provided
  - Priority: CLI > .env > defaults

### 8. **Interactive Viewer** ✅
- **Decision:** Not implemented
- **Rationale:**
  - Focus on stitching quality
  - Output high-quality static images
  - Use standard image viewers for results

### 9. **Dataset Preparation** ✅
- **Decision:** Prepare multiple test datasets
- **Implementation:**
  - Directory structure: `data/sample_panorama/{set1,set2,set3}/`
  - Include: building, landscape, 360-degree scenarios
  - Download from official source or prepare manually

### 10. **Error Handling** ✅
- **Decision:** Continue with warnings + detailed logging
- **Implementation:**
  - Log all warnings and errors
  - Skip failed image pairs
  - Generate summary report at end

---

## Design Decisions Summary

所有关键设计决策已确认（2025-11-14）：

| # | 决策项 | 选择 | 状态 |
|---|--------|------|------|
| 1 | 焦距处理 | 从EXIF读取（支持手动覆盖） | ✅ |
| 2 | Pipeline模式 | 混合模式（自动运行，保存所有中间结果） | ✅ |
| 3 | 中间结果保存 | 全部保存，使用时间戳隔离 | ✅ |
| 4 | 数据集准备 | 准备多个测试数据集 | ✅ |
| 5 | Translation格式 | JSON | ✅ |
| 6 | 融合方法 | 简单平均 | ✅ |
| 7 | 漂移校正 | 完整支持（可配置） | ✅ |
| 8 | 配置管理 | CLI参数 + .env文件 | ✅ |
| 9 | 交互式查看器 | 不实现 | ✅ |
| 10 | 错误处理 | 继续运行+警告日志 | ✅ |

**参考完整设计规格:** `doc/design_specification.md`

---

## Development Phases

### Phase 1: Foundation (Days 1-2)
- Setup project structure
- Implement configuration loading
- Create image I/O utilities
- Basic visualization tools

### Phase 2: Core Pipeline (Days 3-6)
- Cylindrical warping
- SIFT feature extraction
- Feature matching
- RANSAC alignment

### Phase 3: Stitching (Days 7-9)
- Translation computation
- Drift correction
- Image blending
- Cropping

### Phase 4: Testing & Refinement (Days 10-12)
- Test with real datasets
- Parameter tuning
- Bug fixes
- Performance optimization

### Phase 5: Documentation (Days 13-14)
- Code cleanup
- Report writing
- Generate visualizations
- Final testing

---

## Notes

- This plan is a living document and will be updated as decisions are made
- All updates should be tracked in `todo.md`
- Each module should be tested independently before integration
