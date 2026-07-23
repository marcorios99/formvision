"""Run the public FormVision demonstration."""

from pathlib import Path

from demo.omr_admission.evaluation.demo_batch import DemoInputError, run_demo_batch
from demo.omr_admission.runtime import DemoEngineError


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    report_path = root / "data" / "outputs" / "demo" / "report.json"
    try:
        report = run_demo_batch(root, report_path)
    except DemoInputError as error:
        print("FormVision demo input error: {0}".format(error))
        return 1
    except DemoEngineError as error:
        print("FormVision demo configuration error: {0}".format(error))
        return 1
    summary = report["summary"]
    engines = report["engines"]
    print("FormVision demo")
    print("Processed forms: {0}/{1}".format(summary["forms_processed"], summary["forms_total"]))
    print("QR accuracy: {0}/{1} ({2:.2%})".format(summary["qr"]["correct"], summary["qr"]["total"], summary["qr"]["accuracy"]))
    print("OMR accuracy: {0}/{1} ({2:.2%})".format(summary["omr"]["correct"], summary["omr"]["total"], summary["omr"]["accuracy"]))
    print("OCR: executed with {0} (not evaluated)".format(engines["ocr"]))
    print("ICR: executed with {0} (not evaluated)".format(engines["icr"]))
    print("Report: {0}".format(report_path.relative_to(root).as_posix()))
    print("Evaluation status: {0} (QR/OMR only)".format("PASS" if summary["passed"] else "FAIL"))
    return 0 if summary["passed"] else 1
