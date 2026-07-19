import cv2
import numpy as np


class ContourDetector:
    """Thin wrapper around OpenCV contour detection."""

    def find_external(self, binary_image: np.ndarray) -> list[np.ndarray]:
        contours, _ = cv2.findContours(
            binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        return list(contours)
