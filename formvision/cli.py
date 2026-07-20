"""Command-line interface for processing existing forms."""

import argparse
from pathlib import Path

import cv2

from formvision.exporters.csv_exporter import CsvExporter
from formvision.exporters.json_exporter import JsonExporter
from formvision.exporters.sqlite_exporter import SqliteExporter
from formvision.extractors.icr import MnistDigitIcrEngine
from formvision.extractors.ocr import DoctrOcrEngine
from formvision.layout.coordinate_mapper import CoordinateMapper
from formvision.layout.template_loader import TemplateLoader
from formvision.pipeline.processor import FormProcessingPipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="FormVision form processing CLI.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    process = subparsers.add_parser("process")
    process.add_argument("--image", required=True)
    process.add_argument("--layout", default="demo/omr_admission/template/layout.json")
    process.add_argument("--template-image")
    process.add_argument("--align", action="store_true")
    process.add_argument("--icr-engine", choices=("demo", "mnist"), default="demo")
    process.add_argument("--icr-model", default="formvision/models/mnist_digit_prototypes.npz")
    process.add_argument("--ocr-engine", choices=("demo", "doctr"), default="demo")
    process.add_argument("--doctr-det-arch", default="fast_tiny")
    process.add_argument("--doctr-reco-arch", default="crnn_mobilenet_v3_small")
    process.add_argument("--json-output", default="data/outputs/sample_001.json")
    process.add_argument("--csv-output")
    process.add_argument("--sqlite-output")

    inspect = subparsers.add_parser("inspect-layout")
    inspect.add_argument("--image", required=True)
    inspect.add_argument("--layout", default="demo/omr_admission/template/layout.json")
    inspect.add_argument("--output", default="data/outputs/layout_preview.png")

    args = parser.parse_args()
    template = TemplateLoader().load(args.layout)

    if args.command == "inspect-layout":
        image = cv2.imread(args.image, cv2.IMREAD_COLOR)
        if image is None:
            raise FileNotFoundError(args.image)
        preview = CoordinateMapper().draw_regions(
            image, template.fields, template.page_width, template.page_height
        )
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(output), preview)
        print(f"Wrote layout preview: {output}")
        return

    icr_extractor = None
    if args.icr_engine == "mnist":
        icr_extractor = MnistDigitIcrEngine(args.icr_model)

    ocr_extractor = None
    if args.ocr_engine == "doctr":
        ocr_extractor = DoctrOcrEngine(
            det_arch=args.doctr_det_arch,
            reco_arch=args.doctr_reco_arch,
            assume_straight_pages=True,
        )

    result = FormProcessingPipeline(
        icr_extractor=icr_extractor,
        ocr_extractor=ocr_extractor,
    ).process(
        args.image,
        template,
        template_image_path=args.template_image,
        align=args.align,
    )
    json_path = JsonExporter().export(result, args.json_output)
    print(f"Wrote JSON: {json_path}")
    if args.csv_output:
        print(f"Wrote CSV: {CsvExporter().export(result, args.csv_output)}")
    if args.sqlite_output:
        print(f"Wrote SQLite DB: {SqliteExporter().export(result, args.sqlite_output)}")


if __name__ == "__main__":
    main()
