"""Image I/O utilities."""

import logging
from pathlib import Path
from typing import List, Tuple

import cv2
import numpy as np
from PIL import Image
from PIL.ExifTags import TAGS

logger = logging.getLogger(__name__)


def load_images(image_dir: Path) -> List[Tuple[np.ndarray, str, dict]]:
    """Load all images from directory with EXIF data.

    Args:
        image_dir: Directory containing images

    Returns:
        List of tuples: (image_array, filename, exif_data)
    """
    image_dir = Path(image_dir)
    if not image_dir.exists():
        raise FileNotFoundError(f"Image directory not found: {image_dir}")

    # Find all image files
    image_extensions = {".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"}
    image_files = sorted(
        [f for f in image_dir.iterdir() if f.suffix in image_extensions],
        reverse=True  # Reverse order: higher numbered images are on the left
    )

    if not image_files:
        raise ValueError(f"No images found in {image_dir}")

    logger.info(f"Found {len(image_files)} images in {image_dir}")

    images = []
    for img_path in image_files:
        # Load image with OpenCV
        img = cv2.imread(str(img_path))
        if img is None:
            logger.warning(f"Failed to load image: {img_path}")
            continue

        # Extract EXIF data
        exif_data = extract_exif(img_path)

        # Note: Do NOT apply EXIF orientation if images were manually pre-rotated
        # img = apply_exif_orientation(img, exif_data)

        images.append((img, img_path.name, exif_data))
        logger.debug(f"Loaded {img_path.name}: {img.shape}")

    logger.info(f"Successfully loaded {len(images)} images")
    return images


def extract_exif(image_path: Path) -> dict:
    """Extract EXIF data from image.

    Args:
        image_path: Path to image file

    Returns:
        Dictionary with EXIF data (focal_length, width, height, etc.)
    """
    exif_data = {}

    try:
        with Image.open(image_path) as img:
            exif = img._getexif()
            if exif is not None:
                for tag_id, value in exif.items():
                    tag = TAGS.get(tag_id, tag_id)
                    exif_data[tag] = value

                # Extract focal length
                if "FocalLength" in exif_data:
                    focal = exif_data["FocalLength"]
                    # Handle tuple format (numerator, denominator)
                    if isinstance(focal, tuple):
                        exif_data["FocalLengthValue"] = focal[0] / focal[1]
                    else:
                        exif_data["FocalLengthValue"] = float(focal)

                # Extract image dimensions
                exif_data["ImageWidth"] = img.width
                exif_data["ImageHeight"] = img.height

    except Exception as e:
        logger.warning(f"Failed to extract EXIF from {image_path}: {e}")

    return exif_data


def apply_exif_orientation(image: np.ndarray, exif_data: dict) -> np.ndarray:
    """Apply EXIF orientation to correct image rotation.

    EXIF Orientation values:
        1 = Normal (0°)
        3 = Rotate 180°
        6 = Rotate 90° CW (or 270° CCW)
        8 = Rotate 270° CW (or 90° CCW)

    Args:
        image: Input image
        exif_data: EXIF dictionary with 'Orientation' key

    Returns:
        Rotated image according to EXIF orientation
    """
    if "Orientation" not in exif_data:
        return image

    orientation = exif_data["Orientation"]

    if orientation == 1:
        # Normal, no rotation needed
        return image
    elif orientation == 3:
        # Rotate 180°
        return cv2.rotate(image, cv2.ROTATE_180)
    elif orientation == 6:
        # Rotate 90° clockwise
        return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    elif orientation == 8:
        # Rotate 270° clockwise (or 90° counter-clockwise)
        return cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
    else:
        logger.warning(f"Unknown EXIF orientation value: {orientation}")
        return image


def save_image(image: np.ndarray, output_path: Path, quality: int = 95) -> None:
    """Save image to file.

    Args:
        image: Image array (BGR or grayscale)
        output_path: Output file path
        quality: JPEG quality (1-100)
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.suffix.lower() in [".jpg", ".jpeg"]:
        cv2.imwrite(str(output_path), image, [cv2.IMWRITE_JPEG_QUALITY, quality])
    else:
        cv2.imwrite(str(output_path), image)

    logger.debug(f"Saved image to {output_path}")
