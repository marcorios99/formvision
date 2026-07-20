import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from synthetic.digit_strip import DigitStripFactory
from synthetic.form_overlay import FormOverlay
from synthetic.mnist_exporter import MnistDigitExporter
from synthetic.synthetic_templates import SyntheticOmrSheetFactory


def main() -> None:
    digits_dir = Path("data/digits")
    template_dir = Path("demo/omr_admission/template")
    outputs_dir = Path("data/outputs/digit_overlay_example")
    exam_code = "EXAM-2026-MATH-A-REGION-07-BATCH-042"
    full_name = "ANA TORRES"
    exam_date = "2026-06-12"
    answers = {
        1: "C",
        2: "D",
        3: "A",
        4: "B",
        5: "C",
        6: "D",
        7: "A",
        8: "B",
    }

    MnistDigitExporter().export_digits(output_dir=digits_dir, samples_per_digit=5)

    digit_strip_path, digit_value = DigitStripFactory().create_random_strip(
        digits_dir=digits_dir,
        output_path=outputs_dir / "student_code_strip.png",
        length=8,
    )

    base_form_path = template_dir / "template.png"
    layout_path = template_dir / "layout.json"
    SyntheticOmrSheetFactory().create_sheet(
        image_path=base_form_path,
        layout_path=layout_path,
        document_id=exam_code,
        questions=8,
        student_code="",
        full_name="",
        exam_date="",
        signature="",
        fill_answers=False,
    )

    overlay = FormOverlay()
    student_code_form_path = outputs_dir / "01_with_student_code.png"
    name_form_path = outputs_dir / "02_with_full_name.png"
    date_form_path = outputs_dir / "03_with_exam_date.png"
    final_form_path = outputs_dir / "omr_sheet_final_example.png"

    FormOverlay().paste_image(
        form_path=base_form_path,
        overlay_path=digit_strip_path,
        output_path=student_code_form_path,
        x=95,
        y=270,
        width=335,
        height=72,
    )
    overlay.paste_text(
        form_path=student_code_form_path,
        output_path=name_form_path,
        text=full_name,
        x=470,
        y=270,
        width=560,
        height=72,
        font_scale=0.78,
    )
    overlay.paste_text(
        form_path=name_form_path,
        output_path=date_form_path,
        text=exam_date,
        x=95,
        y=390,
        width=260,
        height=68,
        font_scale=0.72,
    )
    overlay.mark_omr_answers(
        form_path=date_form_path,
        output_path=final_form_path,
        answers=answers,
    )

    metadata = {
        "exam_code": exam_code,
        "student_code": digit_value,
        "full_name": full_name,
        "exam_date": exam_date,
        "answers": {f"question_{key:02d}": value for key, value in answers.items()},
        "digits_dir": str(digits_dir),
        "digit_strip": str(digit_strip_path),
        "base_form": str(base_form_path),
        "layout": str(layout_path),
        "input_image": str(final_form_path),
        "student_code_roi": {"x": 95, "y": 270, "width": 335, "height": 72},
    }
    metadata_path = outputs_dir / "example_metadata.json"
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print(f"Student code: {digit_value}")
    print(f"Exam code: {exam_code}")
    print(f"Digits: {digits_dir}")
    print(f"Digit strip: {digit_strip_path}")
    print(f"Base form: {base_form_path}")
    print(f"Input image: {final_form_path}")
    print(f"Metadata: {metadata_path}")


if __name__ == "__main__":
    main()
