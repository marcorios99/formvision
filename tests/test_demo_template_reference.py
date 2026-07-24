import json
from pathlib import Path

from formvision.extractors.base import Extraction
from formvision.layout.template_loader import TemplateLoader
from formvision.pipeline.processor import FormProcessingPipeline


ROOT = Path(__file__).resolve().parents[1]
DEMO_DIR = ROOT / "demo" / "omr_admission"


class FakeOcrEngine:
    def extract(self, roi):
        return Extraction("recognized text", 1.0, "fake_ocr")


class FakeIcrEngine:
    def extract(self, roi):
        return Extraction("00000000", 1.0, "fake_icr")


def test_scanned_demo_uses_template_reference_and_ground_truth_omr_answers() -> None:
    template_image = DEMO_DIR / "template" / "template.png"
    layout_path = DEMO_DIR / "template" / "layout.json"
    scanned_image = DEMO_DIR / "images" / "scanned" / "student_001.png"
    ground_truth_path = DEMO_DIR / "ground_truth" / "student_001.json"

    assert template_image.is_file()
    assert layout_path.is_file()

    template = TemplateLoader().load(layout_path)
    result = FormProcessingPipeline(
        ocr_extractor=FakeOcrEngine(),
        icr_extractor=FakeIcrEngine(),
    ).process(
        scanned_image,
        template,
        template_image_path=template_image,
        align=True,
    )
    ground_truth = json.loads(ground_truth_path.read_text(encoding="utf-8"))

    assert result.metadata["template_image_path"] == str(template_image)
    assert result.metadata["aligned"] is True
    for field_id, expected_value in ground_truth["answers"].items():
        assert result.fields[field_id].value == expected_value
