"""Cylindrical warping for panorama stitching."""

import logging

import cv2
import numpy as np

logger = logging.getLogger(__name__)


def warp_cylindrical(
    image: np.ndarray, focal_length: float, center: tuple = None
) -> np.ndarray:
    """Warp image to cylindrical coordinates using backward mapping.

    HORIZONTAL panorama (camera rotating horizontally around Y-axis):

    The key insight: We're warping in the HORIZONTAL direction (Y stays relatively unchanged).

    For each pixel in OUTPUT cylindrical image (x_cyl, y_cyl):
        1. Compute angles:
           θ = (y_cyl - yc) / f  (vertical angle - but this creates HORIZONTAL panorama!)
           w = (x_cyl - xc) / f  (horizontal offset, normalized)

        2. Convert to 3D cylinder coordinates:
           x̂ = w
           ŷ = sin(θ)
           ẑ = cos(θ)

        3. Project back to planar image:
           x = f * x̂/ẑ + xc = f * w/cos(θ) + xc
           y = f * ŷ/ẑ + yc = f * sin(θ)/cos(θ) + yc = f * tan(θ) + yc

    Args:
        image: Input image (BGR)
        focal_length: Camera focal length in pixels
        center: Image center (xc, yc). If None, uses image center.

    Returns:
        Warped image in cylindrical coordinates
    """
    h, w = image.shape[:2]

    # Use image center if not specified
    if center is None:
        xc, yc = w / 2.0, h / 2.0
    else:
        xc, yc = center

    logger.debug(
        f"Warping image {w}x{h} with focal_length={focal_length}, "
        f"center=({xc}, {yc})"
    )

    # Create coordinate maps for the output (cylindrical) image
    # For each pixel in output, find where it came from in input
    map_x = np.zeros((h, w), dtype=np.float32)
    map_y = np.zeros((h, w), dtype=np.float32)

    for y_cyl in range(h):
        for x_cyl in range(w):
            # HORIZONTAL panorama: swap the roles of x and y!
            # The cylinder wraps around the Y-axis (vertical)
            theta = (y_cyl - yc) / focal_length  # Vertical angle
            w_normalized = (x_cyl - xc) / focal_length  # Horizontal offset (normalized)

            # Source position in planar image
            # x = f * w / cos(θ) + xc
            x_planar = focal_length * w_normalized / np.cos(theta) + xc
            # y = f * tan(θ) + yc
            y_planar = focal_length * np.tan(theta) + yc

            # Store mapping
            map_x[y_cyl, x_cyl] = x_planar
            map_y[y_cyl, x_cyl] = y_planar

    # Apply remap with bilinear interpolation
    warped = cv2.remap(
        image, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT
    )

    logger.debug("Cylindrical warping completed")
    return warped


def estimate_focal_length_from_exif(
    exif_data: dict, image_width: int, sensor_width_mm: float = None
) -> float:
    """Estimate focal length in pixels from EXIF data.

    Estimation formula:
        focal_length_pixels = focal_length_mm * (image_width_pixels / sensor_width_mm)

    Common sensor widths (35mm equivalent crop factor):
        - Full Frame (35mm): 36mm
        - APS-C Canon: 22.3mm
        - APS-C Nikon/Sony: 23.6mm
        - Micro Four Thirds: 17.3mm
        - 1" sensor: 13.2mm

    Args:
        exif_data: EXIF dictionary
        image_width: Image width in pixels
        sensor_width_mm: Sensor width in mm. If None, uses 35mm equivalent estimation.

    Returns:
        Focal length in pixels, or None if estimation failed
    """
    if "FocalLengthValue" not in exif_data:
        logger.info("No focal length found in EXIF data")
        return None

    focal_mm = exif_data["FocalLengthValue"]
    logger.info(f"EXIF focal length: {focal_mm:.1f}mm (physical)")

    # Try to determine sensor width
    if sensor_width_mm is None:
        # Try to estimate from FocalLengthIn35mmFilm if available
        if "FocalLengthIn35mmFilm" in exif_data:
            focal_35mm = exif_data["FocalLengthIn35mmFilm"]
            if focal_35mm and focal_35mm > 0:
                # Crop factor = focal_35mm / focal_mm
                crop_factor = focal_35mm / focal_mm
                # sensor_width_mm = 36mm / crop_factor
                sensor_width_mm = 36.0 / crop_factor
                logger.info(
                    f"Estimated sensor width from EXIF 35mm equivalent: "
                    f"{sensor_width_mm:.1f}mm (crop factor: {crop_factor:.2f})"
                )

        # Fallback: assume APS-C sensor (most common for consumer cameras)
        if sensor_width_mm is None:
            sensor_width_mm = 23.6  # APS-C default
            logger.warning(
                f"Sensor width unknown, assuming APS-C sensor: {sensor_width_mm}mm "
                f"(this may be inaccurate!)"
            )

    # Calculate focal length in pixels
    focal_pixels = focal_mm * (image_width / sensor_width_mm)
    logger.info(
        f"Estimated focal length from EXIF: {focal_pixels:.1f} pixels "
        f"(focal={focal_mm:.1f}mm, sensor={sensor_width_mm:.1f}mm, width={image_width}px)"
    )

    return focal_pixels
