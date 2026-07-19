import json
from pathlib import Path

from formvision.layout.digit_strip import DigitStripFactory
from formvision.layout.form_overlay import FormOverlay
from formvision.layout.mnist_exporter import MnistDigitExporter
from formvision.layout.synthetic_templates import SyntheticOmrSheetFactory


FIRST_NAMES = [
    "ANA",
    "EMILY",
    "MARTA",
    "JAMES",
    "SOFIA",
    "CARLOS",
    "ELENA",
    "OLIVER",
    "VALERIA",
    "MIGUEL",
]
LAST_NAMES = [
    "TORRES",
    "JOHNSON",
    "SALAZAR",
    "SMITH",
    "VARGAS",
    "CASTILLO",
    "PAREDES",
    "WILLIAMS",
    "ROJAS",
    "NAVARRO",
]
OPTIONS = ("A", "B", "C", "D")


def main() -> None:
    digits_dir = Path("data/digits")
    demo_dir = Path("demo/omr_admission")
    template_dir = demo_dir / "template"
    clean_images_dir = demo_dir / "images/clean"
    expected_dir = demo_dir / "expected"

    exam_code = "EXAM-2026-MATH-A-REGION-07-BATCH-042"
    exam_date = "2026-06-12"

    MnistDigitExporter().export_digits(output_dir=digits_dir, samples_per_digit=12)

    base_form_path = template_dir / "blank.png"
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
    strip_factory = DigitStripFactory()
    students = []

    for index in range(10):
        student_number = index + 1
        student_code = f"{student_number:02d}{(student_number * 7919) % 1000000:06d}"
        full_name = f"{FIRST_NAMES[index]} {LAST_NAMES[-index - 1]}"
        answers = {
            question: OPTIONS[(question + index + 1) % len(OPTIONS)]
            for question in range(1, 9)
        }

        strip = strip_factory.compose_strip(student_code, digits_dir=digits_dir)
        step_1 = clean_images_dir / f"_student_{student_number:03d}_code.png"
        step_2 = clean_images_dir / f"_student_{student_number:03d}_name.png"
        step_3 = clean_images_dir / f"_student_{student_number:03d}_date.png"
        image_path = clean_images_dir / f"student_{student_number:03d}.png"

        overlay.paste_image_array(
            form_path=base_form_path,
            overlay=strip,
            output_path=step_1,
            x=95,
            y=270,
            width=335,
            height=72,
        )
        overlay.paste_text(
            form_path=step_1,
            output_path=step_2,
            text=full_name,
            x=470,
            y=270,
            width=560,
            height=72,
            font_scale=0.78,
        )
        overlay.paste_text(
            form_path=step_2,
            output_path=step_3,
            text=exam_date,
            x=95,
            y=390,
            width=260,
            height=68,
            font_scale=0.72,
        )
        overlay.mark_omr_answers(
            form_path=step_3,
            output_path=image_path,
            answers=answers,
        )

        step_1.unlink(missing_ok=True)
        step_2.unlink(missing_ok=True)
        step_3.unlink(missing_ok=True)

        students.append(
            {
                "image": str(image_path),
                "exam_code": exam_code,
                "student_code": student_code,
                "full_name": full_name,
                "exam_date": exam_date,
                "answers": {f"question_{key:02d}": value for key, value in answers.items()},
            }
        )

    expected_dir.mkdir(parents=True, exist_ok=True)
    for student in students:
        image_name = Path(student["image"]).stem
        (expected_dir / f"{image_name}.json").write_text(
            json.dumps(student, indent=2),
            encoding="utf-8",
        )

    manifest_path = expected_dir / "student_batch.json"
    manifest_path.write_text(json.dumps(students, indent=2), encoding="utf-8")

    print(f"Generated {len(students)} student images in {clean_images_dir}")
    print(f"Template: {base_form_path}")
    print(f"Layout: {layout_path}")
    print(f"Students manifest: {manifest_path}")


if __name__ == "__main__":
    main()
