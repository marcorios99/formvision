import cv2
import numpy as np

from formvision.image_processing.page_frame_normalizer import PageFrameNormalizer


def test_page_frame_normalizer_returns_target_size():
    image = np.full((500, 360, 3), 255, dtype=np.uint8)
    marker_size = 28
    for x, y in ((20, 20), (312, 20), (312, 452), (20, 452)):
        cv2.rectangle(image, (x, y), (x + marker_size, y + marker_size), (0, 0, 0), -1)

    result = PageFrameNormalizer().normalize(image, target_width=360, target_height=500)

    assert result.image.shape[:2] == (500, 360)
    assert result.source_points.shape == (4, 2)


def test_page_frame_normalizer_can_use_reference_markers():
    reference = np.full((500, 360, 3), 255, dtype=np.uint8)
    image = reference.copy()
    marker_size = 28
    for x, y in ((20, 20), (312, 20), (312, 452), (20, 452)):
        cv2.rectangle(reference, (x, y), (x + marker_size, y + marker_size), (0, 0, 0), -1)
        cv2.rectangle(image, (x, y), (x + marker_size, y + marker_size), (0, 0, 0), -1)

    result = PageFrameNormalizer().normalize_to_reference(image, reference)

    assert result.image.shape == reference.shape
    assert result.source_points.shape == (4, 2)
