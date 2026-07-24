from pathlib import Path

from formvision.extractors.base import Extraction
from synthetic.synthetic_templates import SyntheticOmrSheetFactory
from formvision.layout.template_loader import TemplateLoader
from formvision.pipeline.processor import FormProcessingPipeline


class FakeOcrEngine:
    def extract(self, roi):
        return Extraction("recognized text", 1.0, "fake_ocr")


class FakeIcrEngine:
    def extract(self, roi):
        return Extraction("12345678", 1.0, "fake_icr")


def test_pipeline_processes_synthetic_form(tmp_path: Path):
    image_path = tmp_path / "sample.png"
    layout_path = tmp_path / "layout.json"
    SyntheticOmrSheetFactory().create_sheet(
        image_path=image_path,
        layout_path=layout_path,
        questions=8,
    )
    template = TemplateLoader().load(layout_path)

    result = FormProcessingPipeline(
        ocr_extractor=FakeOcrEngine(),
        icr_extractor=FakeIcrEngine(),
    ).process(image_path, template)

    assert result.document_id
    assert result.fields["student_code"].valid
    assert result.fields["question_01"].value == "C"


def test_pipeline_aligns_to_template_before_extraction(tmp_path: Path):
    template_image = tmp_path / "template.png"
    template_layout = tmp_path / "template.json"
    input_image = tmp_path / "student.png"
    input_layout = tmp_path / "student_layout.json"

    factory = SyntheticOmrSheetFactory()
    factory.create_sheet(
        image_path=template_image,
        layout_path=template_layout,
        questions=8,
        student_code="",
        full_name="",
        exam_date="",
        signature="",
        fill_answers=False,
    )
    factory.create_sheet(
        image_path=input_image,
        layout_path=input_layout,
        questions=8,
    )
    template = TemplateLoader().load(input_layout)

    result = FormProcessingPipeline(
        ocr_extractor=FakeOcrEngine(),
        icr_extractor=FakeIcrEngine(),
    ).process(
        input_image,
        template,
        template_image_path=template_image,
        align=True,
    )

    assert result.barcode.value == "OMR-DEMO-0001|synthetic_omr_v1"
    assert result.fields["question_01"].value == "C"
    assert result.fields["question_08"].value == "B"
