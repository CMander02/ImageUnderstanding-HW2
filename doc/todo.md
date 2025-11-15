# Cylindrical Panorama - TODO List

**Last Updated:** 2025-11-14
**Project Deadline:** November 15, 2025

---

## Legend
- ✅ Completed
- 🚧 In Progress
- ⏳ Pending
- ❌ Blocked
- 📝 Needs Discussion

---

## Phase 0: Planning & Setup

### Environment Setup
- ✅ Initialize Python 3.13 environment with uv
- ✅ Install dependencies (OpenCV, NumPy, Matplotlib, python-dotenv)
- ✅ Create `.env` configuration file
- ✅ Setup git repository and branch
- ✅ Create project documentation structure

### Planning
- ✅ Create development plan document
- ✅ Create TODO list
- 📝 **Clarify design decisions** (see questions below)
- ⏳ Finalize codebase structure
- ⏳ Define configuration parameters

---

## Phase 1: Foundation

### Project Structure
- ⏳ Create `src/` directory structure
  - ⏳ `src/__init__.py`
  - ⏳ `src/config.py`
  - ⏳ `src/utils/`
  - ⏳ `src/warping/`
  - ⏳ `src/features/`
  - ⏳ `src/alignment/`
  - ⏳ `src/stitching/`
  - ⏳ `src/pipeline.py`

### Configuration Module
- ⏳ Implement `src/config.py`
  - ⏳ Load `.env` variables
  - ⏳ Define default parameters (focal length, RANSAC params, etc.)
  - ⏳ Validate configuration

### Utility Modules
- ⏳ Implement `src/utils/image_io.py`
  - ⏳ Load images from directory
  - ⏳ Sort images by filename
  - ⏳ Save images with proper naming
  - ⏳ Handle different image formats

- ⏳ Implement `src/utils/visualization.py`
  - ⏳ Display images with matplotlib
  - ⏳ Plot feature points
  - ⏳ Visualize feature matches
  - ⏳ Save visualizations to file

### Output Directory Structure
- ⏳ Create `output/` directories
  - ⏳ `output/warped/`
  - ⏳ `output/features/`
  - ⏳ `output/matches/`
  - ⏳ `output/final/`

---

## Phase 2: Cylindrical Warping (Step 2)

### Implementation
- ⏳ Implement `src/warping/cylindrical.py`
  - ⏳ Define cylindrical projection formulas
    - ⏳ Forward mapping: (x,y) → (θ, h)
    - ⏳ Backward mapping: (θ, h) → (x', y')
  - ⏳ Implement warping function with interpolation
  - ⏳ Handle image boundaries and black regions
  - ⏳ Support configurable focal length

### Testing
- ⏳ Test warping with single image
- ⏳ Verify warped image quality
- ⏳ Test different focal lengths
- ⏳ Save warped images to `output/warped/`

### Documentation
- ⏳ Add docstrings to warping functions
- ⏳ Document focal length parameter effects

---

## Phase 3: Feature Extraction (Step 3)

### Implementation
- ⏳ Implement `src/features/sift.py`
  - ⏳ Initialize SIFT detector
  - ⏳ Extract keypoints and descriptors
  - ⏳ Handle grayscale conversion
  - ⏳ Return structured feature data

### Testing
- ⏳ Extract features from warped images
- ⏳ Verify feature count and distribution
- ⏳ Visualize features on images
- ⏳ Save feature visualizations to `output/features/`

### Documentation
- ⏳ Document SIFT parameters
- ⏳ Add usage examples

---

## Phase 4: Feature Matching & RANSAC (Step 4)

### Feature Matching
- ⏳ Implement `src/alignment/matcher.py`
  - ⏳ Use FLANN or BFMatcher
  - ⏳ Apply Lowe's ratio test
  - ⏳ Match neighboring image pairs
  - ⏳ Return match correspondences

### RANSAC Alignment
- ⏳ Implement `src/alignment/ransac.py`
  - ⏳ Estimate translation using RANSAC
  - ⏳ Filter inliers/outliers
  - ⏳ Compute transformation matrix
  - ⏳ Return translation vector (dx, dy)

### Testing
- ⏳ Test matching on image pairs
- ⏳ Visualize matches
- ⏳ Verify RANSAC accuracy
- ⏳ Save match visualizations to `output/matches/`

### Documentation
- ⏳ Document matcher parameters
- ⏳ Explain RANSAC threshold selection

---

## Phase 5: Translation List (Step 5)

### Implementation
- ⏳ Implement translation computation
  - ⏳ Process all neighboring pairs
  - ⏳ Store pairwise translations
  - ⏳ Save to file (format TBD: JSON/CSV/pickle)

### Testing
- ⏳ Verify translation consistency
- ⏳ Check translation file format
- ⏳ Validate against expected values

### Documentation
- ⏳ Document translation file format
- ⏳ Add example translation data

---

## Phase 6: Drift Correction (Step 6)

