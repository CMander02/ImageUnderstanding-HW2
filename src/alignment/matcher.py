"""Feature matching using FLANN or BFMatcher."""

import logging
from typing import List, Tuple

import cv2
import numpy as np

logger = logging.getLogger(__name__)


def match_features(
    descriptors1: np.ndarray,
    descriptors2: np.ndarray,
    ratio_threshold: float = 0.7,
    use_flann: bool = True,
) -> List[cv2.DMatch]:
    """Match features between two descriptor sets using Lowe's ratio test.

    Args:
        descriptors1: Descriptors from first image
        descriptors2: Descriptors from second image
        ratio_threshold: Lowe's ratio test threshold (0.7-0.8 typical)
        use_flann: Use FLANN matcher (faster) vs BFMatcher

    Returns:
        List of good matches (cv2.DMatch objects)
    """
    if descriptors1 is None or descriptors2 is None:
        logger.warning("One or both descriptor sets are None")
        return []

    if use_flann:
        # FLANN parameters
        FLANN_INDEX_KDTREE = 1
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=50)
        matcher = cv2.FlannBasedMatcher(index_params, search_params)
    else:
        # BFMatcher with L2 norm for SIFT
        matcher = cv2.BFMatcher(cv2.NORM_L2, crossCheck=False)

    # Find 2 nearest neighbors for each descriptor
    matches = matcher.knnMatch(descriptors1, descriptors2, k=2)

    # Apply Lowe's ratio test
    good_matches = []
    for match_pair in matches:
        if len(match_pair) == 2:
            m, n = match_pair
            if m.distance < ratio_threshold * n.distance:
                good_matches.append(m)

    logger.info(
        f"Found {len(good_matches)} good matches out of {len(matches)} "
        f"(ratio={ratio_threshold})"
    )

    return good_matches


def extract_match_points(
    keypoints1: List,
    keypoints2: List,
    matches: List[cv2.DMatch],
) -> Tuple[np.ndarray, np.ndarray]:
    """Extract matched point coordinates from keypoints and matches.

    Args:
        keypoints1: Keypoints from first image
        keypoints2: Keypoints from second image
        matches: List of matches

    Returns:
        Tuple of (points1, points2) as Nx2 arrays
    """
    pts1 = np.float32([keypoints1[m.queryIdx].pt for m in matches])
    pts2 = np.float32([keypoints2[m.trainIdx].pt for m in matches])

    return pts1, pts2
