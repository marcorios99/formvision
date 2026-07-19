from pathlib import Path
import struct

import cv2
import numpy as np


class MnistDigitRenderer:
    """Renders digit strings using locally downloaded MNIST samples."""

    def __init__(self, root: str | Path = "data/external/mnist", seed: int | None = None) -> None:
        self.root = Path(root)
        self.rng = np.random.default_rng(seed)
        self._samples_by_digit: dict[int, list[np.ndarray]] | None = None

    def is_available(self) -> bool:
        return (self.root / "MNIST" / "raw" / "train-images-idx3-ubyte").exists()

    def render(self, value: str, height: int = 48) -> np.ndarray:
        samples = self._load_samples()
        glyphs = [self._prepare_digit(samples[int(digit)], height) for digit in value]
        gap = max(4, height // 9)
        width = sum(glyph.shape[1] for glyph in glyphs) + gap * (len(glyphs) - 1)
        canvas = np.full((height + 8, width), 255, dtype=np.uint8)

        cursor = 0
        for index, glyph in enumerate(glyphs):
            y = 4 + int(self.rng.integers(-2, 3))
            y = max(0, min(canvas.shape[0] - glyph.shape[0], y))
            canvas[y : y + glyph.shape[0], cursor : cursor + glyph.shape[1]] = np.minimum(
                canvas[y : y + glyph.shape[0], cursor : cursor + glyph.shape[1]],
                glyph,
            )
            cursor += glyph.shape[1] + gap
        return cv2.cvtColor(canvas, cv2.COLOR_GRAY2BGR)

    def _load_samples(self) -> dict[int, list[np.ndarray]]:
        if self._samples_by_digit is not None:
            return self._samples_by_digit

        raw_samples = self._load_idx_samples()
        if raw_samples is not None:
            self._samples_by_digit = raw_samples
            return raw_samples

        try:
            from torchvision.datasets import MNIST
        except ImportError as exc:
            raise RuntimeError("torchvision is required to render MNIST digits.") from exc

        if not self.is_available():
            raise FileNotFoundError(f"MNIST dataset not found at {self.root}")

        dataset = MNIST(root=str(self.root), train=True, download=False)
        samples: dict[int, list[np.ndarray]] = {digit: [] for digit in range(10)}
        for image, label in dataset:
            if len(samples[int(label)]) < 80:
                samples[int(label)].append(np.array(image, dtype=np.uint8))
            if all(len(bucket) >= 80 for bucket in samples.values()):
                break
        self._samples_by_digit = samples
        return samples

    def _load_idx_samples(self) -> dict[int, list[np.ndarray]] | None:
        images_path = self.root / "MNIST" / "raw" / "train-images-idx3-ubyte"
        labels_path = self.root / "MNIST" / "raw" / "train-labels-idx1-ubyte"
        if not images_path.exists() or not labels_path.exists():
            return None

        with images_path.open("rb") as images_file:
            magic, count, rows, cols = struct.unpack(">IIII", images_file.read(16))
            if magic != 2051:
                raise ValueError(f"Unexpected MNIST image magic number: {magic}")
            image_data = np.frombuffer(images_file.read(), dtype=np.uint8)
            images = image_data.reshape(count, rows, cols)

        with labels_path.open("rb") as labels_file:
            magic, label_count = struct.unpack(">II", labels_file.read(8))
            if magic != 2049:
                raise ValueError(f"Unexpected MNIST label magic number: {magic}")
            labels = np.frombuffer(labels_file.read(), dtype=np.uint8)
            if label_count != count:
                raise ValueError("MNIST images and labels have different counts.")

        samples: dict[int, list[np.ndarray]] = {digit: [] for digit in range(10)}
        indexes = self.rng.permutation(count)
        for index in indexes:
            label = int(labels[index])
            if len(samples[label]) < 80:
                samples[label].append(images[index].copy())
            if all(len(bucket) >= 80 for bucket in samples.values()):
                break
        return samples

    def _prepare_digit(self, digit_samples: list[np.ndarray], height: int) -> np.ndarray:
        source = digit_samples[int(self.rng.integers(0, len(digit_samples)))]
        ys, xs = np.where(source > 20)
        if len(xs) and len(ys):
            source = source[max(0, ys.min() - 1) : ys.max() + 2, max(0, xs.min() - 1) : xs.max() + 2]

        target_height = int(height + self.rng.integers(-4, 5))
        scale = target_height / source.shape[0]
        target_width = max(8, int(source.shape[1] * scale))
        resized = cv2.resize(source, (target_width, target_height), interpolation=cv2.INTER_CUBIC)

        angle = float(self.rng.uniform(-8, 8))
        matrix = cv2.getRotationMatrix2D((target_width / 2, target_height / 2), angle, 1.0)
        rotated = cv2.warpAffine(
            resized,
            matrix,
            (target_width, target_height),
            flags=cv2.INTER_LINEAR,
            borderValue=0,
        )

        alpha = np.clip(rotated.astype(np.float32) / 255.0, 0.0, 1.0)
        ink = 18 + int(self.rng.integers(0, 22))
        return (255 * (1.0 - alpha) + ink * alpha).astype(np.uint8)