### Implementation
- ⏳ Implement `src/stitching/drift.py`
  - ⏳ Match first and last images
  - ⏳ Compute gap angle θ_g
  - ⏳ Distribute correction across sequence
  - ⏳ Update focal length: f' = f(1 - θ_g/2π)
  - ⏳ Modify rotation parameters

### Testing
- ⏳ Test with 360° panorama dataset
- ⏳ Compare before/after drift correction
- ⏳ Verify focal length update
- ⏳ Handle non-360° cases

### Documentation
- ⏳ Explain drift correction algorithm
- ⏳ Document when to apply correction

---

## Phase 7: Image Blending (Step 7)

### Implementation
- ⏳ Implement `src/stitching/blending.py`
  - ⏳ Create panorama canvas
  - ⏳ Place warped images using translations
  - ⏳ Implement blending algorithm
    - ⏳ Option: Simple averaging
    - ⏳ Option: Linear/feather blending
    - ⏳ Option: Multi-band blending (advanced)
  - ⏳ Handle overlapping regions

### Testing
- ⏳ Test blending with 2-3 images
- ⏳ Test with full image sequence
- ⏳ Compare blending methods
- ⏳ Check for visible seams

### Documentation
- ⏳ Document blending method selection
- ⏳ Add blending quality comparisons

---

## Phase 8: Cropping & Output (Step 8)

### Implementation
- ⏳ Implement `src/stitching/crop.py`
  - ⏳ Detect black borders
  - ⏳ Compute tight bounding box
  - ⏳ Crop panorama
  - ⏳ Save final result

### Output Generation
- ⏳ Export high-quality panorama (PNG/JPG)
- ⏳ Save to `output/final/`
- ⏳ (Optional) Generate interactive viewer

### Testing
- ⏳ Verify crop correctness
- ⏳ Check output quality
- ⏳ Test different output formats

### Documentation
- ⏳ Document output specifications
- ⏳ Add example outputs

---

## Phase 9: Pipeline Integration

### Main Pipeline
- ⏳ Implement `src/pipeline.py`
  - ⏳ Orchestrate all 8 steps
  - ⏳ Handle intermediate outputs
  - ⏳ Add progress logging
  - ⏳ Error handling

### Main Entry Point
- ⏳ Update `main.py`
  - ⏳ Parse command-line arguments (optional)
  - ⏳ Load configuration
  - ⏳ Run pipeline
  - ⏳ Display results

### Testing
- ⏳ End-to-end test with sample dataset
- ⏳ Test with different configurations
- ⏳ Verify all outputs generated

### Documentation
- ⏳ Add usage instructions to README
- ⏳ Document CLI interface (if any)

---

## Phase 10: Testing & Refinement

### Testing
- ⏳ Download official test images
- ⏳ Run full pipeline on test data
- ⏳ Parameter tuning
  - ⏳ Focal length optimization
  - ⏳ RANSAC threshold tuning
  - ⏳ Blending method selection
- ⏳ Quality assessment
- ⏳ Performance profiling

### Bug Fixes
- ⏳ Fix identified issues
- ⏳ Edge case handling
- ⏳ Memory optimization

### Code Quality
- ⏳ Code cleanup
- ⏳ Add type hints (optional)
- ⏳ Improve comments
- ⏳ Remove debug code

---

## Phase 11: Documentation & Report

### Code Documentation
- ⏳ Complete all docstrings
- ⏳ Update README.md
- ⏳ Add usage examples
- ⏳ Document configuration options

### Report Preparation
- ⏳ Generate result visualizations
- ⏳ Capture intermediate outputs
- ⏳ Document algorithm choices
- ⏳ Prepare comparison images
- ⏳ Write report (if required)

### Final Deliverables
- ⏳ Clean git history
- ⏳ Final code review
- ⏳ Create submission package
- ⏳ Test on fresh environment

---

## Questions Needing Decisions

### Critical (Must Decide Before Coding)
1. 📝 **Focal Length:** Fixed config value or auto-estimate? Default value?
2. 📝 **Pipeline Mode:** Fully automated or step-by-step?
3. 📝 **Intermediate Outputs:** Save all stages or final only?
4. 📝 **Image Dataset:** Which official dataset to use? Multiple datasets?

### Important (Affects Implementation)
5. 📝 **Translation Format:** JSON, CSV, or Python pickle?
6. 📝 **Blending Method:** Simple average, linear, or multi-band?
7. 📝 **Drift Correction:** Always apply or optional?
8. 📝 **Match Visualization:** Save all matches or just summary?

### Nice to Have (Can Decide Later)
9. 📝 **CLI Arguments:** Support command-line options?
10. 📝 **Unit Tests:** Add pytest tests?
11. 📝 **Interactive Viewer:** Implement or skip?
12. 📝 **Configuration File:** YAML/JSON config in addition to .env?

---

## Notes

- Update this file as tasks are completed
- Mark blocked tasks with reasons
- Add new tasks as discovered during development
- Reference `development_plan.md` for architectural decisions
