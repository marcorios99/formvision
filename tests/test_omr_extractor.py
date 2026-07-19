import cv2
import numpy as np

from formvision.config.schema import FieldConfig, Rect
from formvision.extractors.omr_extractor import OmrExtractor


def test_omr_extractor_selects_darkest_option():
    roi = np.full((100, 400, 3), 255, dtype=np.uint8)
    for index in range(4):
        cv2.circle(roi, (50 + index * 100, 45), 18, (0, 0, 0), 2)
    cv2.circle(roi, (250, 45), 13, (0, 0, 0), -1)
    field = FieldConfig(
        id="q1",
        label="Question 1",
        type="omr",
        roi=Rect(0, 0, 400, 100),
        options=("A", "B", "C", "D"),
    )

    extraction = OmrExtractor().extract(roi, field)

    assert extraction.value == "C"
    assert extraction.confidence > 0
