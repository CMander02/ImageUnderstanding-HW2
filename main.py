"""Main entry point for cylindrical panorama stitching."""

import logging
import sys
from datetime import datetime
from pathlib import Path

from src.config import load_config, print_config
from src.pipeline import PanoramaStitcher


def setup_output_directory():
    """Setup timestamped output directory.

    Returns:
        Tuple of (output_dir, log_file_path)
    """
    # Create outputs directory if not exists
    outputs_root = Path("./outputs")
    outputs_root.mkdir(exist_ok=True)

    # Create timestamped subdirectory
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_dir = outputs_root / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)

    # Setup log file path
    log_file = output_dir / f"{timestamp}.log"

    return output_dir, log_file


def setup_logging(log_file: Path):
    """Setup logging to both console and file.

    Args:
        log_file: Path to log file
    """
    # Create formatters
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # File handler
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)


def main():
    """Main function."""
    try:
        # Setup output directory and logging
        output_dir, log_file = setup_output_directory()
        setup_logging(log_file)

        logger = logging.getLogger(__name__)
        logger.info("=" * 60)
        logger.info("Cylindrical Panorama Stitching")
        logger.info("=" * 60)
        logger.info(f"Output directory: {output_dir}")
        logger.info(f"Log file: {log_file}")
        logger.info("=" * 60)

        # Load configuration
        config = load_config()

        # Override output path with our timestamped directory
        config.output_path = output_dir

        print_config(config)

        # Run stitching pipeline
        stitcher = PanoramaStitcher(config)
        final_panorama = stitcher.run()

        logger.info("")
        logger.info("=" * 60)
        logger.info("SUCCESS!")
        logger.info(f"Final panorama: {final_panorama}")
        logger.info(f"All outputs in: {output_dir}")
        logger.info("=" * 60)

        return 0

    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error("=" * 60)
        logger.error("PIPELINE FAILED")
        logger.error(f"Error: {e}")
        logger.error("=" * 60)
        logger.error("Full traceback:", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
