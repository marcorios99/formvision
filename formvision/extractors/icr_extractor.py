from formvision.extractors.base import Extraction
from formvision.extractors.icr.base import IcrEngine


class DemoIcrExtractor(IcrEngine):
    """Deterministic ICR placeholder for handwritten-like numeric fields."""

    def extract(self, _roi, demo_value: str | None = None) -> Extraction:
        value = "12345678" if demo_value is None else demo_value
        return Extraction(value=value, confidence=0.82, source="demo_icr")
