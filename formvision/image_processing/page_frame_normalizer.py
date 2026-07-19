from dataclasses import dataclass

import cv2
import numpy as np


@dataclass(frozen=True)
class FrameNormalizationResult:
    image: np.ndarray
    source_points: np.ndarray
    target_size: tuple[int, int]


class PageFrameNormalizer:
    """Normalizes a form page using four dark square frame markers."""

    def normalize(
        self,
        image: np.ndarray,
        target_width: int,
        target_height: int,
    ) -> FrameNormalizationResult:
        marker_centers = self._locate_marker_centers(image)
        ordered_points = self._order_points(marker_centers)
        destination = np.array(
            [
                [0, 0],
                [target_width - 1, 0],
                [target_width - 1, target_height - 1],
                [0, target_height - 1],
            ],
            dtype=np.float32,
        )
        transform = cv2.getPerspectiveTransform(ordered_points, destination)
        normalized = cv2.warpPerspective(image, transform, (target_width, target_height))
        return FrameNormalizationResult(
            image=normalized,
            source_points=ordered_points,
            target_size=(target_width, target_height),
        )

    def normalize_to_reference(
        self,
        image: np.ndarray,
        reference_image: np.ndarray,
    ) -> FrameNormalizationResult:
        source_points = self._order_points(self._locate_marker_centers(image))
        target_points = self._order_points(self._locate_marker_centers(reference_image))
        target_height, target_width = reference_image.shape[:2]
        transform = cv2.getPerspectiveTransform(source_points, target_points)
        normalized = cv2.warpPerspective(image, transform, (target_width, target_height))
        return FrameNormalizationResult(
            image=normalized,
            source_points=source_points,
            target_size=(target_width, target_height),
        )

    def _locate_marker_centers(self, image: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        _, mask = cv2.threshold(gray, 60, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        candidates: list[np.ndarray] = []
        image_area = image.shape[0] * image.shape[1]
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < image_area * 0.0002 or area > image_area * 0.01:
                continue

            x, y, width, height = cv2.boundingRect(contour)
            aspect_ratio = width / max(1, height)
            fill_ratio = area / float(width * height)
            if not 0.72 <= aspect_ratio <= 1.28:
                continue
            if fill_ratio < 0.62:
                continue

            center = np.array([x + width / 2.0, y + height / 2.0], dtype=np.float32)
            candidates.append(center)

        if len(candidates) < 4:
            raise ValueError("Could not find four page frame markers.")

        return self._choose_corner_candidates(np.array(candidates, dtype=np.float32), image.shape)

    def _choose_corner_candidates(
        self,
        candidates: np.ndarray,
        image_shape: tuple[int, ...],
    ) -> np.ndarray:
        height, width = image_shape[:2]
        corners = np.array(
            [
                [0, 0],
                [width - 1, 0],
                [width - 1, height - 1],
                [0, height - 1],
            ],
            dtype=np.float32,
        )
        selected: list[np.ndarray] = []
        used_indexes: set[int] = set()
        for corner in corners:
            distances = np.linalg.norm(candidates - corner, axis=1)
            for index in np.argsort(distances):
                if int(index) not in used_indexes:
                    used_indexes.add(int(index))
                    selected.append(candidates[int(index)])
                    break
        return np.array(selected, dtype=np.float32)

    def _order_points(self, points: np.ndarray) -> np.ndarray:
        if points.shape != (4, 2):
            raise ValueError("Expected exactly four marker points.")

        sums = points.sum(axis=1)
        diffs = np.diff(points, axis=1).reshape(-1)
        top_left = points[np.argmin(sums)]
        bottom_right = points[np.argmax(sums)]
        top_right = points[np.argmin(diffs)]
        bottom_left = points[np.argmax(diffs)]
        return np.array([top_left, top_right, bottom_right, bottom_left], dtype=np.float32)
