from pathlib import Path

from formvision.extractors.icr import MnistDigitIcrEngine
from formvision.extractors.ocr import DoctrOcrEngine
from formvision.exporters.json_exporter import JsonExporter
from formvision.layout.template_loader import TemplateLoader
from formvision.pipeline.processor import FormProcessingPipeline


def main() -> None:
    demo_dir = Path("demo/omr_admission")
    image_dir = demo_dir / "images/scanned"
    layout_path = demo_dir / "template/layout.json"
    results_dir = Path("data/outputs/demo_batch")
    results_dir.mkdir(parents=True, exist_ok=True)

    template = TemplateLoader().load(layout_path)
    pipeline = FormProcessingPipeline(
        icr_extractor=MnistDigitIcrEngine(),
        ocr_extractor=DoctrOcrEngine(),
    )
    exporter = JsonExporter()

    for image_path in sorted(image_dir.glob("student_*.png")):
        result = pipeline.process(
            image_path,
            template,
            template_image_path=demo_dir / "template/template.png",
            align=True,
        )
        output_path = results_dir / f"{image_path.stem}_result.json"
        exporter.export(result, output_path)
        print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
