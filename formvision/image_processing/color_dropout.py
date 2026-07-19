import cv2
import numpy as np


class MagentaDropout:
    """Removes light magenta guide marks while preserving dark handwriting/marks."""

    def apply(self, image: np.ndarray) -> np.ndarray:
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower = np.array([135, 35, 80], dtype=np.uint8)
        upper = np.array([175, 255, 255], dtype=np.uint8)
        mask = cv2.inRange(hsv, lower, upper)
        cleaned = image.copy()
        cleaned[mask > 0] = (255, 255, 255)
        return cleaned
