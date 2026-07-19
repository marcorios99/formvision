from abc import ABC, abstractmethod

from formvision.extractors.base import Extraction


class OcrEngine(ABC):
    """Contract for OCR engines that read printed text from an ROI."""

    @abstractmethod
    def extract(self, roi, demo_value: str | None = None) -> Extraction:
        raise NotImplementedError
