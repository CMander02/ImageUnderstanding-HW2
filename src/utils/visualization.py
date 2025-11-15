"""Visualization utilities."""

import logging
from pathlib import Path
from typing import List, Optional, Tuple

import cv2
import matplotlib.pyplot as plt
import numpy as np

logger = logging.getLogger(__name__)


def show_image(
    image: np.ndarray, title: str = "Image", save_path: Optional[Path] = None
) -> None:
    """Display image using matplotlib.

    Args:
        image: Image array (BGR or grayscale)
        title: Window title
        save_path: Optional path to save visualization
    """
    if len(image.shape) == 3 and image.shape[2] == 3:
        # Convert BGR to RGB for matplotlib
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    else:
        image_rgb = image

    plt.figure(figsize=(12, 8))
    plt.imshow(image_rgb, cmap="gray" if len(image.shape) == 2 else None)
    plt.title(title)
    plt.axis("off")

    if save_path:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, bbox_inches="tight", dpi=150)
        logger.debug(f"Saved visualization to {save_path}")
    else:
        plt.show()

    plt.close()


def plot_features(
    image: np.ndarray,
    keypoints: List,
    title: str = "Features",
    save_path: Optional[Path] = None,
) -> None:
    """Plot detected features on image.

    Args:
        image: Image array (BGR or grayscale)
        keypoints: List of cv2.KeyPoint objects
        title: Plot title
        save_path: Optional path to save visualization
    """
    # Draw keypoints
    img_with_kp = cv2.drawKeypoints(
        image,
        keypoints,
        None,
        flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS,
    )

    show_image(img_with_kp, f"{title} ({len(keypoints)} features)", save_path)


def plot_matches(
    img1: np.ndarray,
    kp1: List,
    img2: np.ndarray,
    kp2: List,
    matches: List,
    title: str = "Feature Matches",
    save_path: Optional[Path] = None,
    max_matches: int = 50,
) -> None:
    """Plot feature matches between two images.

    Args:
        img1: First image (BGR)
        kp1: Keypoints from first image
        img2: Second image (BGR)
        kp2: Keypoints from second image
        matches: List of cv2.DMatch objects
        title: Plot title
        save_path: Optional path to save visualization
        max_matches: Maximum number of matches to display
    """
    # Sort matches by distance and take top N
    matches_sorted = sorted(matches, key=lambda x: x.distance)
    matches_to_draw = matches_sorted[:max_matches]

    # Draw matches
    img_matches = cv2.drawMatches(
        img1,
        kp1,
        img2,
        kp2,
        matches_to_draw,
        None,
        flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS,
    )

    show_image(
        img_matches,
        f"{title} ({len(matches)} total, showing {len(matches_to_draw)})",
        save_path,
    )


def save_match_visualization(
    img1: np.ndarray,
    img2: np.ndarray,
    pts1: np.ndarray,
    pts2: np.ndarray,
    mask: np.ndarray,
    save_path: Path,
) -> None:
    """Save match visualization with inliers highlighted.

    Args:
        img1: First image
        img2: Second image
        pts1: Points in first image
        pts2: Points in second image
        mask: Inlier mask from RANSAC
        save_path: Output path
    """
    # Create side-by-side image
    h1, w1 = img1.shape[:2]
    h2, w2 = img2.shape[:2]
    h = max(h1, h2)
    vis = np.zeros((h, w1 + w2, 3), dtype=np.uint8)

    # Copy images
    vis[:h1, :w1] = img1
    vis[:h2, w1 : w1 + w2] = img2

    # Draw matches
    inliers = mask.ravel() == 1
    for i, (pt1, pt2) in enumerate(zip(pts1, pts2)):
        pt1 = tuple(pt1.astype(int))
        pt2 = tuple((pt2 + [w1, 0]).astype(int))

        if inliers[i]:
            color = (0, 255, 0)  # Green for inliers
            thickness = 2
        else:
            color = (0, 0, 255)  # Red for outliers
            thickness = 1

        cv2.line(vis, pt1, pt2, color, thickness)
        cv2.circle(vis, pt1, 3, color, -1)
        cv2.circle(vis, pt2, 3, color, -1)

    # Save
    save_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(save_path), vis)
    logger.debug(f"Saved match visualization to {save_path}")
