from pathlib import Path

from formvision.evaluation.demo_batch import discover_demo_inputs, run_demo_batch


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
