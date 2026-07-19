import os
from pathlib import Path

from formvision.extractors.base import Extraction
from formvision.extractors.ocr.base import OcrEngine


class DoctrOcrEngine(OcrEngine):
    """Optional docTR OCR adapter.

    This adapter is intentionally lazy-loaded so the project can run without
    docTR unless OCR experimentation is explicitly enabled.
    """

    def __init__(
        self,
        det_arch: str = "fast_tiny",
        reco_arch: str = "crnn_mobilenet_v3_small",
        assume_straight_pages: bool = True,
        cache_dir: str | Path = "formvision/models/doctr_cache",
    ) -> None:
        os.environ.setdefault("DOCTR_CACHE_DIR", str(Path(cache_dir)))
        Path(os.environ["DOCTR_CACHE_DIR"]).mkdir(parents=True, exist_ok=True)
        try:
            from doctr.models import ocr_predictor
        except ImportError as exc:
            raise RuntimeError(
                'docTR is not installed. Install it with: pip install -e ".[ocr]"'
            ) from exc
        self.det_arch = det_arch
        self.reco_arch = reco_arch
        self.assume_straight_pages = assume_straight_pages
        self.predictor = ocr_predictor(
            det_arch=det_arch,
            reco_arch=reco_arch,
            pretrained=True,
            assume_straight_pages=assume_straight_pages,
        )

    def extract(self, roi, demo_value: str | None = None) -> Extraction:
        result = self.predictor([roi])
        words: list[str] = []
        confidences: list[float] = []
        for page in result.pages:
            for block in page.blocks:
                for line in block.lines:
                    for word in line.words:
                        words.append(word.value)
                        confidences.append(float(word.confidence))

        if not words:
            return Extraction(value="", confidence=0.0, source="doctr")
        confidence = sum(confidences) / len(confidences)
        return Extraction(
            value=" ".join(words),
            confidence=confidence,
            source="doctr",
            metadata={
                "det_arch": self.det_arch,
                "reco_arch": self.reco_arch,
                "assume_straight_pages": self.assume_straight_pages,
                "words": words,
                "word_confidences": confidences,
            },
        )
