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

## Key Design Decisions (To Be Confirmed)

### 1. **Focal Length Handling**
- **Option A:** Fixed focal length (user-specified in config)
- **Option B:** Auto-estimate from EXIF data
- **Option C:** Interactive calibration tool
- **Decision:** ?

### 2. **Pipeline Mode**
- **Option A:** Fully automated (one-click run)
- **Option B:** Step-by-step (manual control per stage)
- **Option C:** Hybrid (auto with manual override)
- **Decision:** ?

### 3. **Intermediate Outputs**
- **Option A:** Save all intermediate results (warped images, features, matches)
- **Option B:** Save only final panorama
- **Option C:** Configurable via CLI flags
- **Decision:** ?

### 4. **Error Handling**
- **Option A:** Fail fast (stop on first error)
- **Option B:** Continue with warnings
- **Option C:** Retry with fallback parameters
- **Decision:** ?

### 5. **Testing Strategy**
- **Option A:** Unit tests for each module
- **Option B:** Integration test with sample dataset
- **Option C:** Manual testing only
- **Decision:** ?

---

## Questions for Clarification

### High Priority
1. **Image Dataset:** Should we support multiple datasets or focus on one official set?
2. **Focal Length:** How should we determine/configure focal length?
3. **Pipeline Execution:** Fully automated or step-by-step control?
4. **Output Requirements:** What intermediate outputs are needed for the report?

### Medium Priority
5. **Blending Algorithm:** Simple averaging or advanced multi-band blending?
6. **Drift Correction:** Always apply or only for 360° panoramas?
7. **Visualization:** How much debugging/visualization output is needed?
8. **Performance:** Are there speed/memory constraints?

### Low Priority
9. **Code Quality:** Do we need unit tests?
10. **Documentation:** Level of code documentation required?
11. **Interactive Features:** Any need for GUI or interactive tools?
12. **Extensibility:** Should the code support future extensions (e.g., vertical panoramas)?

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
