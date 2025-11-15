"""Configuration management for panorama stitching."""

import argparse
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


@dataclass
class Config:
    """Configuration for panorama stitching pipeline."""

    # Input/Output
    input_path: Path
    output_path: Path

    # Focal length
    focal_length: Optional[float]
    focal_length_source: str  # "exif" | "config" | "auto"
    default_focal_length: float

    # Pipeline
    save_intermediate: bool
    pipeline_steps: str  # "all" or comma-separated steps

    # SIFT parameters
    sift_n_features: int
    sift_contrast_threshold: float
    sift_edge_threshold: float

    # Feature matching
    match_ratio_threshold: float

    # RANSAC parameters
    ransac_threshold: float
    ransac_max_iters: int
    ransac_confidence: float

    # Drift correction
    enable_drift_correction: bool

    # Blending
    blend_method: str  # "average" | "linear" | "multiband"

    # Output
    output_format: str  # "jpg" | "png"
    output_quality: int  # 1-100 for JPEG


def load_config() -> Config:
    """Load configuration from .env file and command-line arguments.

    Priority: CLI args > .env > defaults

    Returns:
        Config object with all settings
    """
    # Load .env file
    load_dotenv()

    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Cylindrical Panorama Stitching",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Input/Output
    parser.add_argument(
        "--input",
        type=str,
        default=os.getenv("IMAGE_PATH", "./data/pano1"),
        help="Input image directory",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=os.getenv("OUTPUT_PATH", "./output"),
        help="Output directory (timestamp will be added)",
    )

    # Focal length
    parser.add_argument(
        "--focal-length",
        type=float,
        default=None,
        help="Focal length (overrides EXIF and config)",
    )

    # Pipeline options
    parser.add_argument(
        "--no-drift-correction",
        action="store_true",
        help="Disable drift correction",
    )
    parser.add_argument(
        "--blend-method",
        type=str,
        choices=["average", "linear", "multiband"],
        default=os.getenv("BLEND_METHOD", "average"),
        help="Blending method",
    )
    parser.add_argument(
        "--steps",
        type=str,
        default=os.getenv("PIPELINE_STEPS", "all"),
        help="Pipeline steps to run (all or comma-separated)",
    )

    args = parser.parse_args()

    # Build configuration
    config = Config(
        # Input/Output
        input_path=Path(args.input),
        output_path=Path(args.output),
        # Focal length
        focal_length=args.focal_length,
        focal_length_source=os.getenv("FOCAL_LENGTH_SOURCE", "exif"),
        default_focal_length=float(os.getenv("DEFAULT_FOCAL_LENGTH", "500")),
        # Pipeline
        save_intermediate=os.getenv("SAVE_INTERMEDIATE", "true").lower() == "true",
        pipeline_steps=args.steps,
        # SIFT
        sift_n_features=int(os.getenv("SIFT_N_FEATURES", "0")),
        sift_contrast_threshold=float(os.getenv("SIFT_CONTRAST_THRESHOLD", "0.04")),
        sift_edge_threshold=float(os.getenv("SIFT_EDGE_THRESHOLD", "10")),
        # Matching
        match_ratio_threshold=float(os.getenv("MATCH_RATIO_THRESHOLD", "0.7")),
        # RANSAC
        ransac_threshold=float(os.getenv("RANSAC_THRESHOLD", "5.0")),
        ransac_max_iters=int(os.getenv("RANSAC_MAX_ITERS", "2000")),
        ransac_confidence=float(os.getenv("RANSAC_CONFIDENCE", "0.995")),
        # Drift correction
        enable_drift_correction=not args.no_drift_correction
        and os.getenv("ENABLE_DRIFT_CORRECTION", "true").lower() == "true",
        # Blending
        blend_method=args.blend_method,
        # Output
        output_format=os.getenv("OUTPUT_FORMAT", "jpg"),
        output_quality=int(os.getenv("OUTPUT_QUALITY", "95")),
    )

    return config


def print_config(config: Config) -> None:
    """Print configuration for debugging."""
    print("=" * 60)
    print("Panorama Stitching Configuration")
    print("=" * 60)
    print(f"Input:  {config.input_path}")
    print(f"Output: {config.output_path}")
    print(f"Focal length source: {config.focal_length_source}")
    if config.focal_length:
        print(f"Focal length (override): {config.focal_length}")
    else:
        print(f"Default focal length: {config.default_focal_length}")
    print(f"Drift correction: {config.enable_drift_correction}")
    print(f"Blend method: {config.blend_method}")
    print(f"Pipeline steps: {config.pipeline_steps}")
    print("=" * 60)
