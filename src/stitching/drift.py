"""Drift correction for 360-degree panoramas."""

import logging
from typing import Dict, List

import numpy as np

logger = logging.getLogger(__name__)


def correct_drift(
    translations: List[Dict],
    first_last_translation: Dict,
    focal_length: float,
    image_width: int,
) -> Dict:
    """Correct drift for 360-degree panoramas (PDF step 6).

    Algorithm from PDF:
    1. Match first and last images
    2. Compute gap angle θ_g
    3. Distribute gap angle evenly: θ_g / N_images
    4. Update focal length: f' = f * (1 - θ_g / 2π)

    Args:
        translations: List of pairwise translations [{translation: (dx, dy), ...}, ...]
        first_last_translation: Translation from first to last image
        focal_length: Current focal length in pixels
        image_width: Image width in pixels (not used for horizontal panorama)

    Returns:
        Dictionary with:
            - corrected_focal_length: Updated focal length
            - gap_angle: Computed gap angle in radians
            - original_focal_length: Original focal length
            - correction_applied: Whether correction was applied
    """
    n_images = len(translations) + 1  # Number of images

    # Extract translation from first-last match
    dx_gap, dy_gap = first_last_translation["translation"]

    # For HORIZONTAL panorama (cylinder wraps around Y-axis):
    # The drift occurs in the Y direction, so we use dy
    # For cylindrical projection: θ = dy / f
    # Total accumulated angle from pairwise translations
    total_dy = sum(t["translation"][1] for t in translations)

    # Gap angle is the difference
    # In a perfect 360° panorama: total accumulated angle should be 2π
    # Gap angle represents the accumulated error
    theta_accumulated = total_dy / focal_length
    theta_gap = dy_gap / focal_length

    # The gap angle is the error we need to correct
    # Distribute evenly across all image pairs
    correction_per_pair = theta_gap / n_images

    # Update focal length according to PDF formula
    # f' = f * (1 - θ_g / 2π)
    corrected_focal_length = focal_length * (1 - theta_gap / (2 * np.pi))

    logger.info(
        f"Drift correction: gap_angle={theta_gap:.4f} rad ({np.degrees(theta_gap):.2f}°), "
        f"f={focal_length:.1f} -> f'={corrected_focal_length:.1f}"
    )

    return {
        "corrected_focal_length": corrected_focal_length,
        "original_focal_length": focal_length,
        "gap_angle": theta_gap,
        "gap_angle_degrees": np.degrees(theta_gap),
        "correction_per_pair": correction_per_pair,
        "num_images": n_images,
        "correction_applied": True,
    }


def should_apply_drift_correction(
    first_last_match_quality: Dict, min_inlier_ratio: float = 0.3
) -> bool:
    """Determine if drift correction should be applied.

    Args:
        first_last_match_quality: Match result from first-last image pair
        min_inlier_ratio: Minimum inlier ratio to trust the match

    Returns:
        True if drift correction should be applied
    """
    # Check if we have enough inliers
    if first_last_match_quality["num_inliers"] < 10:
        logger.warning(
            f"Too few inliers ({first_last_match_quality['num_inliers']}) "
            "for drift correction"
        )
        return False

    if first_last_match_quality["inlier_ratio"] < min_inlier_ratio:
        logger.warning(
            f"Inlier ratio too low ({first_last_match_quality['inlier_ratio']:.1%}) "
            "for drift correction"
        )
        return False

    return True
