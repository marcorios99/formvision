from types import SimpleNamespace

import numpy as np

from formvision.extractors.ocr.doctr_engine import DoctrOcrEngine


class FakePredictor:
    def __init__(self) -> None:
        self.images = []

    def __call__(self, images):
        self.images.extend(images)
        return SimpleNamespace(pages=[])


def test_doctr_engine_converts_bgr_roi_to_contiguous_rgb(monkeypatch, tmp_path) -> None:
    monkeypatch.delenv("DOCTR_CACHE_DIR", raising=False)
    predictor = FakePredictor()
    engine = DoctrOcrEngine(predictor=predictor, cache_dir=tmp_path / "cache")
    roi = np.array([[[1, 2, 3], [4, 5, 6]]], dtype=np.uint8)

    engine.extract(roi)

    submitted = predictor.images[0]
    assert submitted.tolist() == [[[3, 2, 1], [6, 5, 4]]]
    assert submitted.dtype == np.uint8
    assert submitted.shape == roi.shape
    assert submitted.flags.c_contiguous
    assert roi.tolist() == [[[1, 2, 3], [4, 5, 6]]]


def test_doctr_engine_uses_the_existing_cache_directory(monkeypatch, tmp_path) -> None:
    cache_dir = tmp_path / "existing-cache"
    monkeypatch.setenv("DOCTR_CACHE_DIR", str(cache_dir))
    engine = DoctrOcrEngine(predictor=FakePredictor(), cache_dir=tmp_path / "ignored-cache")

    assert engine.cache_dir == cache_dir
