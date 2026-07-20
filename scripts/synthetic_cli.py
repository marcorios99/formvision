"""Command-line interface for synthetic repository assets."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from formvision.layout.template_loader import TemplateLoader
from synthetic.digit_strip import DigitStripFactory
from synthetic.form_overlay import FormOverlay
from synthetic.mnist_exporter import MnistDigitExporter
from synthetic.synthetic_templates import SyntheticFormFactory, SyntheticOmrSheetFactory


def main() -> None:
    parser = argparse.ArgumentParser(description="Synthetic form generation CLI.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate = subparsers.add_parser("generate-sample")
    generate.add_argument("--layout", default="demo/omr_admission/template/layout.json")
    generate.add_argument("--output", default="data/outputs/sample_001.png")
    generate.add_argument("--document-id", default="FORM-2026-0001")

    generate_omr = subparsers.add_parser("generate-omr-sheet")
    generate_omr.add_argument("--image-output", default="data/outputs/omr_sheet_001.png")
    generate_omr.add_argument("--layout-output", default="data/outputs/synthetic_omr_sheet.json")
    generate_omr.add_argument("--document-id", default="OMR-DEMO-0001")
    generate_omr.add_argument("--questions", type=int, default=20)
    generate_omr.add_argument("--options", default="A,B,C,D")
    generate_omr.add_argument("--student-code", default="12345678", help="Eight-digit code to render, or 'random' to generate one.")
    generate_omr.add_argument("--full-name", default="ANA TORRES")
    generate_omr.add_argument("--exam-date", default="2026-06-12")
    generate_omr.add_argument("--signature", default="")
    generate_omr.add_argument("--blank-answers", action="store_true")
    generate_omr.add_argument("--seed", type=int)
    generate_omr.add_argument("--handwriting-source", choices=("opencv", "mnist"), default="opencv")
    generate_omr.add_argument("--mnist-root", default="data/external/mnist")

    export_digits = subparsers.add_parser("export-mnist-digits")
    export_digits.add_argument("--output-dir", default="data/digits")
    export_digits.add_argument("--samples-per-digit", type=int, default=5)
    export_digits.add_argument("--mnist-root", default="data/external/mnist")

    digit_strip = subparsers.add_parser("compose-digit-strip")
    digit_strip.add_argument("--digits-dir", default="data/digits")
    digit_strip.add_argument("--output", default="data/outputs/random_digit_strip.png")
    digit_strip.add_argument("--length", type=int, default=8)
    digit_strip.add_argument("--seed", type=int)

    paste_strip = subparsers.add_parser("paste-digit-strip")
    paste_strip.add_argument("--form-image", default="data/outputs/omr_sheet_001.png")
    paste_strip.add_argument("--digits-image", default="data/outputs/random_digit_strip.png")
    paste_strip.add_argument("--output", default="data/outputs/omr_sheet_with_digit_strip.png")
    paste_strip.add_argument("--x", type=int, default=95)
    paste_strip.add_argument("--y", type=int, default=270)
    paste_strip.add_argument("--width", type=int, default=335)
    paste_strip.add_argument("--height", type=int, default=72)

    args = parser.parse_args()
    if args.command == "generate-sample":
        template = TemplateLoader().load(args.layout)
        path = SyntheticFormFactory().create_sample(template, args.output, document_id=args.document_id)
        print(f"Generated sample: {path}")
        return
    if args.command == "generate-omr-sheet":
        options = tuple(option.strip() for option in args.options.split(",") if option.strip())
        image_path, layout_path = SyntheticOmrSheetFactory().create_sheet(
            image_path=args.image_output, layout_path=args.layout_output, document_id=args.document_id,
            questions=args.questions, options=options, handwriting_source=args.handwriting_source,
            mnist_root=args.mnist_root, student_code=args.student_code, full_name=args.full_name,
            exam_date=args.exam_date, signature=args.signature, fill_answers=not args.blank_answers,
            seed=args.seed,
        )
        print(f"Generated OMR sheet: {image_path}")
        print(f"Generated layout: {layout_path}")
        return
    if args.command == "export-mnist-digits":
        paths = MnistDigitExporter(args.mnist_root).export_digits(args.output_dir, args.samples_per_digit)
        print(f"Exported {len(paths)} digit images to {args.output_dir}")
        return
    if args.command == "compose-digit-strip":
        output, digits = DigitStripFactory().create_random_strip(args.digits_dir, args.output, args.length, args.seed)
        print(f"Composed digits: {digits}")
        print(f"Wrote digit strip: {output}")
        return

    output = FormOverlay().paste_image(
        form_path=args.form_image, overlay_path=args.digits_image, output_path=args.output,
        x=args.x, y=args.y, width=args.width, height=args.height,
    )
    print(f"Wrote form with pasted digit strip: {output}")


if __name__ == "__main__":
    main()
