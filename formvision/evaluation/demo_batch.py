"""Batch evaluation for the public OMR admission demonstration."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from formvision.layout.template_loader import TemplateLoader
from formvision.pipeline.processor import FormProcessingPipeline


class DemoInputError(ValueError):
    """Raised when the fixed public demo input set is incomplete or inconsistent."""


def discover_demo_inputs(repo_root: Path) -> dict[str, Any]:
    """Locate and validate the fixed set of public demo inputs."""
    demo_root = repo_root / "demo" / "omr_admission"
    template_image = demo_root / "template" / "template.png"
    layout = demo_root / "template" / "layout.json"
    scanned_directory = demo_root / "images" / "scanned"
    expected_directory = demo_root / "expected"
    for path, label in ((template_image, "template.png"), (layout, "layout.json")):
        if not path.is_file():
            raise DemoInputError("Required demo input is missing: {0}".format(label))
    if not scanned_directory.is_dir() or not expected_directory.is_dir():
        raise DemoInputError("Required demo directories are missing")
    scanned = sorted(scanned_directory.glob("student_*.png"))
    expected = sorted(expected_directory.glob("student_*.json"))
    if len(scanned) != 10:
        raise DemoInputError("Expected exactly 10 scanned forms, found {0}".format(len(scanned)))
    scanned_stems = {path.stem for path in scanned}
    # ``student_batch.json`` is a batch manifest, not an expected form pair.
    expected_stems = {path.stem for path in expected if path.stem in scanned_stems}
    missing_expected = sorted(scanned_stems - expected_stems)
    unexpected_expected = sorted(expected_stems - scanned_stems)
    if missing_expected or unexpected_expected:
        raise DemoInputError("Scanned/expected pairs do not match: missing={0}; unexpected={1}".format(missing_expected, unexpected_expected))
    return {
        "template_image": template_image, "layout": layout,
        "scanned_directory": scanned_directory, "expected_directory": expected_directory,
        "pairs": [(image, expected_directory / (image.stem + ".json")) for image in scanned],
    }


def run_demo_batch(repo_root: Path, output_path: Path | None = None) -> dict[str, Any]:
    """Run the demo once and write a deterministic, human-readable JSON report."""
    repo_root = repo_root.resolve()
    inputs = discover_demo_inputs(repo_root)
    output_path = (output_path or repo_root / "data" / "outputs" / "demo" / "report.json").resolve()
    template = TemplateLoader().load(inputs["layout"])
    pipeline = FormProcessingPipeline()
    forms, qr_correct, qr_total, omr_correct, omr_total, forms_failed = [], 0, 0, 0, 0, 0
    for image_path, expected_path in inputs["pairs"]:
        form = _base_form(image_path, expected_path, inputs["template_image"], repo_root)
        try:
            expected = _load_expected(expected_path)
            result = pipeline.process(image_path, template, template_image_path=inputs["template_image"], align=True)
            form["processing_status"] = result.status
            qr_match = result.document_id == expected["exam_code"]
            qr_total += 1
            qr_correct += int(qr_match)
            form["qr"] = {"expected": expected["exam_code"], "actual": result.document_id, "barcode_value": result.barcode.value, "template_id": result.template_id, "confidence": result.barcode.confidence, "source": result.barcode.source, "match": qr_match}
            form["omr"] = _compare_omr(expected["answers"], result.fields)
            omr_correct += form["omr"]["correct"]
            omr_total += form["omr"]["total"]
            form["ocr"]["fields"] = _non_evaluated_fields(template, result.fields, expected, "ocr")
            form["icr"]["fields"] = _non_evaluated_fields(template, result.fields, expected, "icr")
        except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
            forms_failed += 1
            form["errors"].append({"type": type(error).__name__, "message": str(error)})
        forms.append(form)
    summary = {"forms_total": len(forms), "forms_processed": len(forms) - forms_failed, "forms_failed": forms_failed, "qr": _metric(qr_correct, qr_total), "omr": _metric(omr_correct, omr_total), "ocr": {"evaluated": False}, "icr": {"evaluated": False}}
    summary["passed"] = forms_failed == 0 and qr_correct == qr_total and omr_correct == omr_total
    report = {"schema_version": "1.0", "demo": "omr_admission", "generated_at": datetime.now(timezone.utc).isoformat(), "inputs": {key: _relative_path(inputs[key], repo_root) for key in ("template_image", "layout", "scanned_directory", "expected_directory")}, "engines": {"qr": "opencv_qr", "omr": "omr", "ocr": "demo_ocr", "icr": "demo_icr"}, "summary": summary, "forms": forms}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report


def _base_form(image_path: Path, expected_path: Path, template_image: Path, root: Path) -> dict[str, Any]:
    placeholder = {"evaluated": False, "reason": "Demo extractor does not perform image recognition.", "fields": {}}
    return {"student_id": image_path.stem, "image": _relative_path(image_path, root), "expected_file": _relative_path(expected_path, root), "processing_status": "failed", "alignment": {"enabled": True, "template_image": _relative_path(template_image, root)}, "qr": None, "omr": None, "ocr": dict(placeholder), "icr": dict(placeholder), "errors": []}


def _load_expected(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _compare_omr(expected_answers: dict[str, Any], fields: dict[str, Any]) -> dict[str, Any]:
    questions, correct = {}, 0
    for field_id in sorted(expected_answers):
        field, match = fields[field_id], fields[field_id].value == expected_answers[field_id]
        correct += int(match)
        questions[field_id] = {"expected": expected_answers[field_id], "actual": field.value, "match": match, "confidence": field.confidence, "source": field.source, "valid": field.valid, "issues": field.issues}
    total = len(questions)
    return {"correct": correct, "total": total, "accuracy": correct / total if total else 0.0, "questions": questions}


def _non_evaluated_fields(template: Any, fields: dict[str, Any], expected: dict[str, Any], field_type: str) -> dict[str, Any]:
    values = {}
    for field in sorted(template.fields, key=lambda item: item.id):
        if field.type == field_type:
            result = fields[field.id]
            values[field.id] = {"expected": expected.get(field.id), "actual": result.value, "source": result.source}
    return values


def _metric(correct: int, total: int) -> dict[str, Any]:
    return {"correct": correct, "total": total, "accuracy": correct / total if total else 0.0}


def _relative_path(path: Path, repo_root: Path) -> str:
    return path.resolve().relative_to(repo_root).as_posix()
