from dataclasses import dataclass

import cv2
import numpy as np


@dataclass(frozen=True)
class DigitCandidate:
    image: np.ndarray
    bbox: tuple[int, int, int, int]


class DigitSegmenter:
    """Segments separated handwritten digits from a constrained numeric ROI."""

    def __init__(
        self,
        min_area_ratio: float = 0.003,
        max_area_ratio: float = 0.35,
        min_height_ratio: float = 0.22,
        output_size: int = 28,
        border_margin: int = 4,
    ) -> None:
        self.min_area_ratio = min_area_ratio
        self.max_area_ratio = max_area_ratio
        self.min_height_ratio = min_height_ratio
        self.output_size = output_size
        self.border_margin = border_margin

    def segment(self, roi: np.ndarray) -> list[DigitCandidate]:
        if roi is None or roi.size == 0:
            return []

        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape) == 3 else roi.copy()
        margin = min(self.border_margin, max(0, min(gray.shape[:2]) // 8))
        if margin and gray.shape[0] > margin * 2 and gray.shape[1] > margin * 2:
            gray = gray[margin:-margin, margin:-margin]
        else:
            margin = 0

        binary = self._binarize(gray)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        height, width = binary.shape[:2]
        min_area = max(8, int(height * width * self.min_area_ratio))
        max_area = int(height * width * self.max_area_ratio)
        min_height = max(6, int(height * self.min_height_ratio))
        boxes: list[tuple[int, int, int, int]] = []

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = cv2.contourArea(contour)
            touches_frame = x <= 1 or y <= 1 or x + w >= width - 1 or y + h >= height - 1
            if area < min_area or area > max_area or h < min_height or touches_frame:
                continue
            boxes.append((x + margin, y + margin, w, h))

        boxes = self._merge_overlapping_boxes(sorted(boxes, key=lambda box: box[0]))
        full_binary = self._binarize(
            cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape) == 3 else roi.copy()
        )
        return [DigitCandidate(self._normalize(full_binary, box), box) for box in boxes]

    def _binarize(self, gray: np.ndarray) -> np.ndarray:
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
        kernel = np.ones((2, 2), dtype=np.uint8)
        return cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

    def _merge_overlapping_boxes(
        self,
        boxes: list[tuple[int, int, int, int]],
    ) -> list[tuple[int, int, int, int]]:
        if not boxes:
            return []

        merged: list[tuple[int, int, int, int]] = [boxes[0]]
        for x, y, w, h in boxes[1:]:
            px, py, pw, ph = merged[-1]
            overlaps = x <= px + pw
            close = x - (px + pw) <= max(2, min(w, pw) // 5)
            if overlaps or close:
                x1 = min(px, x)
                y1 = min(py, y)
                x2 = max(px + pw, x + w)
                y2 = max(py + ph, y + h)
                merged[-1] = (x1, y1, x2 - x1, y2 - y1)
            else:
                merged.append((x, y, w, h))
        return merged

    def _normalize(self, binary: np.ndarray, box: tuple[int, int, int, int]) -> np.ndarray:
        x, y, w, h = box
        pad = 2
        y1 = max(0, y - pad)
        y2 = min(binary.shape[0], y + h + pad)
        x1 = max(0, x - pad)
        x2 = min(binary.shape[1], x + w + pad)
        digit = binary[y1:y2, x1:x2]

        target = self.output_size
        scale = min((target - 8) / max(1, digit.shape[1]), (target - 8) / max(1, digit.shape[0]))
        new_width = max(1, int(round(digit.shape[1] * scale)))
        new_height = max(1, int(round(digit.shape[0] * scale)))
        resized = cv2.resize(digit, (new_width, new_height), interpolation=cv2.INTER_AREA)

        canvas = np.zeros((target, target), dtype=np.uint8)
        x_offset = (target - new_width) // 2
        y_offset = (target - new_height) // 2
        canvas[y_offset : y_offset + new_height, x_offset : x_offset + new_width] = resized
        return canvas
