from pathlib import Path

import cv2
import numpy as np


class DigitStripFactory:
    """Creates a standalone image by composing digit PNG samples."""

    def create_random_strip(
        self,
        digits_dir: str | Path = "data/digits",
        output_path: str | Path = "data/outputs/random_digit_strip.png",
        length: int = 8,
        seed: int | None = None,
    ) -> tuple[Path, str]:
        rng = np.random.default_rng(seed)
        digits = "".join(str(int(value)) for value in rng.integers(0, 10, size=length))
        canvas = self.compose_strip(digits, digits_dir, rng)

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(output), canvas)
        return output, digits

    def compose_strip(
        self,
        digits: str,
        digits_dir: str | Path = "data/digits",
        rng: np.random.Generator | None = None,
    ) -> np.ndarray:
        rng = rng or np.random.default_rng()
        images = [self._pick_digit_image(Path(digits_dir), digit, rng) for digit in digits]

        height = max(image.shape[0] for image in images) + 24
        gap = 12
        width = sum(image.shape[1] for image in images) + gap * (len(images) - 1) + 40
        canvas = np.full((height, width, 3), 255, dtype=np.uint8)

        cursor = 20
        for image in images:
            y = (height - image.shape[0]) // 2 + int(rng.integers(-3, 4))
            y = max(0, min(height - image.shape[0], y))
            canvas[y : y + image.shape[0], cursor : cursor + image.shape[1]] = image
            cursor += image.shape[1] + gap
        return canvas

    def _pick_digit_image(
        self,
        digits_dir: Path,
        digit: str,
        rng: np.random.Generator,
    ) -> np.ndarray:
        candidates = sorted((digits_dir / digit).glob("*.png"))
        if not candidates:
            raise FileNotFoundError(f"No PNG samples found for digit {digit} in {digits_dir}")
        path = candidates[int(rng.integers(0, len(candidates)))]
        image = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if image is None:
            raise FileNotFoundError(f"Could not read digit sample: {path}")
        return image
