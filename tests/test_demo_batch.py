from pathlib import Path
import shutil

import pytest

from demo.omr_admission.evaluation.demo_batch import DemoInputError, discover_demo_inputs, run_demo_batch
from demo.omr_admission.runtime import DemoRuntime
from formvision.extractors.base import Extraction
from formvision.pipeline.processor import FormProcessingPipeline


ROOT = Path(__file__).resolve().parents[1]


class FakeOcrEngine:
    def extract(self, roi, demo_value=None) -> Extraction:
        return Extraction(value="test ocr", confidence=0.9, source="doctr", metadata={"test": True})


class FakeIcrEngine:
    def extract(self, roi, demo_value=None) -> Extraction:
        return Extraction(value="00000000", confidence=0.8, source="mnist_icr", metadata={"test": True})


def demo_runtime() -> DemoRuntime:
    return DemoRuntime(
        pipeline=FormProcessingPipeline(
            ocr_extractor=FakeOcrEngine(),
            icr_extractor=FakeIcrEngine(),
        )
    )


def test_demo_batch_evaluates_public_scanned_forms(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    assert len(discover_demo_inputs(ROOT)["pairs"]) == 10
    monkeypatch.setattr(
        "demo.omr_admission.evaluation.demo_batch.build_demo_runtime",
        lambda root: pytest.fail("The injected runtime must be used instead of the real runtime."),
    )
    report_path = tmp_path / "report.json"
    report = run_demo_batch(ROOT, report_path, runtime=demo_runtime())
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
    assert "ground_truth_directory" in report["inputs"]
    assert "expected_directory" not in report["inputs"]
    assert report["engines"] == {"qr": "opencv_qr", "omr": "omr", "ocr": "doctr", "icr": "mnist_icr"}
    for form in report["forms"]:
        assert form["alignment"]["enabled"] is True
        assert form["qr"]["expected"] == form["qr"]["actual"]
        assert form["omr"]["total"] == 8
        assert form["ocr"]["evaluated"] is False
        assert form["icr"]["evaluated"] is False
        assert form["ocr"]["fields"]["full_name"]["source"] == "doctr"
        assert form["ocr"]["fields"]["full_name"]["metadata"] == {"test": True}
        assert form["icr"]["fields"]["student_code"]["source"] == "mnist_icr"
        assert not form["errors"]
        assert "ground_truth_file" in form
        assert "expected_file" not in form
        assert "\\" not in form["image"]
        assert not Path(form["image"]).is_absolute()


def test_demo_batch_builds_the_default_runtime_once(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    received_roots = []

    def build_fake_runtime(repo_root: Path) -> DemoRuntime:
        received_roots.append(repo_root)
        return demo_runtime()

    monkeypatch.setattr(
        "demo.omr_admission.evaluation.demo_batch.build_demo_runtime",
        build_fake_runtime,
    )

    report = run_demo_batch(ROOT, tmp_path / "report.json")

    assert received_roots == [ROOT.resolve()]
    assert report["engines"]["ocr"] == "doctr"
    assert report["engines"]["icr"] == "mnist_icr"


def test_discovery_rejects_unexpected_ground_truth_file(tmp_path: Path) -> None:
    demo_root = tmp_path / "demo" / "omr_admission"
    template_dir = demo_root / "template"
    scanned_dir = demo_root / "images" / "scanned"
    ground_truth_dir = demo_root / "ground_truth"
    template_dir.mkdir(parents=True)
    scanned_dir.mkdir(parents=True)
    ground_truth_dir.mkdir(parents=True)
    shutil.copy2(ROOT / "demo" / "omr_admission" / "template" / "template.png", template_dir / "template.png")
    shutil.copy2(ROOT / "demo" / "omr_admission" / "template" / "layout.json", template_dir / "layout.json")
    for index in range(1, 11):
        stem = "student_{0:03d}".format(index)
        (scanned_dir / (stem + ".png")).touch()
        (ground_truth_dir / (stem + ".json")).write_text("{}", encoding="utf-8")
    (ground_truth_dir / "student_011.json").write_text("{}", encoding="utf-8")

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
    report = run_demo_batch(ROOT, report_path, runtime=demo_runtime())

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
    assert report["forms"][4]["ocr"]["reason"] == "The result is not available because form processing did not complete successfully."
    assert report["forms"][4]["icr"]["reason"] == "The result is not available because form processing did not complete successfully."
    assert report_path.parent != tmp_path / "demo"
