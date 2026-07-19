from pathlib import Path

import cv2
import numpy as np


class ImageLoader:
    """Loads images as OpenCV BGR arrays."""

    def load(self, image_path: str | Path) -> np.ndarray:
        path = Path(image_path)
        image = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if image is None:
            raise FileNotFoundError(f"Could not read image: {path}")
        return image
