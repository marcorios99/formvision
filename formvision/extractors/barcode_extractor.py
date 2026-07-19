import cv2
import numpy as np

from formvision.extractors.base import Extraction


class BarcodeExtractor:
    """Reads QR codes with OpenCV and leaves room for 1D barcode plugins."""

    def extract(self, image: np.ndarray) -> Extraction:
        detector = cv2.QRCodeDetector()
        value, points, _ = detector.detectAndDecode(image)
        if not value:
            return Extraction(value=None, confidence=0.0, source="opencv_qr")
        return Extraction(
            value=value,
            confidence=1.0,
            source="opencv_qr",
            metadata={"points": points.tolist() if points is not None else None},
        )
