import json
from pathlib import Path

from formvision.layout.template_loader import TemplateLoader
from formvision.pipeline.processor import FormProcessingPipeline


ROOT = Path(__file__).resolve().parents[1]
DEMO_DIR = ROOT / "demo" / "omr_admission"


def test_scanned_demo_uses_template_reference_and_expected_omr_answers() -> None:
    template_image = DEMO_DIR / "template" / "template.png"
    layout_path = DEMO_DIR / "template" / "layout.json"
    scanned_image = DEMO_DIR / "images" / "scanned" / "student_001.png"
    expected_path = DEMO_DIR / "expected" / "student_001.json"

    assert template_image.is_file()
    assert layout_path.is_file()

    template = TemplateLoader().load(layout_path)
    result = FormProcessingPipeline().process(
        scanned_image,
        template,
        template_image_path=template_image,
        align=True,
    )
    expected = json.loads(expected_path.read_text(encoding="utf-8"))

    assert result.metadata["template_image_path"] == str(template_image)
    assert result.metadata["aligned"] is True
    for field_id, expected_value in expected["answers"].items():
        assert result.fields[field_id].value == expected_value
