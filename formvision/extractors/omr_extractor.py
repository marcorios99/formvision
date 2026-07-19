import cv2
import numpy as np

from formvision.config.schema import FieldConfig
from formvision.extractors.base import Extraction


class OmrExtractor:
    """Detects the darkest option inside a synthetic multiple-choice ROI."""

    def extract(self, roi: np.ndarray, field: FieldConfig) -> Extraction:
        if not field.options:
            return Extraction(value=None, confidence=0.0, source="omr")

        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape) == 3 else roi
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
        height, width = binary.shape[:2]
        option_width = width // len(field.options)

        scores: dict[str, float] = {}
        for index, option in enumerate(field.options):
            x1 = index * option_width
            x2 = width if index == len(field.options) - 1 else (index + 1) * option_width
            segment = binary[:, x1:x2]
            middle = segment[
                round(height * 0.18) : round(height * 0.78),
                round(segment.shape[1] * 0.18) : round(segment.shape[1] * 0.82),
            ]
            scores[option] = float(np.count_nonzero(middle)) / float(middle.size)

        ordered = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        winner, score = ordered[0]
        runner_up = ordered[1][1] if len(ordered) > 1 else 0.0
        confidence = max(0.0, min(1.0, score - runner_up + score))
        return Extraction(
            value=winner,
            confidence=confidence,
            source="omr",
            metadata={"scores": scores},
        )
