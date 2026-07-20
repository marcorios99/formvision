import json
from pathlib import Path

import numpy as np

from formvision.config.schema import FieldConfig, FormTemplate, Rect
from formvision.exporters.json_exporter import JsonExporter
from formvision.extractors.base import Extraction
from formvision.image_processing.page_frame_normalizer import FrameNormalizationResult
from formvision.layout.coordinate_mapper import CoordinateMapper
from formvision.layout.template_loader import TemplateLoader
from formvision.pipeline.processor import FormProcessingPipeline
from formvision.pipeline.result_models import BarcodeResult, FieldResult, FormProcessingResult


def test_template_loader_converts_layout_json_to_schema_objects(tmp_path: Path) -> None:
    layout_path = tmp_path / "layout.json"
    layout_path.write_text(
        json.dumps(
            {
                "template_id": "admission-v1",
                "page_size": {"width": 200, "height": 100},
                "fields": [
                    {
                        "id": "candidate_id",
                        "type": "icr",
                        "roi": {"x": 10, "y": 20, "width": 30, "height": 40},
                        "validators": ["required", "digits:8"],
                        "options": ["unused"],
                        "demo_value": "12345678",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    template = TemplateLoader().load(layout_path)

    assert template == FormTemplate(
        template_id="admission-v1",
        page_width=200,
        page_height=100,
        fields=(
            FieldConfig(
                id="candidate_id",
                label="candidate_id",
                type="icr",
                roi=Rect(x=10, y=20, width=30, height=40),
                validators=("required", "digits:8"),
                options=("unused",),
                demo_value="12345678",
            ),
        ),
    )


def test_coordinate_mapper_scales_and_crops_field_roi() -> None:
    image = np.arange(80, dtype=np.uint8).reshape(8, 10)
    field = FieldConfig("value", "Value", "ocr", Rect(2, 1, 4, 2))

    mapper = CoordinateMapper()
    scaled = mapper.scale_rect(field.roi, template_width=10, template_height=4, image=image)
    crop = mapper.crop_field(image, field, template_width=10, template_height=4)

    assert scaled == Rect(x=2, y=2, width=4, height=4)
    assert np.array_equal(crop, image[2:6, 2:6])


def test_pipeline_aligns_to_supplied_template_and_dispatches_fields_in_type_order() -> None:
    input_image = np.full((4, 4, 3), 10, dtype=np.uint8)
    reference_image = np.full((6, 8, 3), 20, dtype=np.uint8)
    aligned_image = np.full((6, 8, 3), 30, dtype=np.uint8)
    calls: list[object] = []

    class Loader:
        def load(self, path):
            calls.append(("load", str(path)))
            return {"input.png": input_image, "template.png": reference_image}[str(path)]

    class FrameNormalizer:
        def normalize_to_reference(self, image, reference):
            calls.append(("align", image, reference))
            return FrameNormalizationResult(aligned_image, np.zeros((4, 2)), (8, 6))

    class Dropout:
        def apply(self, image):
            calls.append(("dropout", image))
            return image

    class Barcode:
        def extract(self, image):
            calls.append(("barcode", image))
            return Extraction("document-7|template-7", 1.0, "fake_qr")

    class Mapper:
        def crop_field(self, image, field, page_width, page_height):
            calls.append(("crop", field.id, image, page_width, page_height))
            return image

    class Omr:
        def extract(self, roi, field):
            calls.append(("omr", field.id, roi))
            return Extraction("B", 0.9, "fake_omr")

    class Icr:
        def extract(self, roi, demo_value=None):
            calls.append(("icr", demo_value, roi))
            return Extraction(demo_value, 0.8, "fake_icr")

    class Ocr:
        def extract(self, roi, demo_value=None):
            calls.append(("ocr", demo_value, roi))
            return Extraction(demo_value, 0.7, "fake_ocr")

    template = FormTemplate(
        "fallback-template",
        8,
        6,
        (
            FieldConfig("z_ocr", "OCR", "ocr", Rect(0, 0, 1, 1), demo_value="printed"),
            FieldConfig("a_icr", "ICR", "icr", Rect(0, 0, 1, 1), demo_value="123"),
            FieldConfig("b_omr", "OMR", "omr", Rect(0, 0, 1, 1), options=("A", "B")),
        ),
    )
    pipeline = FormProcessingPipeline(
        loader=Loader(),
        frame_normalizer=FrameNormalizer(),
        magenta_dropout=Dropout(),
        barcode_extractor=Barcode(),
        mapper=Mapper(),
        omr_extractor=Omr(),
        icr_extractor=Icr(),
        ocr_extractor=Ocr(),
    )

    result = pipeline.process("input.png", template, template_image_path="template.png", align=True)

    assert [(call[0], call[1]) for call in calls if call[0] == "load"] == [
        ("load", "input.png"),
        ("load", "template.png"),
    ]
    assert [call[:2] for call in calls if call[0] in {"omr", "icr", "ocr"}] == [
        ("omr", "b_omr"),
        ("icr", "123"),
        ("ocr", "printed"),
    ]
    assert all(call[-1] is aligned_image for call in calls if call[0] in {"omr", "icr", "ocr"})
    assert result.document_id == "document-7"
    assert result.template_id == "template-7"
    assert result.status == "processed"
    assert result.fields["b_omr"].value == "B"
    assert result.metadata["aligned"] is True
    assert result.metadata["template_image_path"] == "template.png"


def test_pipeline_includes_validation_issues_in_result() -> None:
    class Loader:
        def load(self, path):
            return np.zeros((2, 2, 3), dtype=np.uint8)

    class Mapper:
        def crop_field(self, *args):
            return np.zeros((1, 1, 3), dtype=np.uint8)

    class Barcode:
        def extract(self, image):
            return Extraction(None, 0.0, "fake_qr")

    class Ocr:
        def extract(self, roi, demo_value=None):
            return Extraction("", 0.5, "fake_ocr")

    template = FormTemplate(
        "template",
        2,
        2,
        (FieldConfig("required_text", "Text", "ocr", Rect(0, 0, 1, 1), validators=("required",)),),
    )
    result = FormProcessingPipeline(
        loader=Loader(), mapper=Mapper(), barcode_extractor=Barcode(), ocr_extractor=Ocr()
    ).process("blank.png", template)

    assert result.document_id == "blank"
    assert result.template_id == "template"
    assert result.status == "processed_with_warnings"
    assert result.fields["required_text"].valid is False
    assert result.fields["required_text"].issues == [
        {"code": "required", "message": "Field is required."}
    ]


def test_json_exporter_serializes_complete_processing_result(tmp_path: Path) -> None:
    result = FormProcessingResult(
        document_id="document-1",
        template_id="template-1",
        status="processed",
        barcode=BarcodeResult("document-1|template-1", "QR_CODE", 1.0, "fake_qr"),
        fields={
            "answer": FieldResult("A", 0.9, "fake_omr", True, [], {"choice": 0}),
        },
        metadata={"aligned": True},
    )

    output_path = JsonExporter().export(result, tmp_path / "nested" / "result.json")

    assert output_path.is_file()
    assert json.loads(output_path.read_text(encoding="utf-8")) == {
        "document_id": "document-1",
        "template_id": "template-1",
        "status": "processed",
        "barcode": {"value": "document-1|template-1", "type": "QR_CODE", "confidence": 1.0, "source": "fake_qr"},
        "fields": {
            "answer": {
                "value": "A",
                "confidence": 0.9,
                "source": "fake_omr",
                "valid": True,
                "issues": [],
                "metadata": {"choice": 0},
            }
        },
        "metadata": {"aligned": True},
    }
