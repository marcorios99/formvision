from formvision.extractors.base import Extraction
from formvision.extractors.ocr.base import OcrEngine


class DemoOcrExtractor(OcrEngine):
    """Deterministic OCR placeholder for synthetic samples."""

    def extract(self, _roi, demo_value: str | None = None) -> Extraction:
        value = "ANA TORRES" if demo_value is None else demo_value
        return Extraction(value=value, confidence=0.80, source="demo_ocr")
