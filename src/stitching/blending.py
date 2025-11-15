"""Image blending for panorama stitching."""

import logging
from typing import List, Tuple

import cv2
import numpy as np

logger = logging.getLogger(__name__)


def blend_images(
    images: List[np.ndarray],
    translations: List[Tuple[float, float]],
    method: str = "average",
) -> np.ndarray:
    """Blend multiple images into a panorama.

    Args:
        images: List of warped images (BGR)
        translations: List of cumulative translations [(dx, dy), ...]
        method: Blending method ("average", "linear", "multiband")

    Returns:
        Blended panorama image
    """
    if not images:
        raise ValueError("No images to blend")

    if method == "average":
        return blend_average(images, translations)
    elif method == "linear":
        return blend_linear(images, translations)
    elif method == "multiband":
        logger.warning("Multi-band blending not implemented, using average")
        return blend_average(images, translations)
    else:
        raise ValueError(f"Unknown blending method: {method}")


def blend_average(
    images: List[np.ndarray], translations: List[Tuple[float, float]]
) -> np.ndarray:
    """Simple average blending for overlapping regions.

    Args:
        images: List of warped images
        translations: List of cumulative translations

    Returns:
        Blended panorama
    """
    if len(images) == 0:
        raise ValueError("No images to blend")

    # Compute panorama canvas size
    min_x, max_x, min_y, max_y = compute_canvas_bounds(images, translations)

    canvas_width = int(np.ceil(max_x - min_x))
    canvas_height = int(np.ceil(max_y - min_y))

    logger.info(f"Canvas size: {canvas_width} x {canvas_height}")

    # Create canvas and weight map
    canvas = np.zeros((canvas_height, canvas_width, 3), dtype=np.float32)
    weights = np.zeros((canvas_height, canvas_width), dtype=np.float32)

    # Place each image on canvas
    for i, (img, (tx, ty)) in enumerate(zip(images, translations)):
        # Compute position on canvas
        x_offset = int(np.round(tx - min_x))
        y_offset = int(np.round(ty - min_y))

        h, w = img.shape[:2]

        # Check bounds
        if x_offset + w > canvas_width:
            w = canvas_width - x_offset
        if y_offset + h > canvas_height:
            h = canvas_height - y_offset
        if x_offset < 0:
            w += x_offset
            x_offset = 0
        if y_offset < 0:
            h += y_offset
            y_offset = 0

        if w <= 0 or h <= 0:
            logger.warning(f"Image {i} out of canvas bounds, skipping")
            continue

        # Create mask for non-black pixels
        img_crop = img[:h, :w]
        mask = np.any(img_crop > 0, axis=2).astype(np.float32)

        # Add to canvas with weighted average
        canvas[y_offset : y_offset + h, x_offset : x_offset + w] += (
            img_crop.astype(np.float32) * mask[:, :, np.newaxis]
        )
        weights[y_offset : y_offset + h, x_offset : x_offset + w] += mask

        logger.debug(f"Placed image {i} at ({x_offset}, {y_offset})")

    # Normalize by weights (avoid division by zero)
    non_zero = weights > 0
    canvas[non_zero] /= weights[non_zero, np.newaxis]

    # Convert back to uint8
    panorama = canvas.astype(np.uint8)

    logger.info("Average blending completed")
    return panorama


def blend_linear(
    images: List[np.ndarray], translations: List[Tuple[float, float]]
) -> np.ndarray:
    """Linear (feathering) blending for smoother transitions.

    Args:
        images: List of warped images
        translations: List of cumulative translations

    Returns:
        Blended panorama
    """
    # For simplicity, use average blending for now
    # Linear blending would compute distance transforms for weighting
    logger.warning("Linear blending not fully implemented, using average")
    return blend_average(images, translations)


def compute_canvas_bounds(
    images: List[np.ndarray], translations: List[Tuple[float, float]]
) -> Tuple[float, float, float, float]:
    """Compute bounding box for all images.

    Args:
        images: List of images
        translations: List of cumulative translations

    Returns:
        Tuple of (min_x, max_x, min_y, max_y)
    """
    min_x = min_y = float("inf")
    max_x = max_y = float("-inf")

    for img, (tx, ty) in zip(images, translations):
        h, w = img.shape[:2]

        # Corners of this image
        corners_x = [tx, tx + w]
        corners_y = [ty, ty + h]

        min_x = min(min_x, min(corners_x))
        max_x = max(max_x, max(corners_x))
        min_y = min(min_y, min(corners_y))
        max_y = max(max_y, max(corners_y))

    return min_x, max_x, min_y, max_y


def compute_cumulative_translations(
    pairwise_translations: List[Tuple[float, float]],
) -> List[Tuple[float, float]]:
    """Convert pairwise translations to cumulative translations.

    Args:
        pairwise_translations: List of (dx, dy) between adjacent pairs
            where (dx, dy) = pts2 - pts1 (image2 position relative to image1)

    Returns:
        List of cumulative (x, y) positions, starting from (0, 0)

    Note: We negate the translations because RANSAC computes "image2 - image1",
          but for stitching we need "where to place image1 relative to image2".

          For HORIZONTAL panorama (cylinder wraps around Y-axis):
          - We accumulate Y translations (vertical stitching)
          - We ignore X translations (horizontal should align after warping)
    """
    cumulative = [(0.0, 0.0)]  # First image at origin

    current_x, current_y = 0.0, 0.0
    for dx, dy in pairwise_translations:
        # Negate because RANSAC gives us (img2 - img1) but we need placement offset
        # For horizontal panorama, accumulate Y (vertical) translation
        current_y -= dy
        # Ignore horizontal translation for cylindrical panoramas
        # current_x -= dx
        cumulative.append((current_x, current_y))

    return cumulative
