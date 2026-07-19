import cv2
import numpy as np


class ImagePreprocessor:
    """Small set of reusable preprocessing operations for scanned forms."""

    def to_grayscale(self, image: np.ndarray) -> np.ndarray:
        if len(image.shape) == 2:
            return image
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    def binarize(self, image: np.ndarray) -> np.ndarray:
        gray = self.to_grayscale(image)
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        return cv2.threshold(
            blurred, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU
        )[1]

    def crop(self, image: np.ndarray, x: int, y: int, width: int, height: int) -> np.ndarray:
        return image[y : y + height, x : x + width]
