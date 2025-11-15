"""Cropping utilities for panoramas."""

import logging

import cv2
import numpy as np

logger = logging.getLogger(__name__)


def crop_panorama(image: np.ndarray, threshold: int = 10) -> np.ndarray:
    """Crop black borders from panorama.

    Args:
        image: Panorama image (BGR)
        threshold: Pixel value threshold for considering a pixel as "black"

    Returns:
        Cropped panorama
    """
    if image is None or image.size == 0:
        raise ValueError("Invalid image for cropping")

    # Convert to grayscale for border detection
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    # Find non-black pixels
    non_black = gray > threshold

    # Find bounding box
    rows = np.any(non_black, axis=1)
    cols = np.any(non_black, axis=0)

    if not np.any(rows) or not np.any(cols):
        logger.warning("No non-black pixels found, returning original image")
        return image

    y_min, y_max = np.where(rows)[0][[0, -1]]
    x_min, x_max = np.where(cols)[0][[0, -1]]

    # Crop image
    cropped = image[y_min : y_max + 1, x_min : x_max + 1]

    logger.info(
        f"Cropped from {image.shape[:2]} to {cropped.shape[:2]} "
        f"(removed {y_min}px top, {image.shape[0]-y_max}px bottom, "
        f"{x_min}px left, {image.shape[1]-x_max}px right)"
    )

    return cropped


def find_largest_interior_rectangle(image: np.ndarray, threshold: int = 10) -> tuple:
    """Find the largest rectangle that doesn't contain black borders.

    This is more aggressive than simple crop_panorama and ensures no black pixels.

    Args:
        image: Panorama image (BGR)
        threshold: Pixel value threshold

    Returns:
        Tuple of (x, y, w, h) for the rectangle
    """
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    # Create binary mask
    mask = (gray > threshold).astype(np.uint8) * 255

    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        logger.warning("No valid contours found")
        return (0, 0, image.shape[1], image.shape[0])

    # Find largest contour
    largest_contour = max(contours, key=cv2.contourArea)

    # Get bounding rectangle
    x, y, w, h = cv2.boundingRect(largest_contour)

    logger.debug(f"Largest interior rectangle: ({x}, {y}, {w}, {h})")

    return (x, y, w, h)
