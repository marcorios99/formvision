from pathlib import Path

import numpy as np

from formvision.extractors.base import Extraction
from formvision.extractors.icr.base import IcrEngine
from formvision.extractors.icr.digit_segmenter import DigitSegmenter


class MnistDigitIcrEngine(IcrEngine):
    """Reads separated numeric handwriting with segmentation and MNIST prototypes."""

    nearest_neighbors = 25
    confidence_temperature = 0.035

    def __init__(
        self,
        model_path: str | Path = "formvision/models/mnist_digit_prototypes.npz",
        segmenter: DigitSegmenter | None = None,
    ) -> None:
        path = Path(model_path)
        if not path.exists():
            raise FileNotFoundError(
                f"ICR model not found at {path}. Run training/train_mnist_digit.py first."
            )
        data = np.load(path)
        self.prototypes = data["prototypes"].astype(np.float32)
        self.labels = data["labels"].astype(str)
        self.samples = data["samples"].astype(np.float32) if "samples" in data else self.prototypes
        self.sample_labels = data["sample_labels"].astype(str) if "sample_labels" in data else self.labels
        self.segmenter = segmenter or DigitSegmenter()

    def extract(self, roi, demo_value: str | None = None) -> Extraction:
        candidates = self.segmenter.segment(roi)
        if not candidates:
            return Extraction(value="", confidence=0.0, source="mnist_icr")

        predictions: list[str] = []
        confidences: list[float] = []
        boxes: list[tuple[int, int, int, int]] = []

        for candidate in candidates:
            digit, confidence = self._predict(candidate.image)
            predictions.append(digit)
            confidences.append(confidence)
            boxes.append(candidate.bbox)

        return Extraction(
            value="".join(predictions),
            confidence=float(np.mean(confidences)) if confidences else 0.0,
            source="mnist_icr",
            metadata={
                "boxes": boxes,
                "digit_confidences": confidences,
                "num_segments": len(candidates),
            },
        )

    def _predict(self, image: np.ndarray) -> tuple[str, float]:
        sample = image.astype(np.float32) / 255.0
        references = self.samples.astype(np.float32) / 255.0
        distances = np.mean((references - sample) ** 2, axis=(1, 2))
        order = np.argsort(distances)
        nearest = order[: self.nearest_neighbors]
        nearest_distances = distances[nearest]
        nearest_labels = self.sample_labels[nearest]

        shifted = nearest_distances - float(nearest_distances.min())
        weights = np.exp(-shifted / self.confidence_temperature)
        class_scores: dict[str, float] = {}
        for label, weight in zip(nearest_labels, weights):
            class_scores[str(label)] = class_scores.get(str(label), 0.0) + float(weight)

        total = sum(class_scores.values())
        digit, score = max(class_scores.items(), key=lambda item: item[1])
        confidence = score / total if total else 0.0
        return digit, float(confidence)
