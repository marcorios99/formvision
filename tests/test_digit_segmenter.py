import cv2
import numpy as np

from formvision.extractors.icr import DigitSegmenter


def test_digit_segmenter_orders_candidates_left_to_right():
    roi = np.full((72, 180, 3), 255, dtype=np.uint8)
    cv2.putText(roi, "123", (12, 52), cv2.FONT_HERSHEY_SIMPLEX, 1.6, (20, 20, 20), 3)

    candidates = DigitSegmenter().segment(roi)

    assert len(candidates) == 3
    assert [candidate.image.shape for candidate in candidates] == [(28, 28)] * 3
    assert [candidate.bbox[0] for candidate in candidates] == sorted(
        candidate.bbox[0] for candidate in candidates
    )
