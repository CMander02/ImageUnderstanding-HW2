"""SIFT feature extraction."""

import logging
from typing import Tuple

import cv2
import numpy as np

logger = logging.getLogger(__name__)


def extract_sift_features(
    image: np.ndarray,
    n_features: int = 0,
    contrast_threshold: float = 0.04,
    edge_threshold: float = 10,
) -> Tuple[list, np.ndarray]:
    """Extract SIFT features from image.

    Args:
        image: Input image (BGR or grayscale)
        n_features: Number of features (0 = auto)
        contrast_threshold: Contrast threshold for feature detection
        edge_threshold: Edge threshold for feature detection

    Returns:
        Tuple of (keypoints, descriptors)
    """
    # Convert to grayscale if needed
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    # Create SIFT detector
    sift = cv2.SIFT_create(
        nfeatures=n_features,
        contrastThreshold=contrast_threshold,
        edgeThreshold=edge_threshold,
    )

    # Detect and compute
    keypoints, descriptors = sift.detectAndCompute(gray, None)

    logger.info(f"Extracted {len(keypoints)} SIFT features")

    return keypoints, descriptors
