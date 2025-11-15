"""Main pipeline for panorama stitching."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

from .alignment.matcher import extract_match_points, match_features
from .alignment.ransac import estimate_pure_translation_ransac
from .config import Config
from .features.sift import extract_sift_features
from .stitching.blending import blend_images, compute_cumulative_translations
from .stitching.crop import crop_panorama
from .stitching.drift import correct_drift, should_apply_drift_correction
from .utils.image_io import load_images, save_image
from .utils.visualization import plot_features, save_match_visualization
from .warping.cylindrical import estimate_focal_length_from_exif, warp_cylindrical

logger = logging.getLogger(__name__)


def convert_to_serializable(obj: Any) -> Any:
    """Convert numpy types to Python native types for JSON serialization.

    Args:
        obj: Object to convert

    Returns:
        JSON-serializable version of the object
    """
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_to_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_to_serializable(item) for item in obj)
    else:
        return obj


class PanoramaStitcher:
    """Panorama stitching pipeline."""

    def __init__(self, config: Config):
        """Initialize stitcher with configuration.

        Args:
            config: Configuration object
        """
        self.config = config
        self.output_dir = None
        self.images_data = []
        self.warped_images = []
        self.features = []
        self.translations = []
        self.focal_length = None

    def run(self) -> Path:
        """Run complete stitching pipeline.

        Returns:
            Path to final panorama
        """
        # Setup output directory
        self._setup_output_dir()

        # Setup logging
        self._setup_logging()

        logger.info("=" * 60)
        logger.info("Starting Panorama Stitching Pipeline")
        logger.info("=" * 60)

        # Step 1: Load images
        self._load_images()

        # Step 2: Cylindrical warping
        self._warp_images()

        # Step 3: Extract features
        self._extract_features()

        # Step 4: Match and align
        self._match_and_align()

        # Step 5: Save translations
        self._save_translations()

        # Step 6: Drift correction (if enabled)
        if self.config.enable_drift_correction:
            self._apply_drift_correction()

        # Step 7: Blend images
        panorama = self._blend_images()

        # Step 8: Crop and save
        final_path = self._crop_and_save(panorama)

        logger.info("=" * 60)
        logger.info(f"Pipeline completed! Result: {final_path}")
        logger.info("=" * 60)

        return final_path

    def _setup_output_dir(self):
        """Setup output directory structure."""
        # Use the output path provided by config (already timestamped by main.py)
        self.output_dir = self.config.output_path
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        for subdir in ["warped", "features", "matches"]:
            (self.output_dir / subdir).mkdir(exist_ok=True)

        logger.info(f"Pipeline output directory: {self.output_dir}")

    def _setup_logging(self):
        """Logging already setup by main.py, this is a no-op."""
        pass

    def _load_images(self):
        """Step 1: Load images and extract EXIF."""
        logger.info("Step 1: Loading images...")
        self.images_data = load_images(self.config.input_path)

        # Determine focal length
        if self.config.focal_length:
            self.focal_length = self.config.focal_length
            logger.info(f"Using CLI focal length: {self.focal_length} pixels")
        elif self.config.focal_length_source == "exif":
            # Try to get from EXIF with automatic sensor width estimation
            first_exif = self.images_data[0][2]
            first_image = self.images_data[0][0]
            # IMPORTANT: Use the WIDTH of the image, not height!
            # OpenCV image shape is (height, width, channels)
            image_width = first_image.shape[1]
            estimated_f = estimate_focal_length_from_exif(
                first_exif,
                image_width,
                sensor_width_mm=None,  # Will auto-estimate from EXIF 35mm equivalent
            )
            if estimated_f:
                self.focal_length = estimated_f
                logger.info(f"Using EXIF-estimated focal length: {self.focal_length:.1f} pixels")
            else:
                self.focal_length = self.config.default_focal_length
                logger.warning(
                    f"EXIF estimation failed, using default focal length: "
                    f"{self.focal_length} pixels"
                )
        else:
            self.focal_length = self.config.default_focal_length
            logger.info(f"Using default focal length: {self.focal_length} pixels")

        # Save metadata
        metadata = {
            "num_images": len(self.images_data),
            "focal_length": float(self.focal_length),
            "focal_length_source": (
                "cli" if self.config.focal_length else self.config.focal_length_source
            ),
            "image_files": [name for _, name, _ in self.images_data],
        }
        with open(self.output_dir / "metadata.json", "w") as f:
            json.dump(convert_to_serializable(metadata), f, indent=2)

    def _warp_images(self):
        """Step 2: Warp to cylindrical coordinates."""
        logger.info("Step 2: Warping images to cylindrical coordinates...")
        self.warped_images = []

        for i, (img, name, _) in enumerate(self.images_data):
            logger.info(f"  Warping {name}...")
            warped = warp_cylindrical(img, self.focal_length)
            self.warped_images.append(warped)

            if self.config.save_intermediate:
                save_path = self.output_dir / "warped" / f"{Path(name).stem}_warped.jpg"
                save_image(warped, save_path, self.config.output_quality)

    def _extract_features(self):
        """Step 3: Extract SIFT features."""
        logger.info("Step 3: Extracting SIFT features...")
        self.features = []

        for i, img in enumerate(self.warped_images):
            logger.info(f"  Extracting features from image {i}...")
            kp, desc = extract_sift_features(
                img,
                self.config.sift_n_features,
                self.config.sift_contrast_threshold,
                self.config.sift_edge_threshold,
            )
            self.features.append((kp, desc))

            if self.config.save_intermediate:
                save_path = self.output_dir / "features" / f"img_{i:04d}_features.jpg"
                plot_features(img, kp, f"Image {i} Features", save_path)

    def _match_and_align(self):
        """Step 4: Match features and estimate translations."""
        logger.info("Step 4: Matching features and estimating translations...")
        self.translations = []

        for i in range(len(self.features) - 1):
            logger.info(f"  Matching images {i} <-> {i+1}...")
            kp1, desc1 = self.features[i]
            kp2, desc2 = self.features[i + 1]

            # Match features
            matches = match_features(
                desc1, desc2, self.config.match_ratio_threshold
            )

            if len(matches) < 4:
                logger.warning(f"Not enough matches for pair {i}-{i+1}, using zero translation")
                self.translations.append({
                    "pair": [i, i + 1],
                    "translation": (0, 0),
                    "num_matches": len(matches),
                    "num_inliers": 0,
                    "inlier_ratio": 0.0,
                })
                continue

            # Extract points
            pts1, pts2 = extract_match_points(kp1, kp2, matches)

            # RANSAC
            result = estimate_pure_translation_ransac(
                pts1,
                pts2,
                self.config.ransac_threshold,
                self.config.ransac_max_iters,
            )

            self.translations.append({
                "pair": [i, i + 1],
                "translation": result["translation"],
                "num_matches": len(matches),
                "num_inliers": result["num_inliers"],
                "inlier_ratio": result["inlier_ratio"],
            })

            # Save visualization
            if self.config.save_intermediate:
                save_path = self.output_dir / "matches" / f"match_{i:04d}_{i+1:04d}.jpg"
                save_match_visualization(
                    self.warped_images[i],
                    self.warped_images[i + 1],
                    pts1,
                    pts2,
                    result["inliers"],
                    save_path,
                )

    def _save_translations(self):
        """Step 5: Save translation list to JSON."""
        logger.info("Step 5: Saving translations...")

        data = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "focal_length": float(self.focal_length),
                "num_images": len(self.images_data),
            },
            "translations": convert_to_serializable(self.translations),
        }

        with open(self.output_dir / "translations.json", "w") as f:
            json.dump(data, f, indent=2)

    def _apply_drift_correction(self):
        """Step 6: Apply drift correction."""
        logger.info("Step 6: Applying drift correction...")

        # Match first and last images
        kp1, desc1 = self.features[0]
        kp_last, desc_last = self.features[-1]

        matches = match_features(desc1, desc_last, self.config.match_ratio_threshold)

        if len(matches) < 4:
            logger.warning("Not enough matches between first and last images, skipping drift correction")
            return

        pts1, pts_last = extract_match_points(kp1, kp_last, matches)

        first_last_result = estimate_pure_translation_ransac(
            pts1, pts_last, self.config.ransac_threshold, self.config.ransac_max_iters
        )

        if should_apply_drift_correction(first_last_result):
            correction = correct_drift(
                self.translations,
                first_last_result,
                self.focal_length,
                self.warped_images[0].shape[1],
            )

            # Save correction parameters
            with open(self.output_dir / "drift_correction.json", "w") as f:
                json.dump(convert_to_serializable(correction), f, indent=2)

            # Update focal length if corrected
            if "corrected_focal_length" in correction:
                self.focal_length = correction["corrected_focal_length"]
        else:
            logger.warning("Drift correction skipped due to poor match quality")

    def _blend_images(self):
        """Step 7: Blend images into panorama."""
        logger.info("Step 7: Blending images...")

        # Compute cumulative translations
        pairwise_t = [t["translation"] for t in self.translations]
        cumulative_t = compute_cumulative_translations(pairwise_t)

        # Blend
        panorama = blend_images(
            self.warped_images, cumulative_t, self.config.blend_method
        )

        if self.config.save_intermediate:
            save_image(
                panorama,
                self.output_dir / "blended.jpg",
                self.config.output_quality,
            )

        return panorama

    def _crop_and_save(self, panorama):
        """Step 8: Crop and save final result."""
        logger.info("Step 8: Cropping and saving final panorama...")

        cropped = crop_panorama(panorama)

        final_path = self.output_dir / f"final.{self.config.output_format}"
        save_image(cropped, final_path, self.config.output_quality)

        return final_path
