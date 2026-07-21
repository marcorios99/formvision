import numpy as np
import pytest

from formvision.config.schema import FieldConfig, FormTemplate, Rect
from formvision.extractors.base import Extraction
from formvision.pipeline.processor import FormProcessingPipeline


class Loader:
    def load(self, path):
        return np.zeros((2, 2, 3), dtype=np.uint8)


class Mapper:
    def crop_field(self, *args):
        return np.zeros((1, 1, 3), dtype=np.uint8)


class Barcode:
    def extract(self, image):
        return Extraction(None, 0.0, "fake_qr")


def _pipeline(**kwargs) -> FormProcessingPipeline:
    return FormProcessingPipeline(loader=Loader(), mapper=Mapper(), barcode_extractor=Barcode(), **kwargs)


def _template(field_type: str, field_id: str) -> FormTemplate:
    return FormTemplate(
        "template",
        2,
        2,
        (FieldConfig(field_id, field_id, field_type, Rect(0, 0, 1, 1), demo_value="value"),),
    )


def test_pipeline_requires_ocr_engine_for_ocr_field() -> None:
    with pytest.raises(RuntimeError, match="full_name.*ocr_extractor"):
        _pipeline().process("input.png", _template("ocr", "full_name"))


def test_pipeline_requires_icr_engine_for_icr_field() -> None:
    with pytest.raises(RuntimeError, match="student_code.*icr_extractor"):
        _pipeline().process("input.png", _template("icr", "student_code"))


def test_pipeline_processes_field_with_explicit_engine() -> None:
    class Ocr:
        def extract(self, roi, demo_value=None):
            return Extraction("recognized", 1.0, "fake_ocr")

    result = _pipeline(ocr_extractor=Ocr()).process("input.png", _template("ocr", "full_name"))

    assert result.fields["full_name"].value == "recognized"
