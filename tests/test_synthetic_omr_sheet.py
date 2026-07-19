import json
from pathlib import Path

from formvision.layout.synthetic_templates import SyntheticOmrSheetFactory


def test_synthetic_omr_sheet_generates_image_and_layout(tmp_path: Path):
    image_path = tmp_path / "sheet.png"
    layout_path = tmp_path / "sheet.json"

    SyntheticOmrSheetFactory().create_sheet(
        image_path=image_path,
        layout_path=layout_path,
        questions=6,
        options=("A", "B", "C", "D"),
        student_code="random",
        seed=7,
    )

    layout = json.loads(layout_path.read_text(encoding="utf-8"))

    assert image_path.exists()
    assert layout["template_id"] == "synthetic_omr_v1"
    assert len(layout["fields"]) == 10
    assert layout["fields"][-1]["type"] == "omr"
