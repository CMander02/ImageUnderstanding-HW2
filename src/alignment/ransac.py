"""RANSAC-based translation estimation."""

import logging
from typing import Dict, Tuple

import cv2
import numpy as np

logger = logging.getLogger(__name__)


def estimate_translation_ransac(
    pts1: np.ndarray,
    pts2: np.ndarray,
    threshold: float = 5.0,
    max_iters: int = 2000,
    confidence: float = 0.995,
) -> Dict:
    """Estimate translation between two sets of matched points using RANSAC.

    For panorama stitching, we assume only translation (no rotation/scaling).

    Args:
        pts1: Points in first image (Nx2)
        pts2: Points in second image (Nx2)
        threshold: RANSAC inlier threshold in pixels
        max_iters: Maximum RANSAC iterations
        confidence: Confidence level for RANSAC

    Returns:
        Dictionary with:
            - translation: (dx, dy) translation vector
            - inliers: Inlier mask
            - num_inliers: Number of inliers
            - inlier_ratio: Ratio of inliers to total matches
    """
    if len(pts1) < 4:
        logger.warning(f"Not enough points for RANSAC: {len(pts1)}")
        return {
            "translation": (0, 0),
            "inliers": np.zeros(len(pts1), dtype=bool),
            "num_inliers": 0,
            "inlier_ratio": 0.0,
        }

    # Use cv2.estimateAffinePartial2D which handles translation + rotation + scale
    # But we'll extract only translation component
    # Alternative: use custom RANSAC for pure translation

    # Method 1: Use findHomography and extract translation
    # For simple panoramas, we can use a translation-only model
    H, mask = cv2.findHomography(
        pts1, pts2, cv2.RANSAC, ransacReprojThreshold=threshold, maxIters=max_iters, confidence=confidence
    )

    if H is None:
        logger.warning("RANSAC failed to find homography")
        return {
            "translation": (0, 0),
            "inliers": np.zeros(len(pts1), dtype=bool),
            "num_inliers": 0,
            "inlier_ratio": 0.0,
        }

    # Extract translation from homography
    # H is 3x3, translation is in H[0,2] and H[1,2]
    dx = H[0, 2]
    dy = H[1, 2]

    # Count inliers
    inliers = mask.ravel().astype(bool)
    num_inliers = np.sum(inliers)
    inlier_ratio = num_inliers / len(pts1)

    logger.info(
        f"RANSAC: translation=({dx:.1f}, {dy:.1f}), "
        f"inliers={num_inliers}/{len(pts1)} ({inlier_ratio:.1%})"
    )

    return {
        "translation": (dx, dy),
        "homography": H,
        "inliers": inliers,
        "num_inliers": num_inliers,
        "inlier_ratio": inlier_ratio,
    }


def estimate_pure_translation_ransac(
    pts1: np.ndarray,
    pts2: np.ndarray,
    threshold: float = 5.0,
    max_iters: int = 2000,
) -> Dict:
    """Estimate pure translation (no rotation/scale) using custom RANSAC.

    This is more appropriate for cylindrical panoramas where we only have translation.

    Args:
        pts1: Points in first image (Nx2)
        pts2: Points in second image (Nx2)
        threshold: Inlier threshold in pixels
        max_iters: Maximum iterations

    Returns:
        Dictionary with translation and inlier information
    """
    if len(pts1) < 1:
        logger.warning("No points for RANSAC")
        return {
            "translation": (0, 0),
            "inliers": np.zeros(0, dtype=bool),
            "num_inliers": 0,
            "inlier_ratio": 0.0,
        }

    best_inliers = 0
    best_translation = (0, 0)
    best_mask = np.zeros(len(pts1), dtype=bool)

    n_points = len(pts1)

    for _ in range(max_iters):
        # Randomly sample one point pair
        idx = np.random.randint(0, n_points)

        # Compute translation from this pair
        dx = pts2[idx, 0] - pts1[idx, 0]
        dy = pts2[idx, 1] - pts1[idx, 1]

        # Transform all pts1 by this translation
        transformed = pts1 + np.array([dx, dy])

        # Compute distances to pts2
        distances = np.linalg.norm(transformed - pts2, axis=1)

        # Count inliers
        mask = distances < threshold
        num_inliers = np.sum(mask)

        if num_inliers > best_inliers:
            best_inliers = num_inliers
            best_translation = (dx, dy)
            best_mask = mask

    # Refine translation using all inliers
    if best_inliers > 0:
        inlier_pts1 = pts1[best_mask]
        inlier_pts2 = pts2[best_mask]
        dx = np.median(inlier_pts2[:, 0] - inlier_pts1[:, 0])
        dy = np.median(inlier_pts2[:, 1] - inlier_pts1[:, 1])
        best_translation = (dx, dy)

    inlier_ratio = best_inliers / n_points if n_points > 0 else 0.0

    logger.info(
        f"Pure translation RANSAC: t=({best_translation[0]:.1f}, {best_translation[1]:.1f}), "
        f"inliers={best_inliers}/{n_points} ({inlier_ratio:.1%})"
    )

    return {
        "translation": best_translation,
        "inliers": best_mask,
        "num_inliers": best_inliers,
        "inlier_ratio": inlier_ratio,
    }
