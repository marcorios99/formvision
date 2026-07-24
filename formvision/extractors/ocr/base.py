from abc import ABC, abstractmethod

from formvision.extractors.base import Extraction


class OcrEngine(ABC):
    """Contract for OCR engines that read printed text from an ROI."""

    @abstractmethod
    def extract(self, roi) -> Extraction:
        raise NotImplementedError
