from dataclasses import dataclass

import cv2
import numpy as np


@dataclass(frozen=True)
class ScanSimulationConfig:
    max_rotation_degrees: float = 1.5
    max_shift_pixels: int = 8
    noise_sigma: float = 3.0


class ScanSimulator:
    """Applies mild scan-like rotation, translation and sensor noise."""

    def __init__(self, config: ScanSimulationConfig | None = None) -> None:
        self.config = config or ScanSimulationConfig()

    def apply(self, image: np.ndarray, seed: int | None = None) -> np.ndarray:
        rng = np.random.default_rng(seed)
        height, width = image.shape[:2]
        angle = float(rng.uniform(-self.config.max_rotation_degrees, self.config.max_rotation_degrees))
        shift_x = int(rng.integers(-self.config.max_shift_pixels, self.config.max_shift_pixels + 1))
        shift_y = int(rng.integers(-self.config.max_shift_pixels, self.config.max_shift_pixels + 1))

        matrix = cv2.getRotationMatrix2D((width / 2, height / 2), angle, 1.0)
        matrix[0, 2] += shift_x
        matrix[1, 2] += shift_y
        rotated = cv2.warpAffine(
            image,
            matrix,
            (width, height),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(255, 255, 255),
        )

        noise = rng.normal(0, self.config.noise_sigma, rotated.shape).astype(np.float32)
        noisy = rotated.astype(np.float32) + noise
        return np.clip(noisy, 0, 255).astype(np.uint8)
