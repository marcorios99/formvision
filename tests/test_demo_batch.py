from pathlib import Path
import shutil

import pytest

from demo.omr_admission.evaluation.demo_batch import DemoInputError, discover_demo_inputs, run_demo_batch
from formvision.pipeline.processor import FormProcessingPipeline


ROOT = Path(__file__).resolve().parents[1]


def test_demo_batch_evaluates_public_scanned_forms(tmp_path: Path) -> None:
    assert len(discover_demo_inputs(ROOT)["pairs"]) == 10
    report_path = tmp_path / "report.json"
    report = run_demo_batch(ROOT, report_path)
    assert report_path.is_file()
    assert report["summary"]["forms_processed"] == 10
    assert report["summary"]["forms_failed"] == 0
    assert report["summary"]["qr"] == {"correct": 10, "total": 10, "accuracy": 1.0}
    assert report["summary"]["omr"] == {"correct": 80, "total": 80, "accuracy": 1.0}
    assert report["summary"]["ocr"] == {"evaluated": False}
    assert report["summary"]["icr"] == {"evaluated": False}
    assert report["summary"]["passed"] is True
    assert report["forms"][0]["student_id"] == "student_001"
    assert report["forms"][-1]["student_id"] == "student_010"
    for form in report["forms"]:
        assert form["alignment"]["enabled"] is True
        assert form["qr"]["expected"] == form["qr"]["actual"]
        assert form["omr"]["total"] == 8
        assert form["ocr"]["evaluated"] is False
        assert form["icr"]["evaluated"] is False
        assert not form["errors"]
        assert "\\" not in form["image"]
        assert not Path(form["image"]).is_absolute()


def test_discovery_rejects_unexpected_expected_file(tmp_path: Path) -> None:
    demo_root = tmp_path / "demo" / "omr_admission"
    template_dir = demo_root / "template"
    scanned_dir = demo_root / "images" / "scanned"
    expected_dir = demo_root / "expected"
    template_dir.mkdir(parents=True)
    scanned_dir.mkdir(parents=True)
    expected_dir.mkdir(parents=True)
    shutil.copy2(ROOT / "demo" / "omr_admission" / "template" / "template.png", template_dir / "template.png")
    shutil.copy2(ROOT / "demo" / "omr_admission" / "template" / "layout.json", template_dir / "layout.json")
    for index in range(1, 11):
        stem = "student_{0:03d}".format(index)
        (scanned_dir / (stem + ".png")).touch()
        (expected_dir / (stem + ".json")).write_text("{}", encoding="utf-8")
    (expected_dir / "student_011.json").write_text("{}", encoding="utf-8")

    with pytest.raises(DemoInputError, match="student_011"):
        discover_demo_inputs(tmp_path)


def test_demo_batch_continues_after_form_processing_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    original_process = FormProcessingPipeline.process

    def process_with_one_failure(self, image_path, *args, **kwargs):
        if Path(image_path).stem == "student_005":
            raise RuntimeError("simulated processing failure")
        return original_process(self, image_path, *args, **kwargs)

    monkeypatch.setattr(FormProcessingPipeline, "process", process_with_one_failure)
    report_path = tmp_path / "report.json"
    report = run_demo_batch(ROOT, report_path)

    assert report["summary"]["forms_total"] == 10
    assert report["summary"]["forms_processed"] == 9
    assert report["summary"]["forms_failed"] == 1
    assert report["summary"]["passed"] is False
    assert len(report["forms"]) == 10
    assert report_path.is_file()
    failed = report["forms"][4]
    assert failed["student_id"] == "student_005"
    assert failed["processing_status"] == "failed"
    assert failed["errors"][0]["type"] == "RuntimeError"
    assert "simulated processing failure" in failed["errors"][0]["message"]
    assert [form["student_id"] for form in report["forms"]] == ["student_{0:03d}".format(i) for i in range(1, 11)]
    assert report["forms"][5]["processing_status"] != "failed"
    assert report["forms"][4]["ocr"]["evaluated"] is False
    assert report["forms"][4]["icr"]["evaluated"] is False
    assert report_path.parent != tmp_path / "demo"
