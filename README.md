# Cylindrical Panorama Stitching

A uv run implementation of cylindrical panorama image stitching using SIFT features and RANSAC alignment.

## Quick Start

### 1. Environment Setup

```bash
# Install dependencies using uv
uv sync
```

### 2. Data Preparation

Download and prepare the pano1 dataset:

```bash
# Download from USTC server and extract to data/pano1/
uv run scripts/prepare_data.py
```

This will:
- Download `pano1.zip` from http://staff.ustc.edu.cn/~xjchen99/teaching/pano1.zip
- Extract images to `data/pano1/`
- Clean up temporary files

Alternatively, manually download images to your desired directory.

### 3. Run Stitching

```bash
# Basic usage (uses default input directory)
uv run main.py

# Specify input directory
uv run main.py --input data/pano1
```

### 4. View Results

Results are saved in timestamped directories under `outputs/`:
```
outputs/
└── 20250115-143022/
    ├── warped/              # Cylindrical projected images
    ├── features/            # Feature detection visualization
    ├── matches/             # Feature matching visualization
    ├── blended.jpg          # Blended panorama
    ├── final.jpg            # Final cropped result
    └── 20250115-143022.log     # Execution log
```

## Command Line Arguments

### Basic Usage
```bash
uv run main.py [OPTIONS]
```

### Available Options

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--input` | string | `./data/pano1` | Input image directory |
| `--output` | string | `./output` | Base output directory (timestamp added automatically) |
| `--focal-length` | float | None | Focal length in pixels (overrides EXIF) |
| `--blend-method` | choice | `average` | Blending method: `average`, `linear`, or `multiband` |
| `--no-drift-correction` | flag | False | Disable drift correction for 360° panoramas |
| `--steps` | string | `all` | Pipeline steps to run (e.g., `all` or `warp,match,blend`) |

### Examples

```bash
# Use custom input directory
uv run main.py --input data/my_photos

# Override focal length
uv run main.py --focal-length 800

# Use linear blending without drift correction
uv run main.py --blend-method linear --no-drift-correction

# Run specific pipeline steps
uv run main.py --steps warp,match,blend
```

## Environment Configuration

Additional parameters can be configured via `.env` file:

```bash
# Input/Output
IMAGE_PATH=./data/pano1
OUTPUT_PATH=./output

# Focal Length
DEFAULT_FOCAL_LENGTH=500
FOCAL_LENGTH_SOURCE=exif  # exif | config | auto

# Pipeline
SAVE_INTERMEDIATE=true
PIPELINE_STEPS=all

# SIFT Parameters
SIFT_N_FEATURES=0
SIFT_CONTRAST_THRESHOLD=0.04
SIFT_EDGE_THRESHOLD=10

# Feature Matching
MATCH_RATIO_THRESHOLD=0.7

# RANSAC
RANSAC_THRESHOLD=5.0
RANSAC_MAX_ITERS=2000
RANSAC_CONFIDENCE=0.995

# Drift Correction
ENABLE_DRIFT_CORRECTION=true

# Blending
BLEND_METHOD=average

# Output
OUTPUT_FORMAT=jpg
OUTPUT_QUALITY=95
```

**Configuration Priority:** Command-line arguments > `.env` file > Default values

## Pipeline Overview

The stitching pipeline consists of 8 steps:

1. **Image Loading** - Load image sequence from directory
2. **Cylindrical Projection** - Warp images using focal length from EXIF or config
3. **Feature Detection** - Detect SIFT features in projected images
4. **Feature Matching** - Match features between adjacent images using RANSAC
5. **Translation Estimation** - Compute and save translation parameters to JSON
6. **Drift Correction** - Apply end-to-end correction for 360° panoramas
7. **Image Blending** - Blend aligned images using selected method
8. **Cropping** - Automatically crop black borders from final result

## Technical Stack

- **uv run:** 3.13
- **Package Manager:** uv
- **Core Libraries:**
  - OpenCV (cv2) - Image processing, SIFT, RANSAC
  - NumPy - Numerical computation
  - Matplotlib - Visualization
  - Pillow - EXIF metadata reading
  - uv run-dotenv - Configuration management

## Project Structure

```
ImageUnderstanding-HW2/
├── main.py                 # Main entry point
├── src/                    # Source code package
│   ├── config.py           # Configuration management
│   ├── pipeline.py         # Main stitching pipeline
│   ├── warping.py          # Cylindrical projection
│   ├── features.py         # SIFT feature detection
│   ├── matching.py         # Feature matching and RANSAC
│   ├── alignment.py        # Image alignment
│   ├── blending.py         # Image blending
│   └── utils.py            # Utility functions
├── data/                   # Input images
│   └── pano1/              # Sample dataset
├── outputs/                # Output results (timestamped)
├── scripts/                # Utility scripts
│   └── prepare_data.py     # Data download script
├── .env                    # Configuration file
└── pyproject.toml          # Project dependencies
```

## License

This project is for educational purposes as part of the Image Understanding course.
