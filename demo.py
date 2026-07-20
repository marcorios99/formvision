"""Run the public FormVision batch demonstration."""

from pathlib import Path

from formvision.evaluation.demo_batch import DemoInputError, run_demo_batch


def main() -> int:
    root = Path(__file__).resolve().parent
    report_path = root / "data" / "outputs" / "demo" / "report.json"
    try:
        report = run_demo_batch(root, report_path)
    except DemoInputError as error:
        print("FormVision demo input error: {0}".format(error))
        return 1
    summary = report["summary"]
    print("FormVision demo")
    print("Processed forms: {0}/{1}".format(summary["forms_processed"], summary["forms_total"]))
    print("QR accuracy: {0}/{1} ({2:.2%})".format(summary["qr"]["correct"], summary["qr"]["total"], summary["qr"]["accuracy"]))
    print("OMR accuracy: {0}/{1} ({2:.2%})".format(summary["omr"]["correct"], summary["omr"]["total"], summary["omr"]["accuracy"]))
    print("OCR: not evaluated (demo engine)")
    print("ICR: not evaluated (demo engine)")
    print("Report: {0}".format(report_path.relative_to(root).as_posix()))
    print("Status: {0}".format("PASS" if summary["passed"] else "FAIL"))
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
